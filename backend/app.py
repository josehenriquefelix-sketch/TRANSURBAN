from pathlib import Path

import pandas as pd
from flask import Flask, jsonify, request, send_from_directory
from ollama import chat


BASE = Path(__file__).resolve().parents[1]
FRONTEND = BASE / "frontend"
DATA = BASE / "data" / "atrasos_analise.csv"

MODEL = "llama3.2"

app = Flask(
    __name__,
    static_folder=str(FRONTEND),
    static_url_path=""
)


def carregar_dados():
    return pd.read_csv(
        DATA,
        encoding="utf-8",
        parse_dates=["data_registro"]
    )


def montar_contexto(df):
    total = len(df)
    media = df["minutos_atraso"].mean()
    maior = df["minutos_atraso"].max()
    menor = df["minutos_atraso"].min()

    linhas = (
        df.groupby(["codigo_linha", "nome_linha"], as_index=False)
        .agg(
            registros=("minutos_atraso", "count"),
            atraso_medio=("minutos_atraso", "mean"),
            maior_atraso=("minutos_atraso", "max")
        )
    )

    linhas["atraso_medio"] = linhas["atraso_medio"].round(2)

    maiores_linhas = linhas[
        linhas["maior_atraso"] == maior
    ].copy()

    maiores_linhas = maiores_linhas.sort_values("codigo_linha")

    return f"""
FONTE:
Massa de teste sintética acadêmica do TransUrban.
Não representa rastreamento em tempo real.

RESUMO:
Total de registros: {total}
Atraso médio: {media:.2f} minutos
Maior atraso: {maior:.0f} minutos
Menor atraso: {menor:.0f} minutos
Período: {df["data_registro"].min().date()} até {df["data_registro"].max().date()}

LINHAS ANALISADAS:
{linhas.to_csv(index=False)}

LINHAS QUE EMPATAM NO MAIOR ATRASO:
{maiores_linhas.to_csv(index=False)}

IMPORTANTE:
Se houver mais de uma linha em "LINHAS QUE EMPATAM NO MAIOR ATRASO",
informe TODAS elas. Nunca escolha apenas uma linha.
"""


def resposta_factual(pergunta, df):
    texto = pergunta.lower()

    maximo = df["minutos_atraso"].max()

    linhas = (
        df.groupby(["codigo_linha", "nome_linha"], as_index=False)
        .agg(maior_atraso=("minutos_atraso", "max"))
    )

    maiores = linhas[
        linhas["maior_atraso"] == maximo
    ].sort_values("codigo_linha")

    # Perguntas sobre qual linha teve o maior atraso
    if (
        "maior atraso" in texto
        and (
            "qual linha" in texto
            or "qual ônibus" in texto
            or "qual onibus" in texto
            or "qual foi a linha" in texto
        )
    ):
        nomes = [
            f'{row.codigo_linha} - {row.nome_linha}'
            for row in maiores.itertuples()
        ]

        return (
            f"O maior atraso registrado foi de {int(maximo)} minutos. "
            f"Houve empate entre as seguintes linhas: "
            + "; ".join(nomes)
            + ". Esses dados pertencem à massa de teste acadêmica."
        )

    # Pergunta simples sobre o maior atraso
    if "maior atraso" in texto:
        return (
            f"O maior atraso registrado foi de {int(maximo)} minutos. "
            "Os dados pertencem à massa de teste acadêmica."
        )

    # Pergunta sobre quantidade de registros
    if (
        "quantos registros" in texto
        or "quantidade de registros" in texto
    ):
        return (
            f"A massa de teste possui {len(df)} registros."
        )

    # Pergunta sobre média
    if (
        "atraso médio" in texto
        or "atraso medio" in texto
        or "média de atraso" in texto
        or "media de atraso" in texto
    ):
        return (
            f"O atraso médio da massa de teste é de "
            f"{df['minutos_atraso'].mean():.2f} minutos."
        )

    return None


def gerar_resposta(pergunta):
    df = carregar_dados()

    fato = resposta_factual(pergunta, df)

    if fato:
        return fato

    contexto = montar_contexto(df)

    mensagens = [
        {
            "role": "system",
            "content": """
Você é o assistente do projeto TransUrban.

Regras obrigatórias:
- Responda em português do Brasil.
- Use somente o contexto fornecido.
- Nunca invente dados.
- Não escolha uma linha quando houver empate.
- Se houver empate, informe todas as linhas apresentadas no contexto.
- Se uma informação não estiver no contexto, diga que ela não está disponível.
- A massa de dados é sintética e acadêmica.
- O TransUrban não possui rastreamento em tempo real.
- Seja objetivo.
"""
        },
        {
            "role": "user",
            "content": f"""
CONTEXTO DO TRANSURBAN:

{contexto}

PERGUNTA:
{pergunta}
"""
        }
    ]

    resposta = chat(
        model=MODEL,
        messages=mensagens,
        options={
            "temperature": 0,
            "num_predict": 160
        }
    )

    return resposta.message.content


@app.get("/")
def index():
    return send_from_directory(FRONTEND, "index.html")


@app.post("/api/chat")
def api_chat():
    dados = request.get_json(silent=True) or {}
    pergunta = str(dados.get("message", "")).strip()

    if not pergunta:
        return jsonify({
            "error": "Digite uma pergunta."
        }), 400

    try:
        return jsonify({
            "answer": gerar_resposta(pergunta)
        })

    except Exception as erro:
        return jsonify({
            "error": f"Erro ao consultar a IA: {erro}"
        }), 500


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
