"""Conferência de leitura para executar no computador do evento."""
import importlib
import json
import logging
import sys
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

falhas = []


def resultado(nome, aprovado, orientacao=""):
    print(f"[{'OK' if aprovado else 'FALHA'}] {nome}")
    if not aprovado:
        falhas.append(nome)
        if orientacao:
            print(f"        {orientacao}")


def main():
    print("TRANSURBAN - Conferencia do ambiente\n")
    resultado("Python 3.10 ou superior", sys.version_info >= (3, 10))
    for modulo in ("fastapi", "uvicorn", "pandas", "dotenv", "supabase", "httpx", "tzdata"):
        try:
            importlib.import_module(modulo)
            resultado(f"Dependencia {modulo}", True)
        except ImportError:
            resultado(f"Dependencia {modulo}", False, "Execute INICIAR_TRANSURBAN.cmd para preparar o ambiente.")
    if falhas:
        return 1

    logging.disable(logging.CRITICAL)
    from backend.analise import carregar
    from backend.database import get_supabase, supabase_configurado

    configurado = supabase_configurado()
    resultado("Configuracao privada do Supabase", configurado,
              "Preencha backend/.env com a URL e a chave do projeto da equipe.")
    if configurado:
        tabelas = {
            "cidade": "id_cidade",
            "linha_onibus": "id_linha",
            "tu_perfil": "usuario_id",
            "tu_carteira": "numero",
            "tu_trajeto": "id",
            "tu_horario": "id",
            "tu_avaliacao": "id",
            "tu_recarga": "id",
            "tu_acesso": "usuario_id",
            "tu_motorista": "usuario_id",
            "tu_favorito": "usuario_id",
            "tu_viagem_operacional": "id",
            "tu_posicao_atual": "viagem_id",
            "tu_manifestacao": "id",
            "tu_manifestacao_evento": "id",
        }
        for tabela, coluna in tabelas.items():
            try:
                get_supabase().table(tabela).select(coluna).limit(1).execute()
                resultado(f"Supabase / tabela {tabela}", True)
            except Exception:
                resultado(f"Supabase / tabela {tabela}", False,
                          "Confira a internet, a chave e as migracoes SQL. Use o mesmo projeto Supabase.")

    try:
        carregar()
        resultado("Base de analise interna em UTF-8", True)
    except Exception:
        resultado("Base de analise interna em UTF-8", False,
                  "Atualize o repositorio e confira data/atrasos_analise.csv.")

    for rota in ("/", "/mobilidade.css", "/mobilidade.js", "/logo-mobilidade.svg", "/vendor/leaflet.js", "/docs", "/dados/docs", "/mobilidade/catalogo", "/mobilidade/viagens", "/portal/contexto"):
        try:
            with urlopen(f"http://127.0.0.1:8000{rota}", timeout=10) as resposta:
                resultado(f"Site e API {rota}", resposta.status == 200)
        except (OSError, URLError):
            resultado(f"Site e API {rota}", False,
                      "Abra INICIAR_TRANSURBAN.cmd e mantenha a janela do servidor aberta.")
    try:
        with urlopen("http://127.0.0.1:8000/openapi.json", timeout=10) as resposta:
            esquema = json.load(resposta)
        resultado("Documentacao de DS separada de Ciencia de Dados",
                  "/auth/login" in esquema["paths"] and not any(p.startswith("/ia/") for p in esquema["paths"]))
    except (OSError, ValueError, KeyError):
        resultado("Documentacao da versao atual", False,
                  "Feche uma instancia antiga do servidor com Ctrl+C e inicie novamente.")
    try:
        urlopen("http://127.0.0.1:8000/backend/.env", timeout=10).close()
        resultado("Arquivo privado protegido no servidor", False)
    except HTTPError as erro:
        resultado("Arquivo privado protegido no servidor", erro.code == 404)
    except OSError:
        resultado("Arquivo privado protegido no servidor", False, "Inicie o servidor para conferir.")

    print()
    if falhas:
        print(f"Foram encontradas {len(falhas)} pendencias. Confira as orientacoes acima.")
        return 1
    print("As verificacoes deste computador passaram.")
    print("Confira tambem login, navegacao e acesso a internet no local do evento.")
    print("Esta checagem nao confirma integracao com GPS, pagamentos ou bilhetagem real.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
