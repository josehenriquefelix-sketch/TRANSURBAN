"""Contrato HTTP com SDK real e PostgREST simulado; não é teste do Supabase remoto."""
import unittest
import httpx
from postgrest import SyncPostgrestClient
from fastapi.testclient import TestClient
from unittest.mock import patch
from backend.main import app
from backend.controller import cidades, linhas

class SDKTests(unittest.TestCase):
 def test_crud_com_sdk_real(self):
  calls=[]
  def server(request):
   calls.append((request.method,request.url.path))
   if request.url.path.endswith('/cidade'):
    return httpx.Response(200,json=[{'id_cidade':7,'nome':'Maringá'}])
   if request.method=='DELETE':return httpx.Response(200,json=[{'id_linha':31}])
   return httpx.Response(201 if request.method=='POST' else 200,json=[{'id_linha':31,'id_cidade':7,'codigo':'T01','nome':'Teste','cidade':{'nome':'Maringá'}}])
  db=SyncPostgrestClient('https://teste.invalid/rest/v1')
  db.session.close()
  db.session=httpx.Client(base_url='https://teste.invalid/rest/v1',transport=httpx.MockTransport(server))
  with patch.object(cidades,'get_supabase',lambda:db),patch.object(linhas,'get_supabase',lambda:db):
   c=TestClient(app);body={'id_cidade':7,'codigo':'T01','nome':'Teste'}
   self.assertEqual(c.post('/linhas',json=body).status_code,201)
   self.assertEqual(c.put('/linhas/31',json=body).status_code,200)
   self.assertEqual(c.get('/linhas/31').json()['cidade'],'Maringá')
   self.assertEqual(c.delete('/linhas/31').status_code,204)
  self.assertIn(('POST','/rest/v1/linha_onibus'),calls)
  db.session.close()

class AnaliseTests(unittest.TestCase):
 def test_calculos_independentes(self):
  import csv
  from pathlib import Path
  rows=list(csv.DictReader((Path(__file__).parents[1]/'data/atrasos_analise.csv').open(encoding='utf-8-sig')))
  values=[float(x['minutos_atraso']) for x in rows]
  c=TestClient(app);s=c.get('/ia/resumo').json()
  self.assertEqual(len(rows),180)
  self.assertEqual(s['observacoes_validas'],len(rows))
  self.assertEqual(s['atraso_total_min_observacoes'],sum(values))
  self.assertAlmostEqual(s['atraso_medio_min'],sum(values)/len(values),places=4)
  self.assertEqual(s['maior_atraso_min'],max(values))
  for key in ('cidade','periodo','transito','clima'):
   groups=c.get('/ia/totalizacao/'+key).json()
   self.assertEqual(sum(x['observacoes'] for x in groups),len(rows))
   self.assertEqual(sum(x['atraso_total_min'] for x in groups),sum(values))
 def test_validacoes_linha(self):
  c=TestClient(app)
  for payload in ({'id_cidade':1,'codigo':'X','nome':' a '},{'id_cidade':'1','codigo':'X','nome':'Teste'},{'id_cidade':0,'codigo':'X','nome':'Teste'},{'id_cidade':1,'codigo':'X','nome':'Teste','cidade':'Copiada'}):
   self.assertEqual(c.post('/linhas',json=payload).status_code,422)
 def test_cors_put_delete(self):
  c=TestClient(app)
  for method in ('POST','PUT','DELETE'):
   r=c.options('/linhas',headers={'Origin':'http://127.0.0.1:5500','Access-Control-Request-Method':method,'Access-Control-Request-Headers':'content-type'})
   self.assertEqual(r.status_code,200)
  self.assertNotIn('access-control-allow-origin',c.options('/linhas',headers={'Origin':'https://invalido.example','Access-Control-Request-Method':'PUT'}).headers)
