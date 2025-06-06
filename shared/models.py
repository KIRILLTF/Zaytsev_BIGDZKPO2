from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Report(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True, index=True)

    filename = Column(String, nullable=False)
