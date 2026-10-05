"""Integração HTTP/ORM; SQLite temporário, nunca escreve no Supabase."""
import json
import tempfile
import unittest
import os
from unittest.mock import patch
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from backend.database import Base, get_db
from backend.main import app
from backend.models import Cidade, LinhaOnibus

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.engine = create_engine(f'sqlite:///{Path(self.tmp.name) / "teste.db"}', connect_args={'check_same_thread': False})
        @event.listens_for(self.engine, 'connect')
        def fk(conn, _): conn.execute('PRAGMA foreign_keys=ON')
        Base.metadata.create_all(self.engine)
        def session():
            with Session(self.engine) as s: yield s
        app.dependency_overrides[get_db] = session
        # Sem lifespan: banco temporário já criado; não toca o banco configurado.
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        self.engine.dispose()
        self.tmp.cleanup()

    def cidade(self):
        r = self.client.post('/cidades', json={'nome': 'Maringá'})
        self.assertEqual(r.status_code, 201)
        return r.json()['id_cidade']

    def test_cadastro_consulta_persistencia_e_relacionamento(self):
        cid = self.cidade()
        r = self.client.post('/linhas', json={'id_cidade': cid, 'codigo': '001', 'nome': 'Linha acadêmica'})
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()['cidade'], 'Maringá')
        self.assertEqual(self.client.get('/linhas').json(), [r.json()])
        self.assertEqual(self.client.get(f'/linhas/{r.json()["id_linha"]}').json(), r.json())
        with Session(self.engine) as s:
            linha = s.scalar(select(LinhaOnibus))
            self.assertEqual(linha.id_cidade, cid)
            self.assertEqual(linha.cidade.nome, 'Maringá')
        self.assertEqual(self.client.get('/cidades').json()[0]['nome'], 'Maringá')

    def test_fk_inexistente_404_e_banco_vazio(self):
        r = self.client.post('/linhas', json={'id_cidade': 999999, 'codigo': 'X', 'nome': 'Teste'})
        self.assertEqual(r.status_code, 404)
        self.assertEqual(self.client.get('/linhas').json(), [])

    def test_duplicata_409_e_rollback(self):
        cid = self.cidade()
        self.assertEqual(self.client.post('/cidades', json={'nome': 'Maringá'}).status_code, 409)
        v = {'id_cidade': cid, 'codigo': '001', 'nome': 'Teste'}
        self.assertEqual(self.client.post('/linhas', json=v).status_code, 201)
        self.assertEqual(self.client.post('/linhas', json=v).status_code, 409)
        self.assertEqual(self.client.post('/cidades', json={'nome': 'Sarandi'}).status_code, 201)

    def test_codigo_pode_repetir_em_cidades_distintas(self):
        for nome in ['Maringá', 'Sarandi']:
            cid = self.client.post('/cidades', json={'nome': nome}).json()['id_cidade']
            self.assertEqual(self.client.post('/linhas', json={'id_cidade': cid, 'codigo': '001', 'nome': 'Teste'}).status_code, 201)
        self.assertEqual(len(self.client.get('/linhas').json()), 2)

    def test_validacao_422(self):
        for body in [{'nome': ''}, {'nome': '   '}, {'nome': 'A' * 101}, {'nome': 'Teste', 'id_cidade': 1}]:
            self.assertEqual(self.client.post('/cidades', json=body).status_code, 422)
        for cid in [0, -1, True, '1']:
            self.assertEqual(self.client.post('/linhas', json={'id_cidade': cid, 'codigo': '001', 'nome': 'Teste'}).status_code, 422)

    def test_fk_tambem_protegida_no_banco(self):
        with Session(self.engine) as s:
            s.add(LinhaOnibus(id_cidade=999, codigo='X', nome='Teste'))
            with self.assertRaises(IntegrityError):
                s.commit()
            s.rollback()

    def test_get_ia_docs_health_e_filtros(self):
        for route in ['/', '/health', '/docs', '/openapi.json', '/ia/qualidade', '/ia/resumo', '/ia/maiores-atrasos']:
            self.assertEqual(self.client.get(route).status_code, 200, route)
        for d in ['cidade', 'linha', 'data', 'periodo', 'transito', 'clima', 'trecho']:
            r = self.client.get('/ia/agrupamentos/' + d)
            self.assertEqual(r.status_code, 200)
            json.dumps(r.json(), allow_nan=False)
        self.assertEqual(self.client.get('/ia/agrupamentos/invalido').status_code, 422)
        self.assertEqual(self.client.get('/linhas/999999').status_code, 404)
        self.assertEqual(self.client.get('/linhas?limite=0').status_code, 422)
        self.assertEqual(self.client.get('/linhas?id_cidade=999999').json(), [])

    def test_fonte_invalida_interrompe_indicadores_com_422(self):
        import pandas as pd
        from backend.analise import DEFAULT_CSV
        frame = pd.read_csv(DEFAULT_CSV, dtype=str).iloc[:2].copy()
        frame.loc[0, 'minutos_atraso'] = '-1'
        csv_path = Path(self.tmp.name) / 'invalido.csv'
        frame.to_csv(csv_path, index=False)
        with patch.dict(os.environ, {'CSV_PATH': str(csv_path)}):
            q = self.client.get('/ia/qualidade')
            self.assertEqual(q.status_code, 200)
            self.assertEqual(q.json()['registros_excluidos'], 1)
            for rota in ['/ia/resumo', '/ia/agrupamentos/linha', '/ia/maiores-atrasos']:
                self.assertEqual(self.client.get(rota).status_code, 422)
        with patch.dict(os.environ, {'CSV_PATH': str(Path(self.tmp.name) / 'ausente.csv')}):
            self.assertEqual(self.client.get('/ia/resumo').status_code, 503)

    def test_csv_vazio_duplicado_e_cabecalho_invalido(self):
        import pandas as pd
        from backend.analise import DEFAULT_CSV
        frame = pd.read_csv(DEFAULT_CSV, dtype=str).iloc[:1].copy()
        csv_path = Path(self.tmp.name) / 'teste.csv'
        fontes = [frame.iloc[:0], pd.concat([frame, frame], ignore_index=True), frame.drop(columns='cidade')]
        for fonte in fontes:
            fonte.to_csv(csv_path, index=False)
            with patch.dict(os.environ, {'CSV_PATH': str(csv_path)}):
                self.assertEqual(self.client.get('/ia/resumo').status_code, 422)

if __name__ == '__main__':
    unittest.main()
