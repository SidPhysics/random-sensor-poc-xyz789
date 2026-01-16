# shared/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Use environment variable for flexibility (local SQLite default, can override for Postgres/RDS)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./metrics.db"  # default for local + pytest
)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency to get DB session for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()