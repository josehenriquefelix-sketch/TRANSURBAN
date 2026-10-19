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
