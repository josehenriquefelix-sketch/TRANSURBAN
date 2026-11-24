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
REDE = "--rede" in sys.argv
PORT = 8000
BASE_URL = f"http://{HOST}:{PORT}"
CAMINHOS = {'passageiro':'/', 'motorista':'/motorista/', 'gestao':'/gestao/', 'dados':'/dados/'}
VERSAO = "2026.11.24-essencial"


def porta_aberta() -> bool:
    try:
        with socket.create_connection((HOST, PORT), timeout=0.4):
            return True
    except OSError:
        return False


def servico_transurban_ativo() -> bool:
    try:
        with urlopen(f"http://{HOST}:{PORT}/health", timeout=1) as resposta:
            estado = json.load(resposta)
            return estado.get("projeto") == "TRANSURBAN" and estado.get("versao") == VERSAO
    except (OSError, ValueError):
        return False


def aguardar_servidor(server: subprocess.Popen) -> int:
    try:
        return server.wait()
    except KeyboardInterrupt:
        if server.poll() is None:
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait()
        return 0


def mostrar_rede() -> None:
    """Mostra os endereços IPv4 locais; não publica o computador na internet."""
    try:
        enderecos = sorted({ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]
                            if not ip.startswith("127.") and ":" not in ip})
    except OSError:
        enderecos = []
    print("\nCELULAR: conecte no mesmo Wi-Fi do computador.", flush=True)
    for ip in enderecos:
        print(f"Abra no celular: http://{ip}:{PORT}/acessos.html", flush=True)
    if not enderecos:
        print("Não foi possível identificar o IP. Consulte o IPv4 da rede do computador.")
    print("Não feche esta janela. A rede da escola pode bloquear a comunicação entre aparelhos.")
    print("GPS e login Google no celular exigem endereço HTTPS válido; HTTP da rede serve para as telas e login por senha.\n", flush=True)


def servidor_disponivel_na_rede() -> bool:
    try:
        enderecos = socket.gethostbyname_ex(socket.gethostname())[2]
        for ip in enderecos:
            if ip.startswith("127.") or ":" in ip:
                continue
            try:
                with socket.create_connection((ip, PORT), timeout=0.5):
                    return True
            except OSError:
                continue
    except OSError:
        pass
    return False


def main() -> int:
    argumentos = [valor for valor in sys.argv[1:] if valor != '--rede']
    area = argumentos[0] if argumentos else 'passageiro'
    if area not in CAMINHOS:
        print('Escolha passageiro, motorista, gestao ou dados.')
        return 1
    url = BASE_URL + ("/acessos.html" if REDE else CAMINHOS[area])
    if REDE:
        mostrar_rede()
    if porta_aberta():
        if servico_transurban_ativo():
            if REDE and not servidor_disponivel_na_rede():
                print("A API atual não está acessível na rede. Encerre a execução anterior e abra novamente ABRIR_NO_CELULAR.cmd.")
                return 1
            webbrowser.open(url)
            print("TRANSURBAN ja estava ativo; a pagina foi aberta.")
            return 0
        print(f"A porta {PORT} esta ocupada por uma instancia antiga ou outro programa. Feche a janela antiga com Ctrl+C e tente novamente.")
        input("Pressione Enter para fechar...")
        return 1

    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0" if REDE else HOST, "--port", str(PORT)],
        cwd=ROOT,
    )
    deadline = time.monotonic() + 45
    while time.monotonic() < deadline:
        if server.poll() is not None:
            print("A API encerrou antes de ficar pronta. Confira a mensagem acima para ver o erro.")
            input("Pressione Enter para fechar...")
            return 1
        if servico_transurban_ativo():
            webbrowser.open(url)
            print("TRANSURBAN local aberto. Mantenha este servidor ativo enquanto usa os portais.")
            return aguardar_servidor(server)
        time.sleep(0.4)

    if server.poll() is None:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait()
    print("A API demorou demais para iniciar. Confira a mensagem acima para ver o erro.")
    input("Pressione Enter para fechar...")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
