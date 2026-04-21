from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel
from .db import PocketDB

class Item(BaseModel):
    name: str
    path: str
    user_key: str
    tags: list[str]
    id: int | None
class User(BaseModel):
    name: str
    password: str

db = PocketDB('db.sqlite3')
app = FastAPI()

@app.get('/')
async def root():
    return {"message": "Hello World"}

@app.post('/items/')
async def addItem(item: Item):
    return item

@app.put('/items/')
async def updateItem(item: Item):
    return item

@app.put('/items/')
async def deleteItem(item: Item):
    return item

@app.post('/users/')
async def addUser(user: User):
    user_exists = db.user_exists(name=user.name)

    if user_exists:
        return {"user_exists":True, "user_key":""}
    else:
        return {"user_exists":False, "user_key":"Still need to implement this key thing"}
