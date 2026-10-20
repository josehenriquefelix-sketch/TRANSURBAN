"""Testa por HTTP as etapas DS e IA do roteiro. Não acessa o frontend."""
import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.request import ProxyHandler, Request, build_opener
from uuid import uuid4


class TestesRoteiro:
    def __init__(self, porta):
        self.base = f"http://127.0.0.1:{porta}"
        self.http = build_opener(ProxyHandler({}))
        self.report = {"executado_em_utc": datetime.now(timezone.utc).isoformat(),
                       "servidor": self.base, "frontend_testado": False,
                       "concluido": False, "requisicoes": []}

    @staticmethod
    def conferir(condicao, mensagem):
        if not condicao:
            raise ValueError(mensagem)

    def pedir(self, metodo, rota, esperado=200, entrada=None):
        body = None if entrada is None else json.dumps(entrada).encode("utf-8")
        request = Request(self.base + rota, data=body, method=metodo,
                          headers={"Accept": "application/json", "Content-Type": "application/json"})
        try:
            response = self.http.open(request, timeout=20)
        except HTTPError as error:
            response = error  # 404/422 também são resultados esperados do roteiro.
        with response:
            status = response.code
            payload = json.loads(response.read().decode("utf-8"))
        self.report["requisicoes"].append({"metodo": metodo, "rota": rota,
            "status": status, "esperado": esperado, "entrada": entrada, "resposta": payload})
        self.conferir(status == esperado,
                      f"{metodo} {rota}: esperado {esperado}, recebido {status}.")
        print(f"OK — {metodo} {rota}: {status} (esperado)", flush=True)
        return payload

    def saude(self):
        health = self.pedir("GET", "/health")
        self.conferir(health.get("status") == "ok", "A API não informou status ok.")
        print("Banco informado pela API:", health.get("banco"), flush=True)
        return health

    def ds(self, health):
        self.conferir(health.get("banco") == "sqlite_local",
                      "DS interrompido: este ensaio cria registros e exige SQLite local. "
                      "Inicie a API com iniciar_apresentacao.py; não altera Supabase.")
        print("\nDS — cria cadastros de demonstração; não apaga dados.", flush=True)
        city = self.pedir("POST", "/cidades", 201, {"nome": "Sarandi"})
        self.conferir(city.get("nome") == "Sarandi" and type(city.get("id_cidade")) is int,
                      "Resposta de cidade incompatível com o roteiro.")
        code = "DEMO-20-" + uuid4().hex[:6]
        line = self.pedir("POST", "/linhas", 201,
                         {"codigo": code, "nome": "Linha da apresentação", "id_cidade": city["id_cidade"]})
        self.conferir(line.get("cidade") == "Sarandi" and line.get("id_cidade") == city["id_cidade"]
                      and line.get("codigo") == code, "O relacionamento cidade/linha não confere.")
        cities = self.pedir("GET", "/cidades")
        lines = self.pedir("GET", "/linhas")
        self.conferir(city in cities and line in lines, "O cadastro não apareceu na consulta.")
        ids_city = {x["id_cidade"] for x in cities}
        absent = 999999
        while absent in ids_city:
            absent += 1
        rejected = self.pedir("POST", "/linhas", 404,
                             {"codigo": "ERRO-" + uuid4().hex[:6], "nome": "Tentativa inválida", "id_cidade": absent})
        self.conferir(rejected.get("detail") == "Cidade não encontrada", "Mensagem do 404 diferente da esperada.")
        after = self.pedir("GET", "/linhas")
        self.conferir({x["id_linha"] for x in after} == {x["id_linha"] for x in lines},
                      "A lista de linhas mudou durante o teste da referência inválida.")
        invalid = self.pedir("POST", "/cidades", 422, {"nome": "   "})
        self.conferir(any(x.get("loc") == ["body", "nome"] for x in invalid.get("detail", [])),
                      "A resposta 422 não identificou o campo nome.")
        after_cities = self.pedir("GET", "/cidades")
        self.conferir({x["id_cidade"] for x in after_cities} == ids_city,
                      "A lista de cidades mudou durante o teste do nome vazio.")
        self.report["ds"] = {"id_cidade_criado": city["id_cidade"], "id_linha_criado": line["id_linha"],
                             "codigo_demonstracao": code, "relacionamento_conferido": True,
                             "validacoes_404_422_conferidas": True}
        print(f"DS aprovado. Cidade ID {city['id_cidade']}; linha ID {line['id_linha']}; código {code}.", flush=True)
        print("Persistência: após reiniciar a API, consulte GET /linhas e procure esse ID. "
              "Este script não encerra o servidor.", flush=True)

    def ia(self):
        print("\nIA — somente leitura do CSV público histórico de Curitiba.", flush=True)
        source = self.pedir("GET", "/ia/dados-publicos/fonte")
        self.conferir(source.get("cidade") == "Curitiba" and source.get("feed_oficial") is False,
                      "Fonte diferente da base comunitária histórica do roteiro.")
        quality = self.pedir("GET", "/ia/dados-publicos/qualidade")
        self.conferir(quality.get("apta_para_calculos_do_snapshot") is True
                      and quality.get("hash_csv_confere") is True
                      and quality.get("hashes_originais_conferem") is True,
                      "A auditoria da fonte não foi aprovada.")
        summary = self.pedir("GET", "/ia/dados-publicos/resumo")
        self.conferir(summary.get("sha256") == quality.get("sha256") == source.get("csv_sha256"),
                      "As consultas não identificam o mesmo arquivo CSV.")
        self.conferir(summary.get("registros_programacao") == 71086 and summary.get("linhas_distintas") == 309,
                      "Contagens diferentes do snapshot usado no roteiro.")
        mean = summary.get("media_registros_programacao_por_linha")
        self.conferir(isinstance(mean, (int, float)) and math.isclose(mean, 230.0518, abs_tol=.00001)
                      and summary.get("mediana_registros_programacao_por_linha") == 162,
                      "Média ou mediana diferente do snapshot do roteiro.")
        self.conferir(summary.get("atraso_medio_min") is None and summary.get("viagens_realizadas") is None,
                      "Esta fonte não comprova atraso ou viagens realizadas.")
        for dimension in ["linha", "servico"]:
            group = self.pedir("GET", "/ia/dados-publicos/agrupamentos/" + dimension + "?limite=5")
            rows = group.get("resultados", [])
            self.conferir(group.get("soma_registros_nos_grupos") == 71086
                          and group.get("grupos_exibidos") == len(rows) == min(5, group["total_grupos"])
                          and group.get("soma_registros_dos_grupos_exibidos") == sum(x["registros_programacao"] for x in rows),
                          "Totais completos ou exibidos do agrupamento não conferem.")
        self.report["ia"] = {"registros_programacao": 71086, "linhas_distintas": 309,
                             "media_registros_por_linha": mean, "mediana_registros_por_linha": 162,
                             "natureza": "programação comunitária histórica de Curitiba; não é atraso medido"}
        print("IA aprovada: 71.086 registros; 309 códigos; média 230,0518; mediana 162.", flush=True)
        print("São registros de programação, não passageiros ou viagens comprovadamente realizadas. "
              "Atraso médio null significa indisponível, não zero.", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--ds", action="store_true")
    modes.add_argument("--ia", action="store_true")
    modes.add_argument("--tudo", action="store_true")
    parser.add_argument("--porta", type=int, default=8000)
    parser.add_argument("--salvar", type=Path, help="Relatório JSON em arquivo novo, sem sobrescrever.")
    args = parser.parse_args()
    if not 1 <= args.porta <= 65535:
        parser.error("Porta deve estar entre 1 e 65535.")
    if args.salvar and (args.salvar.exists() or not args.salvar.parent.is_dir()):
        parser.error("Escolha arquivo de saída novo em uma pasta existente.")
    tests = TestesRoteiro(args.porta)
    try:
        health = tests.saude()
        if args.ds or args.tudo:
            tests.ds(health)
        if args.ia or args.tudo:
            tests.ia()
        tests.report["concluido"] = True
    except (OSError, URLError, ValueError, KeyError, TypeError) as error:
        message = ("Não foi possível consultar a API. Deixe iniciar_apresentacao.py aberto "
                   "em outro terminal e confira a porta." if isinstance(error, (OSError, URLError)) else str(error))
        tests.report["falha"] = message
        print("FALHA — " + message, file=sys.stderr)
    if args.salvar:
        with args.salvar.open("x", encoding="utf-8") as out:
            json.dump(tests.report, out, ensure_ascii=False, indent=2)
    return 0 if tests.report["concluido"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
