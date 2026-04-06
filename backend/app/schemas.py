import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr


# ── Tag schemas ──────────────────────────────────────────────────────────────

class TagBase(BaseModel):
    name: str


class TagCreate(TagBase):
    pass


class TagRead(TagBase):
    id: int

    model_config = {"from_attributes": True}


# ── File schemas ─────────────────────────────────────────────────────────────

class FileBase(BaseModel):
    original_filename: str
    content_type: str


class FileCreate(FileBase):
    pass


class FileRead(FileBase):
    id: int
    filename: str
    size: int
    uploaded_at: datetime.datetime
    owner_id: int
    tags: List[TagRead] = []

    model_config = {"from_attributes": True}


# ── User schemas ─────────────────────────────────────────────────────────────

class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    created_at: datetime.datetime
    files: List[FileRead] = []

    model_config = {"from_attributes": True}


# ── Auth schemas ─────────────────────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# ── Feedback schemas ─────────────────────────────────────────────────────────

class FeedbackCreate(BaseModel):
    text: str


class FeedbackRead(FeedbackCreate):
    id: int
    user_id: Optional[int] = None
    created_at: datetime.datetime

    model_config = {"from_attributes": True}
