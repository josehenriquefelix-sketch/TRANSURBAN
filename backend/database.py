from pathlib import Path
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv(Path(__file__).with_name(".env"))


class Base(DeclarativeBase):
    pass


_engine = None


def get_engine():
    global _engine
    if _engine is None:
        database_url = os.getenv("DATABASE_URL", "").strip()
        if not database_url:
            raise RuntimeError(
                "DATABASE_URL não configurada. Copie backend/.env.example para "
                "backend/.env e informe a conexão PostgreSQL do Supabase."
            )
        _engine = create_engine(database_url, pool_pre_ping=True)
    return _engine


def get_db():
    SessionLocal = sessionmaker(
        bind=get_engine(),
        autoflush=False,
        autocommit=False,
    )
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
