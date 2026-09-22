from datetime import date
from pathlib import Path

import pandas as pd
import psycopg2
from flask import Flask, jsonify, request, send_from_directory
from ollama import chat

from database import consultar_todos, consultar_um, database_configurada, executar_retorno

ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "frontend"
DATA = ROOT / "data" / "atrasos_analise.csv"
MODEL = "llama3.2"

app = Flask(__name__, static_folder=str(FRONTEND), static_url_path="")


def erro_banco(erro):
    if isinstance(erro, RuntimeError):
        return jsonify({"error": str(erro)}), 503
    if isinstance(erro, psycopg2.Error):
        return jsonify({"error": "Não foi possível executar a operação no Supabase/PostgreSQL. Confira a conexão e os dados enviados."}), 500
    return jsonify({"error": "Erro interno ao acessar o banco de dados."}), 500


def inteiro(valor, nome, permitir_zero=False):
    try:
        numero = int(valor)
    except (TypeError, ValueError):
        raise ValueError(f"{nome} deve ser um número inteiro.")
    minimo = 0 if permitir_zero else 1
    if numero < minimo:
        raise ValueError(f"{nome} possui valor inválido.")
    return numero


def data_iso(valor):
    try:
        return date.fromisoformat(str(valor))
    except (TypeError, ValueError):
        raise ValueError("data_registro deve usar o formato AAAA-MM-DD.")


@app.get("/")
def index():
    return send_from_directory(FRONTEND, "index.html")


@app.get("/api/health")
def api_health():
    if not database_configurada():
        return jsonify({
            "status": "configuracao_pendente",
            "database": False,
            "message": "Backend ativo. Configure DATABASE_URL para conectar ao Supabase."
        }), 503
    try:
        resultado = consultar_um("SELECT 1 AS ok;")
        return jsonify({
            "status": "ok",
            "database": bool(resultado and resultado["ok"] == 1),
            "message": "Backend e PostgreSQL/Supabase conectados."
        })
    except Exception as erro:
        return erro_banco(erro)


@app.get("/api/cidades")
def api_cidades():
    try:
        return jsonify(consultar_todos(
            "SELECT id_cidade, nome FROM cidade ORDER BY id_cidade;"
        ))
    except Exception as erro:
        return erro_banco(erro)


@app.get("/api/linhas")
def api_linhas():
    try:
        return jsonify(consultar_todos("""
            SELECT l.id_linha, l.codigo, l.nome, l.id_cidade, c.nome AS cidade
            FROM linha_onibus l
            JOIN cidade c ON c.id_cidade = l.id_cidade
            ORDER BY l.codigo, l.id_linha;
        """))
    except Exception as erro:
        return erro_banco(erro)


@app.get("/api/trechos")
def api_trechos():
    try:
        dados = consultar_todos("""
            SELECT t.id_trecho, t.nome, t.distancia_km,
                   t.id_cidade_origem, origem.nome AS cidade_origem,
                   t.id_cidade_destino, destino.nome AS cidade_destino
            FROM trecho t
            JOIN cidade origem ON origem.id_cidade = t.id_cidade_origem
            JOIN cidade destino ON destino.id_cidade = t.id_cidade_destino
            ORDER BY t.id_trecho;
        """)
        for item in dados:
            if item.get("distancia_km") is not None:
                item["distancia_km"] = float(item["distancia_km"])
        return jsonify(dados)
    except Exception as erro:
        return erro_banco(erro)


@app.get("/api/atrasos")
def api_atrasos():
    try:
        limite = request.args.get("limit", 50, type=int)
        limite = max(1, min(limite or 50, 200))
        return jsonify(consultar_todos("""
            SELECT r.id_atraso, r.data_registro, r.minutos_atraso, r.observacao,
                   l.id_linha, l.codigo AS codigo_linha, l.nome AS linha,
                   t.id_trecho, t.nome AS trecho
            FROM registro_atraso r
            JOIN linha_onibus l ON l.id_linha = r.id_linha
            JOIN trecho t ON t.id_trecho = r.id_trecho
            ORDER BY r.data_registro DESC, r.id_atraso DESC
            LIMIT %s;
        """, (limite,)))
    except Exception as erro:
        return erro_banco(erro)


@app.get("/api/atrasos/resumo")
def api_atrasos_resumo():
    try:
        resumo = consultar_um("""
            SELECT COUNT(*)::INTEGER AS total_registros,
                   ROUND(AVG(minutos_atraso), 2) AS atraso_medio,
                   MAX(minutos_atraso) AS maior_atraso,
                   MIN(minutos_atraso) AS menor_atraso
            FROM registro_atraso;
        """) or {}
        if resumo.get("atraso_medio") is not None:
            resumo["atraso_medio"] = float(resumo["atraso_medio"])
        return jsonify(resumo)
    except Exception as erro:
        return erro_banco(erro)


