"""Indicadores descritivos com rastreabilidade e critérios explícitos."""
import hashlib
import json
from io import BytesIO
from pathlib import Path

import numpy as np
import pandas as pd

COLUNAS = ['data_registro', 'cidade', 'codigo_linha', 'nome_linha', 'trecho',
           'tipo_trecho', 'periodo', 'condicao_transito', 'clima',
           'tempo_programado_min', 'tempo_real_min', 'minutos_atraso', 'observacao']
NUMERICAS = ['tempo_programado_min', 'tempo_real_min', 'minutos_atraso']
TEXTOS = [c for c in COLUNAS if c not in NUMERICAS + ['data_registro', 'observacao']]
DEFAULT_CSV = Path(__file__).resolve().parents[1] / 'data' / 'atrasos_analise.csv'
LIMITACOES = [
    'Fonte sintética acadêmica reproduzida no pacote Módulo 6; não é telemetria real.',
    'Cada linha é uma observação de atraso em um trecho, não uma viagem completa.',
    'Sem id_viagem não é possível contar viagens completas, passageiros ou ônibus únicos.',
    'A soma mede minutos por observação; não equivale ao tempo perdido por passageiros.',
    'Duplicatas exatas são sinalizadas; a API interrompe os indicadores até revisão da fonte.',
    'A auditoria identifica linhas inválidas; a API interrompe os indicadores até correção da fonte.',
    'Os agrupamentos descrevem associações, não demonstram causalidade nem fazem previsão de chegada.',
]

def registros(frame):
    # Pandas converte escalares numpy e valores ausentes em JSON válido.
    return json.loads(frame.to_json(orient='records', force_ascii=False))

def carregar(path=DEFAULT_CSV):
    path = Path(path)
    conteudo = path.read_bytes()
    bruto = pd.read_csv(BytesIO(conteudo), dtype='string', encoding='utf-8-sig', keep_default_na=False)
    faltantes = sorted(set(COLUNAS) - set(bruto.columns))
    if faltantes:
        raise ValueError('Colunas obrigatórias ausentes: ' + ', '.join(faltantes))
    d = bruto[COLUNAS].copy()
    for c in COLUNAS:
        d[c] = d[c].str.strip().replace('', pd.NA)
    ausentes = {c: int(d[c].isna().sum()) for c in COLUNAS}
    duplicatas = int(d.duplicated().sum())
    invalidos = pd.Series(False, index=d.index)
    motivos = {}

    def marcar(nome, mascara):
        nonlocal invalidos
        mascara = mascara.fillna(True).astype(bool)
        motivos[nome] = int(mascara.sum())
        invalidos |= mascara

    for c in TEXTOS:
        marcar('ausente_' + c, d[c].isna())
    datas = pd.to_datetime(d['data_registro'], format='%Y-%m-%d', errors='coerce')
    marcar('data_invalida', datas.isna())
    d['data_registro'] = datas.dt.strftime('%Y-%m-%d')
    for c in NUMERICAS:
        d[c] = pd.to_numeric(d[c], errors='coerce').astype(float)
        marcar('numero_invalido_' + c, ~np.isfinite(d[c]))
    marcar('tempo_programado_nao_positivo', d['tempo_programado_min'] <= 0)
    marcar('tempo_real_negativo', d['tempo_real_min'] < 0)
    marcar('atraso_negativo', d['minutos_atraso'] < 0)
    esperado = (d['tempo_real_min'] - d['tempo_programado_min']).clip(lower=0)
    finitos = np.isfinite(d[NUMERICAS]).all(axis=1)
    marcar('atraso_incompativel_com_tempos', finitos & ~np.isclose(d['minutos_atraso'], esperado, atol=0.01, rtol=0))
    limpo = d.loc[~invalidos].copy()
    conflitos = limpo.groupby(['cidade', 'codigo_linha'])['nome_linha'].nunique()
    qualidade = {
        'arquivo': path.name,
        'sha256': hashlib.sha256(conteudo).hexdigest(),
        'origem': 'massa sintética acadêmica; conferir data/ORIGEM_DADOS.txt',
        'registros_lidos': len(d), 'registros_validos': len(limpo),
        'registros_excluidos': int(invalidos.sum()),
        'linhas_csv_excluidas': [int(i) + 2 for i in d.index[invalidos]],
        'ausentes_por_coluna': ausentes, 'motivos_exclusao': motivos,
        'duplicatas_exatas_adicionais': duplicatas,
        'politica_duplicatas': 'mantidas e sinalizadas',
        'codigos_com_nomes_divergentes': int((conflitos > 1).sum()),
        'colunas_extras_ignoradas': sorted(set(bruto.columns) - set(COLUNAS)),
        'tipos_originais': {c: str(bruto[c].dtype) for c in COLUNAS},
        'tipos_analise': {c: str(d[c].dtype) for c in COLUNAS},
        'observacao_qualidade': 'Motivos podem se sobrepor; não somar para obter registros excluídos.',
    }
    return limpo, qualidade

