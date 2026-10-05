"""Configuração, engine e sessão por requisição; não altera o Supabase."""
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase, sessionmaker

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / '.env')
DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{ROOT / "transurban_local.db"}')
url = make_url(DATABASE_URL)
IS_LOCAL = url.get_backend_name() == 'sqlite'
if url.get_backend_name() not in ('sqlite', 'postgresql'):
    raise RuntimeError('Use SQLite para demonstração ou PostgreSQL para Supabase.')
connect_args = {'check_same_thread': False} if IS_LOCAL else {'connect_timeout': 10}
if not IS_LOCAL:
    connect_args['sslmode'] = os.getenv('PGSSLMODE', 'require')
engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=connect_args)
if IS_LOCAL:
    @event.listens_for(engine, 'connect')
    def sqlite_foreign_keys(connection, _record):
        connection.execute('PRAGMA foreign_keys=ON')

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

def get_db():
    with SessionLocal() as session:
        yield session
