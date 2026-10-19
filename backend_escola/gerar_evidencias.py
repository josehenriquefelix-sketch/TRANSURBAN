"""Executa HTTP real em SQLite descartável; nunca usa o banco configurado."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time

import httpx
import analise

ROOT = Path(__file__).resolve().parent

def executar(destino):
    destino.mkdir(parents=True, exist_ok=False)
    report = {"executado_em_utc": datetime.now(timezone.utc).isoformat(),
              "ambiente": "Execução local de validação; não comprova execução na escola nem Supabase.",
              "banco": "SQLite temporário descartável", "concluido": False, "resultados": []}
    with tempfile.TemporaryDirectory() as tmp:
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        env = os.environ.copy()
        env["DATABASE_URL"] = "sqlite:///" + str(Path(tmp) / "teste.db")
        env["CSV_PATH"] = str(analise.DEFAULT_CSV)
        with (destino / "servidor.log").open("w") as log:
            proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", str(port)], cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
            try:
                with httpx.Client(base_url=f"http://127.0.0.1:{port}", trust_env=False, timeout=10) as client:
                    for _ in range(200):
                        if proc.poll() is not None:
                            raise RuntimeError("Servidor não iniciou; confira servidor.log.")
                        try:
                            if client.get("/health").status_code == 200:
                                break
                        except httpx.HTTPError:
                            pass
                        time.sleep(0.1)
                    else:
                        raise RuntimeError("Tempo limite para iniciar a API.")
                    def request(method, path, expected, body=None):
                        r = client.request(method, path, json=body) if body is not None else client.request(method, path)
                        payload = r.json() if "application/json" in r.headers.get("content-type", "") else {"bytes": len(r.content)}
                        report["resultados"].append({"metodo": method, "rota": path, "status": r.status_code, "esperado": expected, "entrada": body, "resposta": payload})
                        assert r.status_code == expected, (path, r.status_code)
                        return payload
                    request("GET", "/docs", 200)
                    request("GET", "/painel/", 200)
                    assert request("GET", "/health", 200)["banco"] == "sqlite_local"
                    city = request("POST", "/cidades", 201, {"nome": "Sarandi"})
                    line = request("POST", "/linhas", 201, {"id_cidade": city["id_cidade"], "codigo": "DEMO-20", "nome": "Linha acadêmica"})
                    assert line["cidade"] == city["nome"]
                    assert request("GET", "/cidades", 200) == [city]
                    assert request("GET", "/linhas", 200) == [line]
                    request("POST", "/linhas", 404, {"id_cidade": 999999, "codigo": "ERRO", "nome": "Teste"})
                    assert request("GET", "/linhas", 200) == [line]
                    request("POST", "/cidades", 422, {"nome": "   "})
                    for route, name in [("/ia/resumo", "resumo"), ("/ia/qualidade", "qualidade"), ("/ia/agrupamentos/linha", "linhas"), ("/ia/agrupamentos/data", "datas")]:
                        payload = request("GET", route, 200)
                        if name == "resumo":
                            assert payload["observacoes_validas"] == 180
                            assert payload["atraso_total_min_observacoes"] == 1362
                            assert payload["atraso_mediano_min"] == 8
                        (destino / (name + ".json")).write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False))
                    request("GET", "/ia/maiores-atrasos", 200)
                    request("GET", "/ia/agrupamentos/invalido", 422)
                    for route, name in [
                        ("/ia/dados-publicos/fonte", "publico-fonte"),
                        ("/ia/dados-publicos/qualidade", "publico-qualidade"),
                        ("/ia/dados-publicos/resumo", "publico-resumo"),
                        ("/ia/dados-publicos/agrupamentos/linha", "publico-linhas"),
                        ("/ia/dados-publicos/agrupamentos/servico", "publico-servicos"),
                    ]:
                        payload = request("GET", route, 200)
                        if name == "publico-resumo":
                            assert payload["registros_programacao"] == 71086
                            assert payload["linhas_distintas"] == 309
                            assert payload["atraso_medio_min"] is None
                        (destino / (name + ".json")).write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False))
                    report["concluido"] = True
            finally:
                proc.terminate()
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()
                (destino / "http.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
    print(f'{len(report["resultados"])} requisições verificadas. Evidências em {destino}. Servidor de teste encerrado.')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dest", type=Path, default=ROOT / "evidencias" / datetime.now(timezone.utc).strftime("execucao-%Y%m%d-%H%M%S-%f"))
    executar(parser.parse_args().dest)
