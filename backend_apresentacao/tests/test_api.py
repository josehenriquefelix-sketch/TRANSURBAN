"""Testes isolados: requer httpx (instalar com pip). Não acessa Supabase."""
import os
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

TEMP = tempfile.TemporaryDirectory()
os.environ['DATABASE_URL']='sqlite:///'+(Path(TEMP.name)/'test.db').as_posix()
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from main import app, engine, Base

def tearDownModule():
    engine.dispose()
    TEMP.cleanup()

class TestAPI(unittest.TestCase):
    def setUp(self):
        Base.metadata.drop_all(engine)
        self.context=TestClient(app)
        self.client=self.context.__enter__()
        self.a=self.client.post('/cidades',json={'nome':'Cidade A'}).json()['id_cidade']
        self.b=self.client.post('/cidades',json={'nome':'Cidade B'}).json()['id_cidade']
        self.linha={'id_cidade':self.a,'codigo':'D-20','nome':'Demonstração'}
        self.l=self.client.post('/linhas',json=self.linha).json()['id_linha']
        self.trecho={'id_cidade_origem':self.a,'id_cidade_destino':self.b,'nome':'A a B','distancia_km':5}
        self.t=self.client.post('/trechos',json=self.trecho).json()['id_trecho']
    def tearDown(self):
        self.context.__exit__(None,None,None)
    def post(self,rota,body,status):
        r=self.client.post(rota,json=body)
        self.assertEqual(r.status_code,status,r.text)
        return r.json()
    def test_01_health(self):
        self.assertEqual(self.client.get('/health').json()['banco'],'sqlite')
    def test_02_painel(self):
        r=self.client.get('/apresentacao');self.assertEqual(r.status_code,200);self.assertIn('TRANSURBAN',r.text)
    def test_03_contrato(self):
        self.assertIn('/atrasos',self.client.get('/openapi.json').json()['paths'])
    def test_04_cidades(self):
        self.assertEqual(len(self.client.get('/cidades').json()),2)
    def test_05_cidade_duplicada(self):
        self.post('/cidades',{'nome':'Cidade A'},409)
    def test_06_nome_vazio(self):
        self.post('/cidades',{'nome':'   '},422)
    def test_07_nome_longo(self):
        self.post('/cidades',{'nome':'x'*101},422)
    def test_08_campo_ausente(self):
        self.post('/linhas',{'nome':'Teste'},422)
    def test_09_linha_relacionada(self):
        self.assertEqual(self.client.get('/linhas').json()[0]['cidade'],'Cidade A')
    def test_10_linha_duplicada(self):
        self.post('/linhas',self.linha,409)
    def test_11_cidade_inexistente(self):
        self.post('/linhas',{**self.linha,'id_cidade':999},404)
    def test_12_id_invalido(self):
        self.post('/linhas',{**self.linha,'id_cidade':0},422)
    def test_13_trecho(self):
        self.assertEqual(len(self.client.get('/trechos').json()),1)
    def test_14_distancia(self):
        self.post('/trechos',{**self.trecho,'distancia_km':0},422)
    def test_15_origem_destino(self):
        self.post('/trechos',{**self.trecho,'id_cidade_destino':self.a},422)
    def test_16_trecho_orfao(self):
        self.post('/trechos',{**self.trecho,'id_cidade_origem':999},404)
    def vincular(self):
        return self.post('/percursos',{'id_linha':self.l,'id_trecho':self.t,'ordem':1},201)
    def test_17_percurso(self):
        self.vincular();self.assertEqual(self.client.get(f'/linhas/{self.l}/percurso').json()[0]['ordem'],1)
    def test_18_percurso_duplicado(self):
        self.vincular();self.post('/percursos',{'id_linha':self.l,'id_trecho':self.t,'ordem':2},409)
    def test_19_ordem_duplicada(self):
        self.vincular();t2=self.post('/trechos',{**self.trecho,'nome':'Outro'},201)['id_trecho'];self.post('/percursos',{'id_linha':self.l,'id_trecho':t2,'ordem':1},409)
    def test_20_ordem_invalida(self):
        self.post('/percursos',{'id_linha':self.l,'id_trecho':self.t,'ordem':0},422)
    def test_21_faixa(self):
        self.post('/faixas',{'id_trecho':self.t,'tipo':'EXCLUSIVA','status':'ATIVA'},201);self.assertEqual(len(self.client.get('/faixas').json()),1)
    def test_22_faixa_invalida(self):
        self.post('/faixas',{'id_trecho':self.t,'tipo':'INVALIDO','status':'ATIVA'},422)
    def atraso(self,**kwargs):
        return {'id_linha':self.l,'id_trecho':self.t,'data_registro':'2026-10-16','minutos_atraso':8,**kwargs}
    def test_23_atraso(self):
        self.vincular();self.post('/atrasos',self.atraso(),201);self.assertEqual(len(self.client.get('/atrasos').json()),1)
    def test_24_atraso_negativo(self):
        self.post('/atrasos',self.atraso(minutos_atraso=-1),422)
    def test_25_data_invalida(self):
        self.post('/atrasos',self.atraso(data_registro='2026-02-30'),422)
    def test_26_atraso_sem_percurso(self):
        self.post('/atrasos',self.atraso(),404)
    def test_27_recupera_apos_erro(self):
        self.post('/linhas',self.linha,409);self.post('/linhas',{**self.linha,'codigo':'NOVO'},201)
    def test_28_persistencia(self):
        self.context.__exit__(None,None,None)
        self.context=TestClient(app);self.client=self.context.__enter__()
        self.assertEqual(len(self.client.get('/linhas').json()),1)
    def test_29_csv(self):
        d=self.client.get('/indicadores').json();self.assertGreater(d['total'],0);self.assertIn('sintético',d['fonte'])
    def test_30_fk_banco(self):
        with self.assertRaises(IntegrityError):
            with engine.begin() as db:
                db.execute(text("INSERT INTO linha_onibus(id_cidade,codigo,nome) VALUES (999,'X','Teste')"))
    def test_31_ia_json(self):
        r=self.client.get('/ia/resumo')
        self.assertEqual(r.status_code,200,r.text)
        self.assertEqual(r.json()['atraso_total_min_observacoes'],1362)
        self.assertEqual(r.json()['atraso_mediano_min'],8)
        q=self.client.get('/ia/qualidade').json()
        self.assertEqual(q['registros_lidos'],180)
        self.assertEqual(q['registros_excluidos'],0)
    def test_32_ia_grupos(self):
        for dim in ['cidade','linha','data','transito','clima','trecho','periodo']:
            r=self.client.get('/ia/agrupamentos/'+dim)
            self.assertEqual(r.status_code,200,r.text)
            self.assertEqual(sum(g['observacoes'] for g in r.json()['resultados']),180)
        self.assertEqual(self.client.get('/ia/agrupamentos/inexistente').status_code,422)
    def test_33_csv_indisponivel(self):
        with patch.dict(os.environ,{'CSV_PATH':str(Path(TEMP.name)/'ausente.csv')}):
            self.assertEqual(self.client.get('/ia/resumo').status_code,503)
            self.assertEqual(self.client.get('/indicadores').status_code,503)
    def test_34_csv_duplicado_bloqueia(self):
        import pandas as pd
        import analise
        frame=pd.read_csv(analise.DEFAULT_CSV,dtype=str).iloc[:1]
        path=Path(TEMP.name)/'duplicado.csv'
        pd.concat([frame,frame]).to_csv(path,index=False)
        with patch.dict(os.environ,{'CSV_PATH':str(path)}):
            self.assertEqual(self.client.get('/ia/qualidade').json()['duplicatas_exatas_adicionais'],1)
            self.assertEqual(self.client.get('/ia/resumo').status_code,422)
            self.assertEqual(self.client.get('/indicadores').status_code,422)

if __name__=='__main__':
    unittest.main()
