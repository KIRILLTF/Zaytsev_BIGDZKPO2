import os
from fastapi import FastAPI
from sqlalchemy import create_engine
from shared.schemas import AnalysisResult   # ← теперь импорт найдётся

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@db:5432/zaytsev_kpo2",
)

engine = create_engine(DATABASE_URL, echo=False, future=True)

app = FastAPI()


@app.get("/ping", response_model=AnalysisResult)
def ping():
    return AnalysisResult(id=1, value=42.0)
