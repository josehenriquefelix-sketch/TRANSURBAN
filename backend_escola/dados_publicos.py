"""Análise de snapshot público GTFS de Curitiba; sem inferir atrasos ou operação real."""
import hashlib
import json
from pathlib import Path
from typing import Literal
from fastapi import APIRouter, HTTPException
import pandas as pd

PASTA = Path(__file__).resolve().parent / 'data' / 'dados_publicos'
COLUNAS = ['id_programacao','codigo_linha','nome_linha','tipo_servico','operadora',
           'cidade_fonte','uf_fonte','periodo_feed_inicio','periodo_feed_fim']
router = APIRouter(prefix='/ia/dados-publicos', tags=['IA — Dados públicos: Curitiba (histórico)'])


def carregar(pasta=PASTA):
    pasta = Path(pasta)
    meta = json.loads((pasta/'fonte.json').read_text(encoding='utf-8'))
    arquivo = pasta/'programacao_curitiba.csv'
    dados = pd.read_csv(arquivo,dtype='string',keep_default_na=False)
    if list(dados.columns)!=COLUNAS:
        raise ValueError('Cabeçalho diferente do snapshot desnormalizado.')
    hash_atual = hashlib.sha256(arquivo.read_bytes()).hexdigest()
    ausentes = {c:int(dados[c].str.strip().eq('').sum()) for c in COLUNAS}
    duplicados = int(dados.id_programacao.duplicated().sum())
    conflitos = int((dados.groupby('codigo_linha').nome_linha.nunique()>1).sum())
    servicos_invalidos = int((~dados.tipo_servico.isin(['dias_uteis','sabado','domingo'])).sum())
    local_incompativel = int((dados.cidade_fonte.ne(meta['cidade']) | dados.uf_fonte.ne(meta['uf'])).sum())
    periodo = meta['periodo_declarado_feed']
    periodo_incompativel = int((dados.periodo_feed_inicio.ne(periodo['inicio']) | dados.periodo_feed_fim.ne(periodo['fim'])).sum())
    original = all((pasta/'originais'/name).is_file() and
                   hashlib.sha256((pasta/'originais'/name).read_bytes()).hexdigest()==digest
                   for name,digest in meta['arquivos_originais_sha256'].items())
    qualidade = {'fonte':'programacao_curitiba.csv','natureza':meta['natureza'],
                 'registros_lidos':len(dados),'ids_programacao_distintos':int(dados.id_programacao.nunique()),
                 'ausentes_por_coluna':ausentes,'ids_duplicados':duplicados,
                 'codigos_com_nomes_divergentes':conflitos,'servicos_invalidos':servicos_invalidos,
                 'local_incompativel':local_incompativel,'periodo_incompativel':periodo_incompativel,
                 'sha256':hash_atual,'hash_csv_confere':hash_atual==meta['csv_sha256'],
                 'hashes_originais_conferem':original,
                 'contagem_confere_com_importacao':len(dados)==meta['registros_csv'] and dados.codigo_linha.nunique()==meta['linhas_distintas'],
                 'politica':'Nenhuma linha é descartada ou substituída silenciosamente; indicadores bloqueados se houver divergência.'}
    qualidade['apta_para_calculos_do_snapshot'] = bool(len(dados) and not any(ausentes.values()) and
        not any([duplicados,conflitos,servicos_invalidos,local_incompativel,periodo_incompativel]) and
        qualidade['hash_csv_confere'] and original and qualidade['contagem_confere_com_importacao'])
    return dados,meta,qualidade


def fonte_validada(estrita=True):
    try:
        dados,meta,qualidade = carregar()
    except OSError as erro:
        raise HTTPException(503,'Snapshot público indisponível. Confira o pacote completo.') from erro
    except (ValueError,KeyError,UnicodeError) as erro:
        raise HTTPException(422,'Snapshot público inválido. Confira arquivos e origem.') from erro
    if estrita and not qualidade['apta_para_calculos_do_snapshot']:
        raise HTTPException(422,'Snapshot divergente ou inválido. Confira /ia/dados-publicos/qualidade.')
    return dados,meta,qualidade


@router.get('/fonte')
def fonte() -> dict:
    return fonte_validada(False)[1]


@router.get('/qualidade')
def qualidade() -> dict:
    return fonte_validada(False)[2]


@router.get('/resumo')
def resumo() -> dict:
    dados,meta,auditoria = fonte_validada()
    contagens = dados.groupby('codigo_linha').size()
    return {'natureza':meta['natureza'],'cidade_fonte':meta['cidade'],'uf_fonte':meta['uf'],
            'feed_oficial':False,'periodo_declarado_feed':meta['periodo_declarado_feed'],
            'fonte':'/ia/dados-publicos/fonte','sha256':auditoria['sha256'],
            'registros_programacao':len(dados),'linhas_distintas':int(len(contagens)),
            'tipos_servico_distintos':int(dados.tipo_servico.nunique()),
            'soma_registros_nos_grupos_linha':int(contagens.sum()),
            'media_registros_programacao_por_linha':round(float(contagens.mean()),4),
            'mediana_registros_programacao_por_linha':float(contagens.median()),
            'minimo_registros_por_linha':int(contagens.min()),
            'maximo_registros_por_linha':int(contagens.max()),
            'base_da_media':'Contagem de registros trip_id por código de linha, somando categorias de serviço do snapshot; não é uma média diária.',
            'viagens_realizadas':None,'atraso_medio_min':None,
            'limitacoes':meta['limitacoes']}


@router.get('/agrupamentos/{dimensao}')
def agrupamentos(dimensao:Literal['linha','servico']) -> dict:
    dados,meta,auditoria = fonte_validada()
    resultados=[]
    if dimensao=='linha':
        for (codigo,nome),grupo in dados.groupby(['codigo_linha','nome_linha'],sort=True):
            resultados.append({'codigo_linha':str(codigo),'nome_linha':str(nome),
                               'registros_programacao':len(grupo),
                               'tipos_servico_presentes':sorted(grupo.tipo_servico.unique().tolist())})
    else:
        for servico,grupo in dados.groupby('tipo_servico',sort=True):
            contagens=grupo.groupby('codigo_linha').size()
            resultados.append({'tipo_servico':str(servico),'registros_programacao':len(grupo),
                               'linhas_com_registros':int(len(contagens)),
                               'media_registros_por_linha_com_registros':round(float(contagens.mean()),4),
                               'mediana_registros_por_linha_com_registros':float(contagens.median())})
    return {'dimensao':dimensao,'cidade_fonte':meta['cidade'],
            'periodo_declarado_feed':meta['periodo_declarado_feed'],
            'registros_programacao':len(dados),'sha256':auditoria['sha256'],
            'soma_registros_nos_grupos':sum(r['registros_programacao'] for r in resultados),
            'resultados':resultados}
