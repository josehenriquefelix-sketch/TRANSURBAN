"""Criação explícita em banco novo; não executada ao iniciar a API."""
from sqlalchemy import inspect
import models
from database import Base, get_engine

def main():
    engine = get_engine()
    try:
        existentes = set(inspect(engine).get_table_names())
        if existentes.intersection(Base.metadata.tables):
            raise RuntimeError("Cidade ou linha_onibus já existe. Nenhuma alteração executada. Consulte docs/avaliacao_backend/02_BANCO.md.")
        with engine.begin() as connection:
            Base.metadata.create_all(connection)
        print("Tabelas cidade e linha_onibus criadas com PK automática e FK.")
    finally:
        engine.dispose()

if __name__ == "__main__":
    main()
