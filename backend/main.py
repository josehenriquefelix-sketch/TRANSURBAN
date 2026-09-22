from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db
from routes import cidades_router

app = FastAPI(
    title="TransUrban API - Módulo 6",
    version="1.0.0",
    description=(
        "Primeiras rotas do Projeto Integrador TransUrban. "
        "A tabela cidade foi escolhida porque possui PK simples, "
        "não possui FK e não possui chave composta."
    ),
)

app.include_router(cidades_router)


@app.get("/")
def raiz():
    return {
        "projeto": "TransUrban",
        "modulo": "Do banco de dados às primeiras rotas",
        "documentacao_api": "/docs",
        "rota_trabalhada": "/cidades/",
    }


@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {
        "status": "ok",
        "database": "PostgreSQL/Supabase conectado",
    }


def demonstrar_analise():
    from analise import (
        agregar_dados,
        aplicar_classificacao,
        calcular_estatisticas,
        carregar_dados,
        gerar_visualizacao,
    )

    dados = carregar_dados()

    print("Primeiras linhas:")
    print(dados.head())

    print("\nColunas:")
    print(list(dados.columns))

    print("\nQuantidade de registros:")
    print(len(dados))

    print("\nEstatísticas de minutos_atraso:")
    estatisticas = calcular_estatisticas(
        dados,
        "minutos_atraso",
    )
    for nome, valor in estatisticas.items():
        print(f"{nome}: {valor:.2f}" if valor is not None else f"{nome}: -")

    print("\nAtraso médio por condição de trânsito:")
    agregado = agregar_dados(
        dados,
        "condicao_transito",
        "minutos_atraso",
        "media",
    )
    print(agregado.round(2))

    classificados = aplicar_classificacao(dados)
    print("\nClassificação dos primeiros registros:")
    print(
        classificados[
            ["minutos_atraso", "classificacao_atraso"]
        ].head()
    )

    caminho = gerar_visualizacao(
        agregado.sort_values(),
        "Atraso médio por condição de trânsito",
        "Condição de trânsito",
        "Minutos de atraso",
        "grafico_02_transito.png",
    )
    print("\nGráfico salvo em:", caminho)


if __name__ == "__main__":
    demonstrar_analise()
