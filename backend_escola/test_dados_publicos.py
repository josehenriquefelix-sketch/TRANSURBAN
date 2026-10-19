"""Reconcilia o CSV derivado com os arquivos GTFS publicados, sem assumir atrasos."""
import hashlib
import shutil
import pandas as pd
import pytest
from dados_publicos import PASTA, carregar, resumo, agrupamentos


def test_csv_reconcilia_com_programacoes_originais():
    dados,meta,q=carregar()
    orig=pd.read_csv(PASTA/'originais/trips.txt',dtype='string',keep_default_na=False)
    routes=pd.read_csv(PASTA/'originais/routes.txt',dtype='string',keep_default_na=False)
    assert q['apta_para_calculos_do_snapshot'] is True
    assert len(dados)==len(orig)==71086
    expected=orig.merge(routes,on='route_id',validate='many_to_one').set_index('trip_id').sort_index()
    actual=dados.set_index('id_programacao').sort_index()
    assert actual.index.tolist()==expected.index.tolist()
    assert actual.codigo_linha.tolist()==expected.route_id.tolist()
    assert actual.nome_linha.tolist()==expected.route_long_name.tolist()
    assert actual.tipo_servico.tolist()==expected.service_id.tolist()
    assert set(dados.cidade_fonte)=={'Curitiba'}
    assert meta['feed_oficial'] is False
    assert meta['periodo_declarado_feed']=={'inicio':'2026-09-28','fim':'2026-10-05'}


def test_resumo_e_agrupamentos_reconciliam_sem_inferir_atrasos():
    r=resumo()
    assert r['registros_programacao']==71086
    assert r['linhas_distintas']==309
    assert r['media_registros_programacao_por_linha']==round(71086/309,4)
    assert r['mediana_registros_programacao_por_linha']==162
    assert r['atraso_medio_min'] is None
    assert r['viagens_realizadas'] is None
    for dim in ['linha','servico']:
        g=agrupamentos(dim)
        assert sum(x['registros_programacao'] for x in g['resultados'])==71086
    services={x['tipo_servico']:x['registros_programacao'] for x in agrupamentos('servico')['resultados']}
    assert services=={'dias_uteis':33425,'sabado':20754,'domingo':16907}


def test_limite_para_projear_nao_altera_totais_da_fonte():
    from fastapi.testclient import TestClient
    from main import app
    with TestClient(app) as client:
        response=client.get('/ia/dados-publicos/agrupamentos/linha?limite=5')
        assert response.status_code==200
        data=response.json()
        assert len(data['resultados'])==data['grupos_exibidos']==5
        assert data['total_grupos']==309
        assert data['soma_registros_nos_grupos']==data['registros_programacao']==71086
        assert data['soma_registros_dos_grupos_exibidos']==sum(r['registros_programacao'] for r in data['resultados'])
        assert data['soma_registros_dos_grupos_exibidos']<data['soma_registros_nos_grupos']
        assert client.get('/ia/dados-publicos/agrupamentos/linha?limite=0').status_code==422


def test_modo_apresentacao_documenta_exemplos_e_separa_base_sintetica(tmp_path):
    import os
    import subprocess
    import sys
    from pathlib import Path
    env=os.environ.copy()
    env['DATABASE_URL']='sqlite:///'+(tmp_path/'sem_cadastro.db').as_posix()
    env['TRANSURBAN_APRESENTACAO']='1'
    code='''from main import app, roteiro
s=app.openapi()
assert '/ia/resumo' not in s['paths']
assert '/ia/dados-publicos/resumo' in s['paths']
assert '/apresentacao' in s['paths']
assert roteiro()['modo_apresentacao'] is True
c=s['paths']['/cidades']['post']['requestBody']['content']['application/json']['examples']
assert c['cadastro_valido']['value']=={'nome':'Sarandi'}
assert c['nome_vazio']['value']=={'nome':'   '}
l=s['paths']['/linhas']['post']['requestBody']['content']['application/json']['examples']
assert l['cidade_inexistente']['value']['id_cidade']==999999
assert '/ia/resumo' not in str(roteiro()['sequencia'])
print('Modo de apresentação e exemplos documentados conferidos.')'''
    subprocess.run([sys.executable,'-c',code],env=env,cwd=Path(__file__).resolve().parent,check=True,capture_output=True,text=True)


@pytest.mark.parametrize('tipo',['duplicata','arquivo_alterado'])
def test_fonte_alterada_nao_e_aceita(tmp_path,tipo):
    pasta=tmp_path/'snapshot'
    shutil.copytree(PASTA,pasta)
    path=pasta/'programacao_curitiba.csv'
    if tipo=='duplicata':
        df=pd.read_csv(path,dtype='string')
        pd.concat([df,df.iloc[:1]]).to_csv(path,index=False)
    else:
        path.write_bytes(path.read_bytes().replace(b'Curitiba',b'OutraCid',1))
    _,_,q=carregar(pasta)
    assert q['apta_para_calculos_do_snapshot'] is False
    assert q['hash_csv_confere'] is False
