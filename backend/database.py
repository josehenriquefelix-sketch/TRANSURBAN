from pathlib import Path
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
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
            raise RuntimeError("DATABASE_URL não configurada. Copie .env.example para .env na pasta backend.")
        url = make_url(database_url)
        if url.get_backend_name() != "postgresql":
            raise RuntimeError("Esta avaliação exige PostgreSQL. Confira DATABASE_URL.")
        url = url.set(drivername="postgresql+psycopg2")
        _engine = create_engine(url, pool_pre_ping=True, hide_parameters=True)
    return _engine

def get_db():
    SessionLocal = sessionmaker(bind=get_engine(), autoflush=False, autocommit=False)
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
