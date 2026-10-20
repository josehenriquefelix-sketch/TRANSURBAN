"""Confere a entrega em banco descartável, sem ler .env ou usar Supabase."""
import argparse
from datetime import datetime, timezone
import hashlib
from importlib.metadata import PackageNotFoundError, version
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
from urllib.error import URLError
from urllib.request import ProxyHandler, Request, build_opener, urlopen

ROOT = Path(__file__).resolve().parent


def diagnosticar(internet=False):
    report = {"executado_em_utc": datetime.now(timezone.utc).isoformat(),
              "verificacoes": [], "internet_testada": internet,
              "observacao": "Não comprova GPS físico, projetor, Windows ou conexão Supabase."}

    def check(nome, ok, detalhe):
        report["verificacoes"].append({"nome": nome, "ok": bool(ok), "detalhe": detalhe})
        print(f"{'OK' if ok else 'FALHA'} — {nome}: {detalhe}", flush=True)

    check("Python", sys.version_info[:2] == (3, 12),
          f"{sys.version_info.major}.{sys.version_info.minor}; esta entrega foi validada em 3.12")
    missing = []
    for package in ["fastapi", "uvicorn", "SQLAlchemy", "psycopg2-binary", "pydantic",
                    "python-dotenv", "pandas", "numpy"]:
        try:
            version(package)
        except PackageNotFoundError:
            missing.append(package)
    check("Dependências", not missing, "instaladas" if not missing else ", ".join(missing))
    try:
        base = ROOT / "web/vendor/leaflet"
        manifest = json.loads((base / "ORIGEM.json").read_text(encoding="utf-8"))
        intact = all(hashlib.sha256((base / name).read_bytes()).hexdigest() == digest
                     for name, digest in manifest["arquivos"].items())
        check("Biblioteca do mapa", intact, "hashes dos arquivos locais conferidos")
    except (OSError, ValueError, KeyError):
        check("Biblioteca do mapa", False, "faltam arquivos ou manifesto válido")

    if not missing:
        with tempfile.TemporaryDirectory(prefix="transurban-diagnostico-") as tmp:
            with socket.socket() as sock:
                sock.bind(("127.0.0.1", 0))
                port = sock.getsockname()[1]
            env = os.environ.copy()
            env.update(DATABASE_URL="sqlite:///" + (Path(tmp) / "teste.db").as_posix(),
                       TRANSURBAN_APRESENTACAO="1", CSV_PATH=str(ROOT / "data/atrasos_analise.csv"))
            local = build_opener(ProxyHandler({}))
            with (Path(tmp) / "servidor.log").open("w", encoding="utf-8") as log:
                process = subprocess.Popen([sys.executable, "-m", "uvicorn", "main:app",
                                            "--host", "127.0.0.1", "--port", str(port)],
                                           cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
                try:
                    base_url = f"http://127.0.0.1:{port}"
                    for _ in range(150):
                        if process.poll() is not None:
                            raise RuntimeError("Inicialização interrompida; execute --testar para diagnóstico detalhado.")
                        try:
                            with local.open(base_url + "/health", timeout=1) as response:
                                health = json.load(response)
                            break
                        except URLError:
                            time.sleep(.1)
                    else:
                        raise RuntimeError("O servidor não respondeu em tempo hábil.")
                    check("Banco de ensaio", health.get("banco") == "sqlite_local", "SQLite temporário; banco pessoal preservado")
                    for path in ["/docs", "/app/", "/app/app.js", "/app/styles.css"]:
                        with local.open(base_url + path, timeout=5) as response:
                            check(path, response.status == 200 and len(response.read()) > 0, "recurso recebido")
                    with local.open(base_url + "/ia/dados-publicos/resumo", timeout=15) as response:
                        data = json.load(response)
                    check("IA e integridade da fonte", data.get("registros_programacao") == 71086
                          and data.get("linhas_distintas") == 309 and data.get("atraso_medio_min") is None,
                          "programação histórica de Curitiba; sem inventar atraso medido")
                    with local.open(base_url + "/web-api/configuracao", timeout=5) as response:
                        config = json.load(response)
                    check("Carteira de demonstração", config.get("pagamentos_reais") is False,
                          "sem cobrança ou depósito real")
                except (OSError, ValueError, RuntimeError) as error:
                    check("Inicialização e consultas locais", False, type(error).__name__ + ": " + str(error))
                finally:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
    if internet:
        # URLs públicas fixas: nenhuma credencial ou configuração privada é enviada.
        services = {
            "Clima": "https://api.open-meteo.com/v1/forecast?latitude=-23.42&longitude=-51.93&current=temperature_2m",
            "Traçado de ruas": "https://router.project-osrm.org/route/v1/driving/-51.93,-23.42;-51.92,-23.43?overview=false",
            "Imagem do mapa": "https://tile.openstreetmap.org/13/2914/4644.png",
        }
        for name, url in services.items():
            try:
                request = Request(url, headers={"User-Agent": "TRANSURBAN-academic-readiness/1.0 (github.com/josehenriquefelix-sketch/TRANSURBAN)"})
                with urlopen(request, timeout=10) as response:
                    body = response.read()
                    if name == "Imagem do mapa":
                        ok = body.startswith(b"\x89PNG\r\n\x1a\n")
                    else:
                        payload = json.loads(body)
                        ok = "current" in payload if name == "Clima" else payload.get("code") == "Ok"
                    check(name, ok, "resposta real recebida com validação TLS ativa")
            except (OSError, ValueError) as error:
                check(name, False, type(error).__name__ + "; confira rede ou disponibilidade do serviço")
    report["aprovado"] = all(item["ok"] for item in report["verificacoes"])
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--internet", action="store_true", help="Também consulta clima, vias e uma imagem do mapa.")
    parser.add_argument("--saida", type=Path, help="Grava relatório em arquivo novo; não sobrescreve existentes.")
    args = parser.parse_args()
    report = diagnosticar(args.internet)
    if args.saida:
        with args.saida.open("x", encoding="utf-8") as output:
            json.dump(report, output, ensure_ascii=False, indent=2)
    print("Diagnóstico aprovado." if report["aprovado"] else "Há pendências; confira as linhas FALHA.")
    return 0 if report["aprovado"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
