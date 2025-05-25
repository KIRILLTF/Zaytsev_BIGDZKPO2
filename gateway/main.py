import io
import os
from typing import Final

import httpx
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import StreamingResponse

# --- динамически собираем URL-ы из переменных окружения ----------------------

def build_url(prefix: str, default_host: str, default_port: int) -> str:
    host = os.getenv(f"{prefix}_HOST", default_host)
    port = int(os.getenv(f"{prefix}_PORT", default_port))
    return os.getenv(f"{prefix}_URL", f"http://{host}:{port}")

STORING_URL:  Final[str] = build_url("STORING_SERVICE", "storing-service", 8081)
ANALYSIS_URL: Final[str] = build_url("ANALYSIS_SERVICE", "analysis-service", 8082)

# ---------------------------------------------------------------------------

app = FastAPI(title="API Gateway")


async def _proxy(method: str, url: str, **kwargs) -> httpx.Response:
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.request(method, url, timeout=30, **kwargs)
            resp.raise_for_status()
            return resp
        except httpx.HTTPStatusError as exc:          # ответ с 4xx/5xx от сервиса
            raise HTTPException(
                status_code=exc.response.status_code, detail=exc.response.text
            )
        except httpx.RequestError as exc:             # не смогли соединиться
            raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/api/v1/files")
async def upload_file(file: UploadFile):
    resp = await _proxy(
        "POST",
        f"{STORING_URL}/upload",
        files={"file": (file.filename, await file.read(), file.content_type)},
    )
    return resp.json()


@app.get(
    "/api/v1/files/{file_id}",
    response_class=StreamingResponse,
    responses={200: {"content": {"application/octet-stream": {}}}},
)
async def get_file(file_id: str):
    resp = await _proxy("GET", f"{STORING_URL}/download/{file_id}")
    return StreamingResponse(
        io.BytesIO(resp.content), media_type="application/octet-stream"
    )


@app.get("/api/v1/files/{file_id}/analyse")
async def analyse_file(file_id: str):
    resp = await _proxy("GET", f"{ANALYSIS_URL}/stats/{file_id}")
    return resp.json()
