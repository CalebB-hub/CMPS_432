from fastapi import FastAPI, status, HTTPException, UploadFile, File, Form, Depends
from pydantic import BaseModel
import uuid
import os
import logging
from .db import PocketDB, Item as DBItem
from .s3_service import S3Service

logger = logging.getLogger(__name__)

db = PocketDB('db.sqlite3')
s3_service = S3Service()
app = FastAPI(title="Cloud Storage API")

class Item(BaseModel):
    name: str
    path: str
    user_key: str
    tags: list[str]
    id: int | None

class User(BaseModel):
    name: str
    password: str

class FileUploadResponse(BaseModel):
    id: int
    name: str
    s3_key: str
    download_url: str
    size: int

class FileDownloadResponse(BaseModel):
    name: str
    download_url: str

class FileListResponse(BaseModel):
    id: int
    name: str
    s3_key: str

@app.get('/')
async def root():
    return {"message": "Hello World"}

@app.post('/items/')
async def addItem(item: Item):
    return item

@app.post('/users/')
async def addUser(user: User):
    user_exists = db.user_exists(name=user.name)

    if user_exists:
        return {"user_exists":True, "user_key":""}
    else:
        db.add_user(user.name, user.password)
        return {"user_exists":False, "user_key":"User created successfully"}

# Upload file to S3
@app.post('/files/upload', response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    user_name: str = Form(...),
    user_password: str = Form(...),
):
    """Upload a file to S3 storage."""
    try:
        # Authenticate user
        is_valid, user_id = db.verify_user_password(user_name, user_password)
        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Read file content
        content = await file.read()
        
        # Generate unique S3 key
        s3_key = f"user_{user_id}/{uuid.uuid4().hex}_{file.filename}"
        
        # Upload to S3
        await s3_service.upload_file(
            file_key=s3_key,
            file_content=content,
            content_type=file.content_type or "application/octet-stream"
        )
        
        # Store metadata in database
        item_id = db.add_item_with_s3(
            user_id=user_id,
            name=file.filename,
            s3_key=s3_key,
        )
        
        # Generate presigned download URL
        download_url = s3_service.get_download_url(s3_key)
        
        logger.info(f"File {file.filename} uploaded by user {user_id}")
        
        return FileUploadResponse(
            id=item_id,
            name=file.filename,
            s3_key=s3_key,
            download_url=download_url,
            size=len(content)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# List files for user
@app.get('/files', response_model=list[FileListResponse])
async def list_files(
    user_name: str,
    user_password: str,
):
    """List all files for the current user."""
    try:
        # Authenticate user
        is_valid, user_id = db.verify_user_password(user_name, user_password)
        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Get files for user
        files = db.get_items_by_user(user_id)
        
        return [
            FileListResponse(
                id=f.id,
                name=f.name,
                s3_key=f.s3_key,
            )
            for f in files
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List files failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"List files failed: {str(e)}")

# Get download URL
@app.get('/files/{file_id}/download', response_model=FileDownloadResponse)
async def download_file(
    file_id: int,
    user_name: str,
    user_password: str,
):
    """Get a presigned download URL for a file."""
    try:
        # Authenticate user
        is_valid, user_id = db.verify_user_password(user_name, user_password)
        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Get file from database
        db_file = db.get_item_by_id(file_id, user_id)
        if not db_file:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Generate presigned URL
        download_url = s3_service.get_download_url(db_file.s3_key, expiration=3600)
        
        logger.info(f"Download URL generated for file {file_id} by user {user_id}")
        
        return FileDownloadResponse(
            name=db_file.name,
            download_url=download_url
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

# Delete file from S3
@app.delete('/files/{file_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: int,
    user_name: str,
    user_password: str,
):
    """Delete a file from S3 storage."""
    try:
        # Authenticate user
        is_valid, user_id = db.verify_user_password(user_name, user_password)
        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Get file from database
        db_file = db.get_item_by_id(file_id, user_id)
        if not db_file:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Delete from S3
        await s3_service.delete_file(db_file.s3_key)
        
        # Delete from database
        db.delete_item_by_id(file_id, user_id)
        
        logger.info(f"File {file_id} deleted by user {user_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

