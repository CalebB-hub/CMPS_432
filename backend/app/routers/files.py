import logging
import os
import uuid
from typing import Dict, List, Optional, Set, Union
import io
import json

import aiofiles
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user
from app.config import settings
from app.database import get_db
from app.s3_service import s3_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/files", tags=["files"])


def _normalize_tag_name(name: str) -> str:
    return name.strip().lower()


def _find_tag_by_name(
    db: Session,
    name: str,
    parent_name: Optional[str] = None,
) -> Optional[models.Tag]:
    normalized_name = _normalize_tag_name(name)
    query = db.query(models.Tag).filter(models.Tag.name == normalized_name)
    candidates = query.all()
    if not candidates:
        return None

    if parent_name is None:
        return candidates[0]

    normalized_parent_name = _normalize_tag_name(parent_name)
    for candidate in candidates:
        if candidate.parent_id is None:
            continue
        parent = db.query(models.Tag).filter(models.Tag.id == candidate.parent_id).first()
        if parent and parent.name == normalized_parent_name:
            return candidate

    return candidates[0]


def _get_or_create_tag(
    db: Session,
    name: str,
    parent_name: Optional[str] = None,
) -> models.Tag:
    tag = _find_tag_by_name(db, name, parent_name=parent_name)
    if tag:
        return tag

    parent_id = None
    if parent_name:
        parent_tag = _find_tag_by_name(db, parent_name)
        if parent_tag:
            parent_id = parent_tag.id

    tag = models.Tag(name=_normalize_tag_name(name), parent_id=parent_id)
    db.add(tag)
    db.flush()
    return tag


def _get_ancestor_tags(db: Session, tag: models.Tag) -> List[models.Tag]:
    ancestors: List[models.Tag] = []
    seen: Set[int] = set()
    current = tag
    while current.parent_id is not None and current.parent_id not in seen:
        seen.add(current.parent_id)
        parent = db.query(models.Tag).filter(models.Tag.id == current.parent_id).first()
        if parent is None:
            break
        ancestors.append(parent)
        current = parent
    return ancestors


def _build_expanded_tags(
    db: Session,
    tag_names: List[str],
    tag_parents: Optional[Dict[str, Optional[str]]] = None,
) -> List[models.Tag]:
    normalized_names = [_normalize_tag_name(name) for name in tag_names if name and name.strip()]
    if not normalized_names:
        return []

    parent_hints: Dict[str, Optional[str]] = {}
    if tag_parents:
        for child_name, parent_name in tag_parents.items():
            normalized_child = _normalize_tag_name(child_name)
            parent_hints[normalized_child] = _normalize_tag_name(parent_name) if parent_name else None

    by_id: Dict[int, models.Tag] = {}
    for name in normalized_names:
        tag = _get_or_create_tag(db, name, parent_name=parent_hints.get(name))
        by_id[tag.id] = tag
        for ancestor in _get_ancestor_tags(db, tag):
            by_id[ancestor.id] = ancestor

    return list(by_id.values())


def _parse_tag_parents_form_value(raw: Optional[str]) -> Dict[str, Optional[str]]:
    if not raw:
        return {}
    try:
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            return {}
        return {
            str(k): (str(v) if v is not None else None)
            for k, v in payload.items()
        }
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid tag_parents payload")


def _extract_tag_update_payload(
    tag_payload: Union[List[str], schemas.FileTagUpdate],
) -> tuple[List[str], Dict[str, Optional[str]]]:
    if isinstance(tag_payload, list):
        return tag_payload, {}
    return tag_payload.tags, tag_payload.tag_parents


def _parse_csv_tags(raw_tags: Optional[str]) -> List[str]:
    if not raw_tags:
        return []
    return [tag for tag in raw_tags.split(",") if tag.strip()]


def _assign_expanded_tags(
    db: Session,
    db_file: models.File,
    tag_names: List[str],
    tag_parents: Optional[Dict[str, Optional[str]]] = None,
) -> None:
    db_file.tags = _build_expanded_tags(db, tag_names, tag_parents=tag_parents)


def _file_to_response(db_file: models.File) -> schemas.FileRead:
    """
    Convert a File model to FileRead schema, including download_url if using S3.
    """
    # Use model_validate to convert ORM model to Pydantic model
    file_read = schemas.FileRead.model_validate(db_file)
    
    # Add download_url if S3 is enabled
    if s3_service.enabled:
        try:
            file_read.download_url = s3_service.get_download_url(db_file.storage_path)
        except Exception as e:
            logger.warning(f"Failed to generate presigned URL for file {db_file.id}: {e}")
    
    return file_read