@app.post("/api/atrasos")
def api_criar_atraso():
    dados = request.get_json(silent=True) or {}
    try:
        id_linha = inteiro(dados.get("id_linha"), "id_linha")
        id_trecho = inteiro(dados.get("id_trecho"), "id_trecho")
        minutos = inteiro(dados.get("minutos_atraso"), "minutos_atraso", True)
        registro_em = data_iso(dados.get("data_registro"))

        observacao = dados.get("observacao")
        observacao = str(observacao).strip() if observacao is not None else None
        observacao = observacao or None
        if observacao and len(observacao) > 255:
            raise ValueError("observacao deve ter no máximo 255 caracteres.")

        if not consultar_um("SELECT id_linha FROM linha_onibus WHERE id_linha=%s;", (id_linha,)):
            return jsonify({"error": "id_linha não existe no banco."}), 400
        if not consultar_um("SELECT id_trecho FROM trecho WHERE id_trecho=%s;", (id_trecho,)):
            return jsonify({"error": "id_trecho não existe no banco."}), 400

        novo = executar_retorno("""
            INSERT INTO registro_atraso
                (id_atraso, id_linha, id_trecho, data_registro, minutos_atraso, observacao)
            VALUES
                ((SELECT COALESCE(MAX(id_atraso),0)+1 FROM registro_atraso),
                 %s, %s, %s, %s, %s)
            RETURNING id_atraso, id_linha, id_trecho, data_registro, minutos_atraso, observacao;
        """, (id_linha, id_trecho, registro_em, minutos, observacao))

        return jsonify({"message": "Atraso registrado com sucesso.", "registro": novo}), 201
    except ValueError as erro:
        return jsonify({"error": str(erro)}), 400
    except Exception as erro:
        return erro_banco(erro)


def carregar_dados():
    return pd.read_csv(DATA, encoding="utf-8", parse_dates=["data_registro"])


def resposta_factual(pergunta, df):
    texto = pergunta.lower()
    maximo = df["minutos_atraso"].max()

    if "maior atraso" in texto and ("qual linha" in texto or "qual ônibus" in texto or "qual onibus" in texto):
        linhas = (
            df.groupby(["codigo_linha", "nome_linha"], as_index=False)
              .agg(maior_atraso=("minutos_atraso", "max"))
        )
        maiores = linhas[linhas["maior_atraso"] == maximo].sort_values("codigo_linha")
        nomes = [f"{r.codigo_linha} - {r.nome_linha}" for r in maiores.itertuples()]
        return f"O maior atraso registrado foi de {int(maximo)} minutos. Houve empate entre: " + "; ".join(nomes) + "."

    if "maior atraso" in texto:
        return f"O maior atraso registrado foi de {int(maximo)} minutos."
    if "quantos registros" in texto or "quantidade de registros" in texto:
        return f"A massa de teste possui {len(df)} registros."
    if "atraso médio" in texto or "atraso medio" in texto or "média de atraso" in texto or "media de atraso" in texto:
        return f"O atraso médio da massa de teste é de {df['minutos_atraso'].mean():.2f} minutos."
    return None


def gerar_resposta(pergunta):
    df = carregar_dados()
    fato = resposta_factual(pergunta, df)
    if fato:
        return fato

    linhas = (
        df.groupby(["codigo_linha", "nome_linha"], as_index=False)
          .agg(registros=("minutos_atraso", "count"),
               atraso_medio=("minutos_atraso", "mean"),
               maior_atraso=("minutos_atraso", "max"))
    )
    linhas["atraso_medio"] = linhas["atraso_medio"].round(2)

    contexto = f"""
FONTE: massa sintética acadêmica do TransUrban. Não representa tempo real.
Total: {len(df)}
Atraso médio: {df['minutos_atraso'].mean():.2f}
Maior atraso: {df['minutos_atraso'].max():.0f}
Menor atraso: {df['minutos_atraso'].min():.0f}
Linhas:
{linhas.to_csv(index=False)}
"""

    resposta = chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Você é o assistente do TransUrban. Responda em português do Brasil, use somente o contexto, não invente dados e deixe claro que os dados são acadêmicos."},
            {"role": "user", "content": f"CONTEXTO:\n{contexto}\nPERGUNTA:\n{pergunta}"}
        ],
        options={"temperature": 0, "num_predict": 160}
    )
    return resposta.message.content


@app.post("/api/chat")
def api_chat():
    dados = request.get_json(silent=True) or {}
    pergunta = str(dados.get("message", "")).strip()
    if not pergunta:
        return jsonify({"error": "Digite uma pergunta."}), 400
    try:
        return jsonify({"answer": gerar_resposta(pergunta)})
    except Exception as erro:
        return jsonify({"error": f"Erro ao consultar a IA: {erro}"}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
