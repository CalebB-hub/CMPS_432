from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user
from app.database import get_db

router = APIRouter(prefix="/api/tags", tags=["tags"])


@router.get("/", response_model=List[schemas.TagRead])
def list_tags(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    return db.query(models.Tag).order_by(models.Tag.name).all()


@router.post("/", response_model=schemas.TagRead, status_code=201)
def create_tag(
    tag_in: schemas.TagCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    existing = db.query(models.Tag).filter(models.Tag.name == tag_in.name.strip().lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tag already exists")
    tag = models.Tag(name=tag_in.name.strip().lower())
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


@router.delete("/{tag_id}", status_code=204)
def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    db.delete(tag)
    db.commit()
