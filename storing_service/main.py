import os, hashlib, io
from uuid import uuid4
from fastapi import FastAPI, UploadFile, HTTPException
from minio import Minio
from sqlmodel import SQLModel, create_engine, Session, select
from models import FileMeta

# ─────────────────────────────  конфиг  ──────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://user:pass@db:5432/files")
engine = create_engine(DATABASE_URL, echo=False, future=True)

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS   = os.getenv("MINIO_ACCESS_KEY", "minio")
MINIO_SECRET   = os.getenv("MINIO_SECRET_KEY", "minio123")
BUCKET_NAME    = os.getenv("MINIO_BUCKET", "reports")

minio_client = Minio(
    MINIO_ENDPOINT, access_key=MINIO_ACCESS, secret_key=MINIO_SECRET, secure=False
)

app = FastAPI(title="File Storing Service")

# ─────────────────────────────  старт  ───────────────────────────────
@app.on_event("startup")
def init_db():
    SQLModel.metadata.create_all(engine)
    if not minio_client.bucket_exists(BUCKET_NAME):
        minio_client.make_bucket(BUCKET_NAME)

# ─────────────────────────────  API  ─────────────────────────────────
@app.post("/internal/store", response_model=FileMeta)
async def store_file(file: UploadFile):
    content = await file.read()
    sha = hashlib.sha256(content).hexdigest()

    with Session(engine) as session:
        if (meta := session.exec(select(FileMeta).where(FileMeta.hash == sha)).first()):
            return meta

        file_id = str(uuid4())
        object_name = f"{file_id}.txt"
        minio_client.put_object(
            BUCKET_NAME, object_name, io.BytesIO(content),
            length=len(content), content_type="text/plain"
        )

        meta = FileMeta(id=file_id, name=file.filename, hash=sha, location=object_name)
        session.add(meta)
        session.commit()
        session.refresh(meta)
        return meta

@app.get("/files/{file_id}")
def get_file(file_id: str):
    with Session(engine) as session:
        meta = session.get(FileMeta, file_id)
        if not meta:
            raise HTTPException(status_code=404, detail="File not found")

    resp = minio_client.get_object(BUCKET_NAME, meta.location)
    return {"filename": meta.name, "content": resp.read().decode()}
