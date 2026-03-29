import os
import uuid
from typing import List, Optional

import aiofiles
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user
from app.config import settings
from app.database import get_db

router = APIRouter(prefix="/api/files", tags=["files"])


def _get_or_create_tag(db: Session, name: str) -> models.Tag:
    tag = db.query(models.Tag).filter(models.Tag.name == name.strip().lower()).first()
    if not tag:
        tag = models.Tag(name=name.strip().lower())
        db.add(tag)
        db.flush()
    return tag


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
    return query.all()


@router.post("/", response_model=schemas.FileRead, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    tags: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Upload a file and optionally attach comma-separated tags."""
    os.makedirs(settings.upload_dir, exist_ok=True)
    unique_name = f"{uuid.uuid4().hex}_{file.filename}"
    dest_path = os.path.join(settings.upload_dir, unique_name)

    async with aiofiles.open(dest_path, "wb") as out_file:
        content = await file.read()
        await out_file.write(content)

    db_file = models.File(
        filename=unique_name,
        original_filename=file.filename,
        content_type=file.content_type or "application/octet-stream",
        size=len(content),
        storage_path=dest_path,
        owner_id=current_user.id,
    )
    db.add(db_file)

    if tags:
        for tag_name in tags.split(","):
            if tag_name.strip():
                db_file.tags.append(_get_or_create_tag(db, tag_name))
    db.commit()
    db.refresh(db_file)
    return db_file


@router.get("/{file_id}", response_model=schemas.FileRead)
def get_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_file = db.query(models.File).filter(
        models.File.id == file_id, models.File.owner_id == current_user.id
    ).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    return db_file


@router.patch("/{file_id}/tags", response_model=schemas.FileRead)
def update_file_tags(
    file_id: int,
    tag_names: List[str],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Replace the tags on a file."""
    db_file = db.query(models.File).filter(
        models.File.id == file_id, models.File.owner_id == current_user.id
    ).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    db_file.tags = [_get_or_create_tag(db, name) for name in tag_names if name.strip()]
    db.commit()
    db.refresh(db_file)
    return db_file


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_file = db.query(models.File).filter(
        models.File.id == file_id, models.File.owner_id == current_user.id
    ).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    if os.path.exists(db_file.storage_path):
        os.remove(db_file.storage_path)

    db.delete(db_file)
    db.commit()
