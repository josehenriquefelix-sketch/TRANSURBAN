from contextlib import contextmanager
from pathlib import Path
import os

from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ENV_PATH)


def database_configurada():
    return bool(os.getenv("DATABASE_URL", "").strip())


def _database_url():
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError(
            "DATABASE_URL não configurada. Copie backend/.env.example para "
            "backend/.env e informe a URL PostgreSQL exibida pelo Supabase."
        )
    return url


@contextmanager
def conexao():
    conn = psycopg2.connect(_database_url())
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def consultar_todos(sql, parametros=()):
    with conexao() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(sql, parametros)
            return [dict(linha) for linha in cursor.fetchall()]


def consultar_um(sql, parametros=()):
    with conexao() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(sql, parametros)
            linha = cursor.fetchone()
            return dict(linha) if linha else None


def executar_retorno(sql, parametros=()):
    with conexao() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(sql, parametros)
            linha = cursor.fetchone()
            return dict(linha) if linha else None
