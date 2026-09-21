from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

BASE = Path(__file__).resolve().parent.parent
CAMINHO_CSV = BASE / "database" / "dados.csv"
PASTA_RESULTADOS = BASE / "ia" / "resultados"
PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)


def carregar_dados():
    dados = pd.read_csv(CAMINHO_CSV, parse_dates=["data_registro"])
    return dados


def calcular_estatisticas(dados, coluna):
    serie = dados[coluna]
    moda = serie.mode()

    return {
        "media": float(serie.mean()),
        "mediana": float(serie.median()),
        "moda": float(moda.iloc[0]) if not moda.empty else None,
        "minimo": float(serie.min()),
        "maximo": float(serie.max()),
        "amplitude": float(serie.max() - serie.min()),
        "variancia": float(serie.var()),
        "desvio_padrao": float(serie.std()),
    }


def agregar_dados(
    dados,
    coluna_grupo,
    coluna_valor,
    operacao="media",
):
    grupo = dados.groupby(coluna_grupo)[coluna_valor]

    if operacao == "soma":
        return grupo.sum()
    if operacao == "contagem":
        return grupo.count()
    if operacao == "media":
        return grupo.mean()

    raise ValueError(
        "Operação deve ser: soma, contagem ou media"
    )


def classificar_valor(valor):
    # Regra acadêmica do TransUrban:
    # até 5 = Baixo; até 10 = Moderado;
    # até 15 = Alto; acima de 15 = Muito alto.
    if valor <= 5:
        return "Baixo"
    if valor <= 10:
        return "Moderado"
    if valor <= 15:
        return "Alto"
    return "Muito alto"


def aplicar_classificacao(
    dados,
    coluna="minutos_atraso",
):
    resultado = dados.copy()
    resultado["classificacao_atraso"] = (
        resultado[coluna].apply(classificar_valor)
    )
    return resultado


def gerar_visualizacao(
    resultado,
    titulo,
    eixo_x,
    eixo_y,
    nome_arquivo,
):
    ax = resultado.plot(kind="bar")
    ax.set_title(titulo)
    ax.set_xlabel(eixo_x)
    ax.set_ylabel(eixo_y)
    plt.tight_layout()

    caminho = PASTA_RESULTADOS / nome_arquivo
    plt.savefig(caminho, dpi=160)
    plt.close()
    return caminho
