"""Configuração privada de conexão, engine e fábrica de sessões."""
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / 'data' / 'transurban.db'
load_dotenv(ROOT / '.env', override=False)
modo = os.environ.get('TRANSURBAN_MODO', 'auto')
url = 'sqlite:///' + DB_PATH.as_posix() if modo == 'local' else os.environ.get('DATABASE_URL', 'sqlite:///' + DB_PATH.as_posix())
if modo == 'supabase' and not url.startswith(('postgresql:', 'postgresql+', 'postgres:')):
    raise RuntimeError('Configure DATABASE_URL no .env local para usar Supabase.')
if url.startswith('postgres://'):
    url = url.replace('postgres://', 'postgresql://', 1)
engine = create_engine(url, connect_args={'check_same_thread': False} if url.startswith('sqlite:') else {'sslmode': 'require', 'connect_timeout': 12}, pool_pre_ping=True)
if engine.dialect.name == 'sqlite':
    @event.listens_for(engine, 'connect')
    def foreign_keys(connection, _):
        connection.execute('PRAGMA foreign_keys=ON')
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

