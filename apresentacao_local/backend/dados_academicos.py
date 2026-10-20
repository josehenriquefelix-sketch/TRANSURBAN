"""Análise descritiva: o CSV é sintético, sem medições reais de ônibus."""
from hashlib import sha256
from pathlib import Path
import pandas as pd
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix='/ia', tags=['Ciência de Dados — amostra sintética'])
CSV = Path(__file__).resolve().parents[1] / 'dados' / 'atrasos.csv'

def carregar():
    return pd.read_csv(CSV, dtype={'codigo_linha': str})

@router.get('/fonte')
def fonte():
    return {'arquivo': CSV.name, 'natureza': 'Massa de teste sintética acadêmica',
            'telemetria_real': False, 'modelo_ia_treinado': False,
            'sha256': sha256(CSV.read_bytes()).hexdigest(),
            'limite': 'Não mede atrasos reais e não prevê chegadas. Não é a base pública de Curitiba.'}

@router.get('/qualidade')
def qualidade():
    df = carregar()
    datas = pd.to_datetime(df.data_registro, errors='coerce')
    return {'registros': len(df), 'colunas': list(df.columns),
            'nulos': int(df.isna().sum().sum()), 'duplicados': int(df.duplicated().sum()),
            'atrasos_negativos': int((df.minutos_atraso < 0).sum()),
            'datas_invalidas': int(datas.isna().sum()),
            'inconsistencias_tempo': int((df.tempo_real_min - df.tempo_programado_min != df.minutos_atraso).sum()),
            'data_inicial': str(datas.min().date()), 'data_final': str(datas.max().date()),
            'natureza': 'sintética'}

@router.get('/resumo')
def resumo():
    df = carregar()
    return {'natureza': 'sintética', 'registros': len(df),
            'linhas_distintas': int(df.codigo_linha.nunique()),
            'cidades': sorted(df.cidade.unique().tolist()),
            'atraso_medio_min': round(float(df.minutos_atraso.mean()), 2),
            'mediana_atraso_min': float(df.minutos_atraso.median()),
            'maior_atraso_min': int(df.minutos_atraso.max()),
            'aviso': 'Indicadores desta amostra de teste; não representam a operação real.'}

@router.get('/agrupamentos/{campo}')
def agrupamentos(campo: str):
    permitidos = {'cidade', 'periodo', 'condicao_transito', 'clima', 'codigo_linha'}
    if campo not in permitidos:
        raise HTTPException(422, 'Use: ' + ', '.join(sorted(permitidos)))
    df = carregar()
    resultado = df.groupby(campo)['minutos_atraso'].agg(['count', 'mean', 'median', 'max']).reset_index()
    resultado = resultado.rename(columns={'count': 'registros', 'mean': 'media_min', 'median': 'mediana_min', 'max': 'maximo_min'})
    return {'natureza': 'sintética', 'grupos': resultado.round(2).to_dict(orient='records')}
