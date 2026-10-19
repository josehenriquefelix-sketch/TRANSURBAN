# Isola os testes em um banco temporário, sem tocar no Supabase ou banco local.
import os
import tempfile
from pathlib import Path
_tmp = tempfile.TemporaryDirectory()
os.environ["DATABASE_URL"] = "sqlite:///" + str(Path(_tmp.name) / "test.db")
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from main import app
from database import engine

def test_swagger_usa_arquivos_locais_sem_cdn():
    with TestClient(app) as client:
        response = client.get("/docs")
        assert response.status_code == 200
        for filename in ("swagger-ui-bundle.js", "swagger-ui.css", "favicon-32x32.png"):
            path = "/documentacao-static/" + filename
            assert path in response.text
            asset = client.get(path)
            assert asset.status_code == 200
            assert len(asset.content) > 100
        assert "cdn.jsdelivr.net" not in response.text
        assert "unpkg.com" not in response.text
        assert '"validatorUrl": null' in response.text

def test_fluxo_completo():
    with TestClient(app) as client:
        assert client.get("/").status_code == 200
        assert client.get("/docs").status_code == 200
        assert client.get("/openapi.json").status_code == 200
        c = client.post("/cidades", json={"nome": "Maringá"})
        assert c.status_code == 201
        cid = c.json()["id_cidade"]
        assert c.json()["nome"] == "Maringá"
        assert client.get("/cidades").json() == [c.json()]
        linha = {"codigo": "TESTE-01", "nome": "Linha de demonstração", "id_cidade": cid}
        r = client.post("/linhas", json=linha)
        assert r.status_code == 201
        assert r.json()["cidade"] == "Maringá"
        assert r.json()["id_cidade"] == cid
        assert client.get("/linhas").json() == [r.json()]
        invalida = client.post("/linhas", json={**linha, "id_cidade": 999999})
        assert invalida.status_code == 404
        assert invalida.json()["detail"] == "Cidade não encontrada"
        assert len(client.get("/linhas").json()) == 1
        assert client.post("/cidades", json={"nome": "   "}).status_code == 422
        assert client.post("/linhas", json={**linha, "id_cidade": 0}).status_code == 422
        assert client.post("/linhas", json={**linha, "codigo": ""}).status_code == 422
        with engine.connect() as conn:
            assert conn.execute(text("SELECT id_cidade FROM linha_onibus")).scalar_one() == cid
        try:
            with engine.begin() as conn:
                conn.execute(text("INSERT INTO linha_onibus(codigo,nome,id_cidade) VALUES ('X','Teste',999999)"))
        except IntegrityError:
            pass
        else:
            raise AssertionError("Banco não validou FK")
