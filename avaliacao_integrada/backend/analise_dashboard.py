"""Consultas por dia sobre a mesma base usada nas totalizações."""
from backend import analise


def dados_validados():
    dados, qualidade = analise.carregar()
    if qualidade['registros_excluidos'] or qualidade['duplicatas_exatas_adicionais']:
        raise ValueError('Corrija linhas inválidas ou duplicadas do CSV antes de calcular.')
    return dados, qualidade


def observacoes_por_dia():
    dados, _ = dados_validados()
    totais = dados.groupby('data_registro').size()
    return [{'data': data, 'observacoes': int(total)} for data, total in totais.sort_index().items()]


def atraso_por_dia():
    dados, _ = dados_validados()
    totais = dados.groupby('data_registro')['minutos_atraso'].sum()
    return [{'data': data, 'atraso_total_min': round(float(total), 4)} for data, total in totais.sort_index().items()]