def resumo(d, qualidade):
    s = d['minutos_atraso']
    n = len(d)
    def valor(f):
        return round(float(f()), 4) if n else None
    return {
        'fonte': qualidade['arquivo'], 'sha256': qualidade['sha256'],
        'registros_lidos': qualidade['registros_lidos'], 'observacoes_validas': n,
        'observacoes_excluidas': qualidade['registros_excluidos'],
        'viagens_completas': None,
        'linhas_distintas_cidade_codigo': len(d[['cidade', 'codigo_linha']].drop_duplicates()),
        'cidades_distintas': int(d['cidade'].nunique()),
        'atraso_total_min_observacoes': round(float(s.sum()), 4),
        'atraso_medio_min': valor(s.mean), 'atraso_mediano_min': valor(s.median),
        'maior_atraso_min': valor(s.max),
        'observacoes_acima_10_min': int((s > 10).sum()),
        'percentual_acima_10_min': round(float((s > 10).mean() * 100), 4) if n else None,
        'periodo_inicio': str(d['data_registro'].min()) if n else None,
        'periodo_fim': str(d['data_registro'].max()) if n else None,
        'limitacoes': LIMITACOES,
    }

DIMENSOES = {'linha': ['cidade', 'codigo_linha'], 'cidade': ['cidade'],
             'data': ['data_registro'], 'periodo': ['periodo'],
             'transito': ['condicao_transito'], 'clima': ['clima'], 'trecho': ['trecho']}

def agrupar(d, dimensao):
    if dimensao not in DIMENSOES:
        raise ValueError('Dimensão inválida')
    cols = DIMENSOES[dimensao]
    a = d.groupby(cols, dropna=False)['minutos_atraso'].agg(
        observacoes='count', atraso_total_min='sum', atraso_medio_min='mean',
        atraso_mediano_min='median', maior_atraso_min='max').reset_index()
    if dimensao == 'linha':
        nomes = d.groupby(cols)['nome_linha'].agg(lambda x: ' / '.join(sorted(set(x.dropna())))).reset_index()
        a = a.merge(nomes, on=cols, how='left')
    return registros(a.sort_values(cols).round(4))

def maiores(d):
    if d.empty:
        return []
    return registros(d.loc[d['minutos_atraso'] == d['minutos_atraso'].max(),
                           ['data_registro', 'cidade', 'codigo_linha', 'nome_linha', 'trecho', 'minutos_atraso']])

if __name__ == '__main__':
    dados, qualidade = carregar()
    if dados.empty or qualidade['registros_excluidos'] or qualidade['duplicatas_exatas_adicionais'] or qualidade['codigos_com_nomes_divergentes']:
        raise ValueError('Corrija ou justifique problemas da fonte antes dos cálculos.')
    print('Primeiras cinco observações:')
    print(dados.head().to_string(index=False))
    print('Resumo:')
    print(json.dumps(resumo(dados, qualidade), ensure_ascii=False, indent=2))
