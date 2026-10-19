"""Preparação e apresentação local em Windows/Linux; não altera o .env."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--preparar", action="store_true")
    modes.add_argument("--testar", action="store_true")
    modes.add_argument("--evidencias", action="store_true")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("A porta deve estar entre 1 e 65535.")
    env_dir = ROOT / ".venv-apresentacao"
    python = env_dir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if args.preparar:
        if sys.version_info[:2] != (3, 12):
            print("Use Python 3.12 para reproduzir o ambiente validado.")
            return 1
        if env_dir.exists() and not python.is_file():
            print(".venv-apresentacao já existe e não é um ambiente válido. Arquivos preservados.")
            return 1
        if not python.is_file():
            venv.EnvBuilder(with_pip=True).create(env_dir)
        subprocess.run([str(python), "-m", "pip", "install", "-r", "requirements-dev.txt"], cwd=ROOT, check=True)
        print("Preparação concluída. Execute novamente com --testar e depois sem argumentos.")
        return 0
    if not python.is_file():
        print("Primeiro execute este arquivo com Python 3.12 e --preparar, com internet.")
        return 1
    env = os.environ.copy()
    env["DATABASE_URL"] = "sqlite:///" + (ROOT / "apresentacao_local.db").as_posix()
    env["CSV_PATH"] = str(ROOT / "data" / "atrasos_analise.csv")
    if args.testar:
        command = [str(python), "-m", "pytest", "-q"]
    elif args.evidencias:
        command = [str(python), "gerar_evidencias.py"]
    else:
        print("Apresentação com SQLite LOCAL. IA pública: snapshot histórico de Curitiba em /ia/dados-publicos. Não usa Supabase.", flush=True)
        print("A base sintética anterior continua separada em /ia; não representa atrasos reais.", flush=True)
        print("O .env existente é preservado. Deixe este terminal aberto; Ctrl+C encerra.", flush=True)
        print(f"No navegador deste notebook: http://127.0.0.1:{args.port}/docs", flush=True)
        command = [str(python), "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", str(args.port)]
    try:
        return subprocess.run(command, cwd=ROOT, env=env).returncode
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
