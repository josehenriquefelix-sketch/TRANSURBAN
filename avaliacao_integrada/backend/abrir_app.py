"""Abre a aplicação local como um único serviço e aguarda a API ficar pronta."""
from __future__ import annotations

import json
import socket
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent.parent
HOST = "127.0.0.1"
PORT = 8000
URL = f"http://{HOST}:{PORT}/"


def porta_aberta() -> bool:
    try:
        with socket.create_connection((HOST, PORT), timeout=0.4):
            return True
    except OSError:
        return False


def servico_transurban_ativo() -> bool:
    try:
        with urlopen(f"http://{HOST}:{PORT}/health", timeout=1) as resposta:
            return json.load(resposta).get("projeto") == "TRANSURBAN"
    except (OSError, ValueError):
        return False


def main() -> int:
    if porta_aberta():
        if servico_transurban_ativo():
            webbrowser.open(URL)
            print("TRANSURBAN ja estava ativo; a pagina foi aberta.")
            return 0
        print(f"A porta {PORT} ja esta em uso por outro programa. Feche-o e tente novamente.")
        input("Pressione Enter para fechar...")
        return 1

    flags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", HOST, "--port", str(PORT)],
        cwd=ROOT,
        creationflags=flags,
    )
    deadline = time.monotonic() + 45
    while time.monotonic() < deadline:
        if server.poll() is not None:
            print("A API encerrou antes de ficar pronta. Confira a janela TRANSURBAN para ver o erro.")
            input("Pressione Enter para fechar...")
            return 1
        if servico_transurban_ativo():
            webbrowser.open(URL)
            print("TRANSURBAN aberto no navegador. Mantenha a janela da API aberta.")
            return 0
        time.sleep(0.4)

    print("A API demorou demais para iniciar. Confira a janela TRANSURBAN para ver o erro.")
    input("Pressione Enter para fechar...")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

