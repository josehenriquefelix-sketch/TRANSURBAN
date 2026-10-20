"""Inicia somente em loopback e abre site/API; não depende de Supabase."""
import json
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path

BASE = Path(__file__).resolve().parent
URL = 'http://127.0.0.1:8000'

def pronto():
    try:
        with urllib.request.urlopen(URL + '/health', timeout=2) as r:
            return json.load(r).get('banco') == 'SQLite local'
    except Exception:
        return False

if __name__ == '__main__':
    if not pronto():
        log = open(BASE / 'servidor.log', 'a', encoding='utf-8')
        proc = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'apresentacao:app', '--host', '127.0.0.1', '--port', '8000'],
                                cwd=BASE / 'backend', stdout=log, stderr=log,
                                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        (BASE / 'servidor.pid').write_text(str(proc.pid))
        for _ in range(40):
            if pronto():
                break
            if proc.poll() is not None:
                raise SystemExit('Servidor não iniciou. Consulte servidor.log nesta pasta.')
            time.sleep(.5)
        else:
            raise SystemExit('Tempo esgotado. Consulte servidor.log.')
    if '--sem-navegador' not in sys.argv:
        for pagina in ['/docs', '/app/', '/apresentacao']:
            webbrowser.open(URL + pagina)
    print('API: ' + URL + '/docs\nSite: ' + URL + '/app/\nPainel: ' + URL + '/apresentacao')
