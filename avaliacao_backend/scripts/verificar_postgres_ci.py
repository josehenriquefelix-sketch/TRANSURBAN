"""Teste PostgreSQL somente em serviço CI local e descartável."""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sqlalchemy.engine import make_url

url = make_url(os.environ['DATABASE_URL'])
if url.get_backend_name() != 'postgresql' or url.host not in ('127.0.0.1', 'localhost') or url.database != 'transurban_ci':
    raise RuntimeError('Este script aceita apenas PostgreSQL local descartável transurban_ci.')

from sqlalchemy import text
from fastapi.testclient import TestClient
from backend.database import Base, engine
from backend.main import app

# Base declarada pelos models já importados; execução apenas no serviço descartável.
Base.metadata.create_all(engine)
resultados = []
with TestClient(app) as client:
    def request(method, path, expected, body=None):
        r = client.request(method, path, json=body) if body else client.request(method, path)
        resultados.append({'metodo': method, 'rota': path, 'status': r.status_code, 'resposta': r.json()})
        assert r.status_code == expected, r.text
        return r.json()
    health = request('GET', '/health', 200)
    assert health['banco'] == 'postgresql'
    cidade = request('POST', '/cidades', 201, {'nome':'Cidade CI TRANSURBAN'})
    linha = request('POST', '/linhas', 201, {'id_cidade':cidade['id_cidade'],'codigo':'CI-001','nome':'Linha CI'})
    assert linha['cidade'] == cidade['nome']
    request('GET', '/cidades', 200)
    assert request('GET', '/linhas', 200)[0] == linha
    request('POST', '/linhas', 404, {'id_cidade':999999,'codigo':'X','nome':'Teste inválido'})
    with engine.connect() as conn:
        persistido = conn.execute(text('SELECT id_linha, id_cidade, nome FROM linha_onibus WHERE id_linha = :id'), {'id':linha['id_linha']}).mappings().one()
        assert persistido['id_cidade'] == cidade['id_cidade']
        resultados.append({'verificacao':'SQL direto PostgreSQL','registro':dict(persistido)})

dest = ROOT/'evidencias'/'postgres_ci.json'
dest.write_text(json.dumps({'banco':'PostgreSQL local descartável CI; não Supabase','aprovado':True,'resultados':resultados},ensure_ascii=False,indent=2))
print('PostgreSQL CI: cadastro, consulta, relacionamento e persistência verificados.')