@router.get("/", response_model=List[schemas.FileRead])
def list_files(
    tags: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """List files for the current user, optionally filtered by comma-separated tags."""
    query = db.query(models.File).filter(models.File.owner_id == current_user.id)
    if tags:
        tag_names = [t.strip().lower() for t in tags.split(",") if t.strip()]
        for tag_name in tag_names:
            query = query.filter(
                models.File.tags.any(models.Tag.name == tag_name)
            )
    files = query.all()
    return [_file_to_response(f) for f in files]


@router.post("/", response_model=schemas.FileRead, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    tags: Optional[str] = Form(None),
    tag_parents: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Upload a file and optionally attach comma-separated tags.
    
    Uses S3 for storage if AWS credentials are configured, otherwise stores locally.
    """
    content = await file.read()
    content_type = file.content_type or "application/octet-stream"
    unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
    
    # Determine storage path
    if s3_service.enabled:
        # S3 storage: use S3 key as storage_path
        s3_key = f"users/{current_user.id}/{unique_filename}"
        try:
            s3_service.upload_file(s3_key, content, content_type)
            storage_path = s3_key
            logger.info(f"File uploaded to S3: {s3_key}")
        except Exception as e:
            logger.error(f"S3 upload failed: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to upload file: {e}")
    else:
        # Local storage: use local filesystem
        os.makedirs(settings.upload_dir, exist_ok=True)
        dest_path = os.path.join(settings.upload_dir, unique_filename)
        async with aiofiles.open(dest_path, "wb") as out_file:
            await out_file.write(content)
        storage_path = dest_path
        logger.info(f"File uploaded locally: {dest_path}")

    db_file = models.File(
        filename=unique_filename,
        original_filename=file.filename,
        content_type=content_type,
        size=len(content),
        storage_path=storage_path,
        owner_id=current_user.id,
    )
    db.add(db_file)

    parsed_tags = _parse_csv_tags(tags)
    parsed_tag_parents = _parse_tag_parents_form_value(tag_parents)
    if parsed_tags:
        _assign_expanded_tags(db, db_file, parsed_tags, tag_parents=parsed_tag_parents)
    
    db.commit()
    db.refresh(db_file)
    return _file_to_response(db_file)


@router.get("/{file_id}/download")
async def download_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Download a file."""
    db_file = db.query(models.File).filter(
        models.File.id == file_id, models.File.owner_id == current_user.id
    ).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    try:
        if s3_service.enabled:
            # For S3, download the file content and return as blob
            file_content = s3_service.download_file(db_file.storage_path)
            return StreamingResponse(
                io.BytesIO(file_content),
                media_type=db_file.content_type,
                headers={
                    "Content-Disposition": f'attachment; filename="{db_file.original_filename}"'
                },
            )
        else:
            # For local storage, return the file directly
            if not os.path.exists(db_file.storage_path):
                raise HTTPException(status_code=404, detail="File not found on disk")
            
            return FileResponse(
                path=db_file.storage_path,
                media_type=db_file.content_type,
                filename=db_file.original_filename,
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download failed for file {file_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@router.get("/{file_id}", response_model=schemas.FileRead)
def get_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Get a specific file with presigned download URL if using S3."""
    db_file = db.query(models.File).filter(
        models.File.id == file_id, models.File.owner_id == current_user.id
    ).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    return _file_to_response(db_file)


@router.patch("/{file_id}/tags", response_model=schemas.FileRead)
def update_file_tags(
    file_id: int,
    tag_payload: Union[List[str], schemas.FileTagUpdate],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Replace the tags on a file."""
    db_file = db.query(models.File).filter(
        models.File.id == file_id, models.File.owner_id == current_user.id
    ).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    tag_names, tag_parents = _extract_tag_update_payload(tag_payload)
    _assign_expanded_tags(db, db_file, tag_names, tag_parents=tag_parents)
    db.commit()
    db.refresh(db_file)
    return _file_to_response(db_file)


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Delete a file from storage and database."""
    db_file = db.query(models.File).filter(
        models.File.id == file_id, models.File.owner_id == current_user.id
    ).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    # Delete from storage
    if s3_service.enabled:
        try:
            s3_service.delete_file(db_file.storage_path)
            logger.info(f"File deleted from S3: {db_file.storage_path}")
        except Exception as e:
            logger.error(f"Failed to delete file from S3: {e}")
            # Continue with DB deletion even if S3 delete fails
    else:
        if os.path.exists(db_file.storage_path):
            try:
                os.remove(db_file.storage_path)
                logger.info(f"File deleted locally: {db_file.storage_path}")
            except Exception as e:
                logger.error(f"Failed to delete local file: {e}")
                # Continue with DB deletion even if file deletion fails

    db.delete(db_file)
    db.commit()
