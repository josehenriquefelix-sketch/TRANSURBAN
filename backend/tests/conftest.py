"""Testes reais em schema exclusivo de PostgreSQL, sem tocar tabelas existentes."""
import os
from pathlib import Path
import sys
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from database import Base, get_db
from main import app


@pytest.fixture
def banco():
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.fail("Defina TEST_DATABASE_URL para um PostgreSQL exclusivo de testes.")
    url = make_url(url)
    if url.get_backend_name() != "postgresql":
        pytest.fail("TEST_DATABASE_URL precisa usar PostgreSQL.")
    url = url.set(drivername="postgresql+psycopg2")
    schema = "teste_transurban_" + uuid4().hex
    admin = create_engine(url, hide_parameters=True)
    with admin.begin() as connection:
        connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    engine = create_engine(url, connect_args={"options": f"-csearch_path={schema}"}, hide_parameters=True)
    try:
        Base.metadata.create_all(engine)
        yield engine
    finally:
        engine.dispose()
        with admin.begin() as connection:
            connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        admin.dispose()


@pytest.fixture
def cliente(banco):
    factory = sessionmaker(bind=banco)
    def sessao():
        with factory() as db:
            yield db
    app.dependency_overrides[get_db] = sessao
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
