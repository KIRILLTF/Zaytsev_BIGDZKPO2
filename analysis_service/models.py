from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class AnalysisResult(SQLModel, table=True):
    id: int = Field(primary_key=True)
    file_id: str = Field(index=True, unique=True)
    paragraphs: int
    words: int
    chars: int
    duplicate_of: Optional[str] = None
    wordcloud_location: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
