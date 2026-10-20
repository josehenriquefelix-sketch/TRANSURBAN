"""Banco SQLite local exclusivo deste pacote de apresentação."""
from pathlib import Path
import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

ARQUIVO = Path(os.environ.get('TRANSURBAN_DB', str(Path(__file__).resolve().parent / 'apresentacao.sqlite3')))
engine = create_engine('sqlite:///' + ARQUIVO.as_posix(), connect_args={'check_same_thread': False})

@event.listens_for(engine, 'connect')
def habilitar_fk(connection, _):
    connection.execute('PRAGMA foreign_keys=ON')

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()
