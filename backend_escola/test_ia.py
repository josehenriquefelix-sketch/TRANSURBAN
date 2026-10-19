"""IA integrada: contrato HTTP, reconciliação e bloqueio de fonte inválida."""
import csv
import json
import os
import statistics
import tempfile
from pathlib import Path

# Mesmo ao executar apenas este arquivo, a importação nunca usa banco remoto.
_temp = tempfile.TemporaryDirectory()
os.environ["DATABASE_URL"] = "sqlite:///" + str(Path(_temp.name) / "ia.db")
from fastapi.testclient import TestClient
import pandas as pd
import pytest
import analise
from main import app
import main

def test_indicadores_conferidos_com_biblioteca_padrao():
    with analise.DEFAULT_CSV.open(encoding="utf-8-sig") as handle:
        numeros = [float(row["minutos_atraso"]) for row in csv.DictReader(handle)]
    with TestClient(app) as client:
        r = client.get("/ia/resumo")
        assert r.status_code == 200
        body = r.json()
        assert body["observacoes_validas"] == len(numeros) == 180
        assert body["atraso_total_min_observacoes"] == sum(numeros) == 1362
        assert body["atraso_medio_min"] == round(statistics.mean(numeros), 4)
        assert body["atraso_mediano_min"] == statistics.median(numeros) == 8
        assert body["viagens_completas"] is None
        json.dumps(body, allow_nan=False)
        for dimension in analise.DIMENSOES:
            response = client.get("/ia/agrupamentos/" + dimension)
            assert response.status_code == 200
            rows = response.json()["resultados"]
            assert sum(row["observacoes"] for row in rows) == 180
            assert sum(row["atraso_total_min"] for row in rows) == 1362
        assert client.get("/ia/agrupamentos/invalido").status_code == 422

@pytest.mark.parametrize("problem", ["atraso", "duplicata", "data", "vazio", "cabecalho"])
def test_fonte_invalida_nao_produz_indicadores(tmp_path, monkeypatch, problem):
    frame = pd.read_csv(analise.DEFAULT_CSV, dtype=str).iloc[:3].copy()
    if problem == "atraso":
        frame.loc[0, "minutos_atraso"] = "-1"
    elif problem == "duplicata":
        frame = pd.concat([frame, frame.iloc[:1]], ignore_index=True)
    elif problem == "data":
        frame.loc[0, "data_registro"] = "inválida"
    elif problem == "vazio":
        frame = frame.iloc[:0]
    else:
        frame = frame.drop(columns="cidade")
    path = tmp_path / "fonte.csv"
    frame.to_csv(path, index=False)
    original = path.read_bytes()
    monkeypatch.setenv("CSV_PATH", str(path))
    with TestClient(app) as client:
        for route in ["/ia/resumo", "/ia/agrupamentos/linha", "/ia/maiores-atrasos"]:
            assert client.get(route).status_code == 422
        assert client.get("/ia/qualidade").status_code == (422 if problem == "cabecalho" else 200)
    assert path.read_bytes() == original

def test_csv_ausente_retorna_503(tmp_path, monkeypatch):
    monkeypatch.setenv("CSV_PATH", str(tmp_path / "ausente.csv"))
    with TestClient(app) as client:
        assert client.get("/ia/resumo").status_code == 503

def test_painel_health_e_erros_documentados():
    with TestClient(app) as client:
        assert client.get("/health").json() == {"status": "ok", "banco": "sqlite_local"}
        for path, mime in [("/painel/", "text/html"), ("/painel/style.css", "text/css"), ("/painel/app.js", "javascript")]:
            response = client.get(path)
            assert response.status_code == 200
            assert mime in response.headers["content-type"]
        contract = client.get("/openapi.json").json()
        assert "404" in contract["paths"]["/linhas"]["post"]["responses"]

def test_maiores_atrasos_preservam_todos_os_empates():
    dados, _ = analise.carregar()
    with TestClient(app) as client:
        response = client.get("/ia/maiores-atrasos")
        assert response.status_code == 200
        rows = response.json()["resultados"]
        assert len(rows) == int((dados["minutos_atraso"] == 12).sum()) == 7
        assert all(row["minutos_atraso"] == 12 for row in rows)

def test_inicializacao_remota_nao_cria_tabelas(monkeypatch):
    monkeypatch.setattr(main, "is_sqlite", False)
    def proibido(*args, **kwargs):
        raise AssertionError("Inicialização remota tentou criar tabelas.")
    monkeypatch.setattr(main.Base.metadata, "create_all", proibido)
    with TestClient(app) as client:
        assert client.get("/").status_code == 200
