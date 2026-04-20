from fastapi import FastAPI, status, HTTPException, UploadFile, File, Form, Depends
from pydantic import BaseModel
import uuid
import os
from .db import PocketDB, Item as DBItem
from .s3_service import S3Service

db = PocketDB('db.sqlite3')
s3_service = S3Service()
app = FastAPI()

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
        return {"user_exists":False, "user_key":"Still need to implement this key thing"}

# Upload file to S3
@app.post('/files/upload', response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    user_key: str = Form(...),
):
    try:
        content = await file.read()
        
        s3_key = f"{user_key}/{uuid.uuid4().hex}_{file.filename}"
        
        # Upload to S3
        await s3_service.upload_file(
            file_key=s3_key,
            file_content=content,
            content_type=file.content_type or "application/octet-stream"
        )
        
        item_data = {
            "name": file.filename,
            "path": s3_key,
            "s3_key": s3_key,
            "user_id": 1 # Placeholder
        }
        
        # Generate download URL
        download_url = s3_service.get_download_url(s3_key)
        
        return FileUploadResponse(
            id=1,  # Placeholder
            name=file.filename,
            s3_key=s3_key,
            download_url=download_url,
            size=len(content)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# Get download URL
@app.get('/files/{file_id}/download', response_model=FileDownloadResponse)
async def download_file(file_id: int, user_key: str):
    try:
        # Retrieve file metadata from database
        # db_file = db.get_item(file_id, user_key)
        # if not db_file:
        #     raise HTTPException(status_code=404, detail="File not found")
        
        s3_key = f"{user_key}/file_{file_id}"
        
        download_url = s3_service.get_download_url(s3_key, expiration=3600)
        
        return FileDownloadResponse(
            name="filename.ext",  # From DB
            download_url=download_url
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

# Delete file from S3
@app.delete('/files/{file_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(file_id: int, user_key: str):
    try:
        # Retrieve s3_key from database
        # db_file = db.get_item(file_id, user_key)
        # if not db_file:
        #     raise HTTPException(status_code=404, detail="File not found")
        
        s3_key = f"{user_key}/file_{file_id}"  # Placeholder
        
        # Delete from S3
        await s3_service.delete_file(s3_key)
        
        # Delete from database
        # db.delete_item(file_id)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

