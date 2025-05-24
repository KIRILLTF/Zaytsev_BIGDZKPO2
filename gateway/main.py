import os
from fastapi import FastAPI, UploadFile, HTTPException
import httpx

STORING_URL = os.getenv("STORING_SERVICE_URL", "http://localhost:8081")
ANALYSIS_URL = os.getenv("ANALYSIS_SERVICE_URL", "http://localhost:8082")

app = FastAPI(title="API Gateway")

@app.post("/api/v1/files")
async def upload_file(file: UploadFile):
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{STORING_URL}/internal/store", files={"file": (file.filename, await file.read(), file.content_type)})
        r.raise_for_status()
        return r.json()

@app.get("/api/v1/files/{file_id}")
async def get_file(file_id: str):
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{STORING_URL}/files/{file_id}")
        r.raise_for_status()
        return r.json()

@app.post("/api/v1/files/{file_id}/analyse")
async def analyse_file(file_id: str):
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{ANALYSIS_URL}/analyse/{file_id}")
        r.raise_for_status()
        return r.json()

@app.get("/api/v1/wordcloud/{location}")
async def get_wordcloud(location: str):
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{ANALYSIS_URL}/wordcloud/{location}")
        r.raise_for_status()
        # Проксируем байты картинки
        return httpx.Response(
            status_code=r.status_code,
            content=r.content,
            headers={"Content-Type": "image/png"}
        )
