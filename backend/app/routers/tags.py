from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user
from app.database import get_db

router = APIRouter(prefix="/api/tags", tags=["tags"])


def _is_circular_reference(tag_id: int, parent_id: int, db: Session) -> bool:
    """
    Check if setting parent_id on tag_id would create a circular reference.
    Returns True if circular reference detected.
    """
    if tag_id == parent_id:
        return True
    
    current = db.query(models.Tag).filter(models.Tag.id == parent_id).first()
    while current:
        if current.id == tag_id:
            return True
        if current.parent_id is None:
            break
        current = db.query(models.Tag).filter(models.Tag.id == current.parent_id).first()
    
    return False


def _build_tag_hierarchy(tag: models.Tag) -> schemas.TagHierarchy:
    """Convert a tag and its children to TagHierarchy schema."""
    children = [_build_tag_hierarchy(child) for child in tag.children]
    return schemas.TagHierarchy(
        id=tag.id,
        name=tag.name,
        parent_id=tag.parent_id,
        children=children
    )


@router.get("/", response_model=List[schemas.TagRead])
def list_tags(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    """List all tags (flat structure)."""
    return db.query(models.Tag).order_by(models.Tag.name).all()


@router.get("/hierarchy", response_model=List[schemas.TagHierarchy])
def get_tags_hierarchy(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    """Get all top-level tags with their hierarchical structure (nested children)."""
    top_level_tags = db.query(models.Tag).filter(models.Tag.parent_id.is_(None)).order_by(models.Tag.name).all()
    return [_build_tag_hierarchy(tag) for tag in top_level_tags]


@router.post("/", response_model=schemas.TagRead, status_code=201)
def create_tag(
    tag_in: schemas.TagCreateWithParent,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """Create a new top-level tag or a child tag if parent_id is provided."""
    tag_name = tag_in.name.strip().lower()
    
    # Check if tag with same name and parent already exists
    existing = db.query(models.Tag).filter(
        models.Tag.name == tag_name,
        models.Tag.parent_id == tag_in.parent_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tag already exists")
    
    # If parent_id provided, validate that parent exists
    if tag_in.parent_id is not None:
        parent = db.query(models.Tag).filter(models.Tag.id == tag_in.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent tag not found")
    
    tag = models.Tag(name=tag_name, parent_id=tag_in.parent_id)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


@router.post("/{parent_id}/children", response_model=schemas.TagRead, status_code=201)
def create_child_tag(
    parent_id: int,
    tag_in: schemas.TagCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """Create a child tag under a specific parent tag."""
    parent = db.query(models.Tag).filter(models.Tag.id == parent_id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent tag not found")
    
    tag_name = tag_in.name.strip().lower()
    
    # Check if tag with same name under this parent already exists
    existing = db.query(models.Tag).filter(
        models.Tag.name == tag_name,
        models.Tag.parent_id == parent_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Child tag already exists under this parent")
    
    tag = models.Tag(name=tag_name, parent_id=parent_id)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


@router.patch("/{tag_id}/parent", response_model=schemas.TagRead)
def update_tag_parent(
    tag_id: int,
    parent_update: schemas.TagCreateWithParent,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """Move a tag to a different parent (or make it a top-level tag if parent_id is None)."""
    tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    new_parent_id = parent_update.parent_id
    
    # Validate parent exists if provided
    if new_parent_id is not None:
        parent = db.query(models.Tag).filter(models.Tag.id == new_parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent tag not found")
        
        # Check for circular reference
        if _is_circular_reference(tag_id, new_parent_id, db):
            raise HTTPException(status_code=400, detail="Cannot set parent: circular reference detected")
    
    tag.parent_id = new_parent_id
    db.commit()
    db.refresh(tag)
    return tag


@router.delete("/{tag_id}", status_code=204)
def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """Delete a tag. Child tags will become top-level tags (orphaned)."""
    tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    # Orphan all children (set their parent_id to None)
    db.query(models.Tag).filter(models.Tag.parent_id == tag_id).update(
        {models.Tag.parent_id: None}
    )
    
    db.delete(tag)
    db.commit()
