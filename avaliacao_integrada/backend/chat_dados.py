"""Perguntas permitidas: o CSV calcula; a IA apenas explica os agregados."""
from backend import analise
from backend.analise_dashboard import dados_validados, observacoes_por_dia, atraso_por_dia


def total_observacoes():
    dados, _ = dados_validados()
    return {'total_observacoes': len(dados)}


def total_linhas():
    dados, _ = dados_validados()
    # Um mesmo código em cidades diferentes não identifica a mesma linha.
    return {'linhas_distintas': len(dados[['cidade', 'codigo_linha']].drop_duplicates())}


def total_atraso():
    dados, _ = dados_validados()
    return {'atraso_total_min': round(float(dados['minutos_atraso'].sum()), 4)}


def atraso_por_cidade():
    dados, _ = dados_validados()
    return analise.agrupar(dados, 'cidade')


CONSULTAS = {
    'Quantas observações de atraso existem no CSV?': total_observacoes,
    'Quantas linhas diferentes aparecem no CSV?': total_linhas,
    'Qual é o total de minutos de atraso observado?': total_atraso,
    'Como os minutos de atraso se distribuem por cidade?': atraso_por_cidade,
    'Quantas observações existem por dia?': observacoes_por_dia,
    'Qual é o total de minutos de atraso por dia?': atraso_por_dia,
}


def encontrar_pergunta(texto):
    return next((pergunta for pergunta in CONSULTAS if pergunta.casefold() == texto.strip().casefold()), None)


def consultar(pergunta):
    return CONSULTAS[pergunta]()
