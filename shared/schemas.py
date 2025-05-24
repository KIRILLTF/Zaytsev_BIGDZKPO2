from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FileMeta(BaseModel):
    id: str
    name: str
    hash: str
    location: str
    created_at: datetime

class AnalysisResult(BaseModel):
    file_id: str
    paragraphs: int
    words: int
    chars: int
    duplicate_of: Optional[str] = None
    wordcloud_location: Optional[str] = None
    created_at: datetime
