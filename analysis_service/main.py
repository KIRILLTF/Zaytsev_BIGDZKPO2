import os, hashlib, io, datetime, re, json
from typing import List
from fastapi import FastAPI, HTTPException
import httpx
from sqlmodel import SQLModel, create_engine, Session, select
from .models import AnalysisResult
from .analyse import basic_stats
from shared.schemas import AnalysisResult as ResultSchema

STORING_URL = os.getenv("STORING_SERVICE_URL", "http://localhost:8081")
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=False, future=True)

app = FastAPI(title="File Analysis Service")

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

async def _fetch_file_content(file_id: str) -> str:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{STORING_URL}/files/{file_id}")
        r.raise_for_status()
        return r.json()["content"]

@app.post("/analyse/{file_id}")
async def analyse(file_id: str):
    with Session(engine) as session:
        cached = session.exec(select(AnalysisResult).where(AnalysisResult.file_id == file_id)).first()
        if cached:
            return cached

    content = await _fetch_file_content(file_id)
    paragraphs, words, chars = basic_stats(content)

    # Dummy duplicate check (hash equality)
    sha = hashlib.sha256(content.encode("utf-8")).hexdigest()
    with Session(engine) as session:
        hashes = [hashlib.sha256(
            (await _fetch_file_content(r.file_id)).encode("utf-8")).hexdigest()
            for r in session.exec(select(AnalysisResult)).all()]
        duplicate_of = None
        if sha in hashes:
            duplicate_of = file_id  # simplistic
        result = AnalysisResult(
            file_id=file_id,
            paragraphs=paragraphs,
            words=words,
            chars=chars,
            duplicate_of=duplicate_of
        )
        session.add(result)
        session.commit()
        session.refresh(result)
        return result

@app.get("/wordcloud/{location}")
async def wordcloud(location: str):
    # Просто перенаправляем в quickchart.io
    url = f"https://quickchart.io/wordcloud?text=https://{location}"
    return {"url": url}
