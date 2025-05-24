from sqlmodel import SQLModel, Field
from datetime import datetime

class FileMeta(SQLModel, table=True):
    id: str = Field(primary_key=True, index=True)
    name: str
    hash: str = Field(index=True)
    location: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
