from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import auth, files, tags

# Create all database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Cloud Storage API",
    description="Cloud file storage with tag-based filtering — CMPS 432",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(files.router)
app.include_router(tags.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
