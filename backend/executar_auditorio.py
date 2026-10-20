"""API para ensaios em schema local persistente, sem alterar .env ou Supabase."""
from argparse import ArgumentParser
import os
import re
import socket

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

import database
import models  # registra as tabelas no metadata

SCHEMA = "transurban_auditorio"


def local_url(raw):
    try:
        url = make_url(raw)
    except Exception:
        raise ValueError("TEST_DATABASE_URL inválida. Confira o .env privadamente.") from None
    if url.get_backend_name() != "postgresql" or url.host not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("O modo auditório exige TEST_DATABASE_URL em PostgreSQL local. Supabase é recusado.")
    return url.set(drivername="postgresql+psycopg2")


def preparar_banco(schema=SCHEMA, criar_cidades=True):
    if not re.fullmatch(r"transurban_auditorio(?:_[a-z0-9_]{1,35})?", schema):
        raise ValueError("Use um schema de ensaio com prefixo transurban_auditorio e letras minúsculas, números ou sublinhado.")
    url = local_url(os.getenv("TEST_DATABASE_URL", ""))
    admin = create_engine(url, hide_parameters=True, connect_args={"connect_timeout": 5})
    try:
        with admin.begin() as connection:
            connection.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))
    finally:
        admin.dispose()
    query = dict(url.query)
    query["options"] = f"-csearch_path={schema}"
    isolated = url.set(query=query)
    engine = create_engine(isolated, hide_parameters=True)
    try:
        with engine.begin() as connection:
            database.Base.metadata.create_all(connection)
            for nome in (("Maringá", "Sarandi") if criar_cidades else ()):
                connection.execute(text("INSERT INTO cidade (nome) VALUES (:nome) ON CONFLICT (nome) DO NOTHING"), {"nome": nome})
    finally:
        engine.dispose()
    # Afeta somente este processo. O .env privado não é sobrescrito.
    os.environ["DATABASE_URL"] = isolated.render_as_string(hide_password=False)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8001)
    parser.add_argument("--schema", default=SCHEMA, help="Schema local persistente com prefixo transurban_auditorio.")
    parser.add_argument("--vazio", action="store_true", help="Não cadastrar cidades automaticamente. Não apaga dados existentes.")
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        raise SystemExit("Use uma porta entre 1024 e 65535.")
    with socket.socket() as probe:
        if probe.connect_ex(("127.0.0.1", args.port)) == 0:
            raise SystemExit(f"A porta {args.port} já está em uso. Use o servidor aberto ou escolha outra porta.")
    try:
        preparar_banco(args.schema, criar_cidades=not args.vazio)
    except Exception:
        raise SystemExit("Modo local indisponível. Confira TEST_DATABASE_URL e inicie o PostgreSQL local. Nenhum segredo foi exibido.") from None
    print(f"MODO LOCAL: schema {args.schema}. Dados de ensaio separados do Supabase.", flush=True)
    print(f"API: http://127.0.0.1:{args.port}/docs | Site: http://127.0.0.1:{args.port}/site/", flush=True)
    print("Dados existentes preservados. Nenhuma linha de ônibus fictícia é criada automaticamente.", flush=True)
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=args.port)


if __name__ == "__main__":
    main()
