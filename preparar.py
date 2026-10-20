"""Cria o ambiente reproduzível sem sobrescrever a configuração privada."""
from pathlib import Path
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def main():
    if sys.version_info[:2] != (3, 13):
        raise SystemExit("Use Python 3.13: python preparar.py. Confira antes com python --version.")
    backend = ROOT / "backend"
    env = backend / ".venv"
    python = env / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    cache = ROOT / ".cache-install"
    cache.mkdir(exist_ok=True)
    install_env = dict(os.environ, TEMP=str(cache), TMP=str(cache), PIP_DISABLE_PIP_VERSION_CHECK="1")
    if not python.exists():
        subprocess.run([sys.executable, "-m", "venv", str(env)], check=True, env=install_env)
    subprocess.run([str(python), "-m", "pip", "install", "-r", str(backend / "requirements-test.lock.txt")], check=True, env=install_env)
    subprocess.run([str(python), "-m", "pip", "check"], check=True)
    target = backend / ".env"
    if not target.exists():
        shutil.copyfile(backend / ".env.example", target)
        print(".env criado para PostgreSQL local. Veja GUIA_AUDITORIO.md.")
    else:
        print(".env existente preservado.")
    print("Ambiente pronto. Configure/inicie o PostgreSQL antes da API e dos testes.")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError:
        raise SystemExit("A preparação não foi concluída. Confira o erro da instalação acima.")
