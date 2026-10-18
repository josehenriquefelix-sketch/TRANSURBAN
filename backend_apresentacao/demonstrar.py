"""Ensaio HTTP real: API deve estar em execução. Cria dados fictícios novos."""
import json
import os
from pathlib import Path
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import HTTPError

BASE = os.environ.get('TRANSURBAN_URL', 'http://127.0.0.1:8000')
def requisicao(method, path, dados=None, esperado=200):
    req = Request(BASE+path, data=json.dumps(dados).encode() if dados is not None else None, headers={'Content-Type':'application/json'}, method=method)
    try:
        with urlopen(req, timeout=15) as r:
            codigo, corpo = r.status, json.load(r)
    except HTTPError as r:
        codigo, corpo = r.code, json.load(r)
    if codigo != esperado:
        raise AssertionError(f'{method} {path}: esperado {esperado}, obtido {codigo}: {corpo}')
    evidencias.append({'metodo':method, 'rota':path, 'status':codigo, 'resposta':corpo})
    return corpo
evidencias=[]
def main():
    tag=datetime.now().strftime('%m%d%H%M%S%f')
    saude=requisicao('GET','/health')
    c1=requisicao('POST','/cidades',{'nome':'Cidade A DEMO '+tag},201)['id_cidade']
    c2=requisicao('POST','/cidades',{'nome':'Cidade B DEMO '+tag},201)['id_cidade']
    linha={'id_cidade':c1,'codigo':'D'+tag,'nome':'Linha fictícia de demonstração'}
    lid=requisicao('POST','/linhas',linha,201)['id_linha']
    tid=requisicao('POST','/trechos',{'id_cidade_origem':c1,'id_cidade_destino':c2,'nome':'Trecho fictício','distancia_km':12.5},201)['id_trecho']
    requisicao('POST','/percursos',{'id_linha':lid,'id_trecho':tid,'ordem':1},201)
    requisicao('POST','/faixas',{'id_trecho':tid,'tipo':'EXCLUSIVA','status':'ATIVA'},201)
    requisicao('POST','/atrasos',{'id_linha':lid,'id_trecho':tid,'data_registro':datetime.now().date().isoformat(),'minutos_atraso':8,'observacao':'Registro fictício de apresentação'},201)
    requisicao('POST','/linhas',linha,409)
    requisicao('POST','/cidades',{'nome':'   '},422)
    requisicao('POST','/linhas',{**linha,'id_cidade':2147483647},404)
    for rota in ['/cidades','/linhas','/trechos',f'/linhas/{lid}/percurso','/faixas','/atrasos','/indicadores','/health']:
        requisicao('GET',rota)
    dest=Path(__file__).resolve().parent/'evidencias'
    dest.mkdir(exist_ok=True)
    nome='ensaio_supabase.json' if saude['banco']=='postgresql' else 'ensaio_local.json'
    (dest/nome).write_text(json.dumps(evidencias,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'ENSAIO APROVADO: {len(evidencias)} requisições. Linha={lid}; trecho={tid}. Evidências: {dest}')
if __name__=='__main__':
    main()
