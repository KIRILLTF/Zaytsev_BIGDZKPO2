import os

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Analysis Service")

class StatsResult(BaseModel):
    paragraphs: int
    words: int
    characters: int

class CompareRequest(BaseModel):
    file_id1: str
    file_id2: str

class CompareResponse(BaseModel):
    identical: bool

STORING_URL = os.getenv("STORING_SERVICE_URL", "http://storing:8081")

client = httpx.AsyncClient()

@app.get("/stats/{file_id}", response_model=StatsResult)
async def stats(file_id: str):
    url = f"{STORING_URL}/download/{file_id}"
    resp = await client.get(url)
    if resp.status_code != 200:
        raise HTTPException(resp.status_code, f"File {file_id} not found")
    text = resp.text

    paragraphs = sum(1 for p in text.split("\n\n") if p.strip())
    words      = len(text.split())
    characters = len(text)

    return StatsResult(
        paragraphs=paragraphs,
        words=words,
        characters=characters
    )

@app.post("/compare", response_model=CompareResponse)
async def compare(req: CompareRequest):
    url1 = f"{STORING_URL}/download/{req.file_id1}"
    url2 = f"{STORING_URL}/download/{req.file_id2}"

    r1, r2 = await client.get(url1), await client.get(url2)

    if r1.status_code != 200:
        raise HTTPException(r1.status_code, f"File {req.file_id1} not found")
    if r2.status_code != 200:
        raise HTTPException(r2.status_code, f"File {req.file_id2} not found")

    identical = r1.content == r2.content
    return CompareResponse(identical=identical)
