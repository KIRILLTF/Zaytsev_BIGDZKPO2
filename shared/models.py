# shared/models.py
from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Report(Base):
    __tablename__ = "reports"

    # UUID-идентификатор файла
    id = Column(String, primary_key=True, index=True)
    # Оригинальное имя загруженного файла
    filename = Column(String, nullable=False)
