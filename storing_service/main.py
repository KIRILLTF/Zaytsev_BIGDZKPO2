import os
import io
import sys
import time
import logging
from uuid import uuid4

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from minio import Minio, S3Error

from shared.models import Base, Report

logger = logging.getLogger("uvicorn.error")
app = FastAPI(title="Storing Service")


@app.on_event("startup")
async def startup_event():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL не задан")
        sys.exit(1)

    engine = None
    for attempt in range(1, 11):
        try:
            engine = create_engine(database_url)
            conn = engine.connect()
            conn.close()
            logger.info(f"PostgreSQL доступен (попытка {attempt})")
            break
        except OperationalError as e:
            logger.warning(f"Не удалось подключиться к БД (попытка {attempt}): {e}")
            time.sleep(2)
    else:
        logger.error("Не удалось установить соединение с БД после 10 попыток")
        sys.exit(1)

    Base.metadata.create_all(bind=engine)
    app.state.db_session = sessionmaker(bind=engine)

    minio_url = os.getenv("MINIO_URL")
    access = os.getenv("MINIO_ACCESS_KEY")
    secret = os.getenv("MINIO_SECRET_KEY")
    if not (minio_url and access and secret):
        logger.error("Параметры MinIO не заданы")
        sys.exit(1)

    host = minio_url.replace("http://", "").replace("https://", "")
    client = None
    for attempt in range(1, 11):
        try:
            client = Minio(host, access_key=access, secret_key=secret, secure=False)
            bucket = "reports"
            if not client.bucket_exists(bucket):
                client.make_bucket(bucket)
            logger.info(f"MinIO доступен (попытка {attempt})")
            break
        except Exception as e:
            logger.warning(f"Не удалось подключиться к MinIO (попытка {attempt}): {e}")
            time.sleep(2)
    else:
        logger.error("Не удалось установить соединение с MinIO после 10 попыток")
        sys.exit(1)

    app.state.minio = client


@app.post("/upload")
async def upload_report(file: UploadFile = File(...)):
    if file.content_type != "text/plain":
        raise HTTPException(415, "Поддерживаются только текстовые файлы (.txt)")

    data = await file.read()
    file_id = str(uuid4())

    try:
        app.state.minio.put_object(
            "reports",
            file_id,
            io.BytesIO(data),
            length=len(data),
            content_type="text/plain"
        )
    except S3Error:
        logger.exception("Ошибка при загрузке в MinIO")
        raise HTTPException(500, "Ошибка хранения файла")

    session = app.state.db_session()
    try:
        report = Report(id=file_id, filename=file.filename)
        session.add(report)
        session.commit()
    except SQLAlchemyError:
        session.rollback()
        logger.exception("Ошибка при записи в БД")
        raise HTTPException(500, "Ошибка записи метаданных")
    finally:
        session.close()

    return {"file_id": file_id}


@app.get("/download/{file_id}")
async def download_report(file_id: str):
    try:
        data = app.state.minio.get_object("reports", file_id)
        return StreamingResponse(data, media_type="text/plain")
    except Exception:
        logger.exception("Ошибка при чтении файла из MinIO")
        raise HTTPException(404, "Файл не найден")
