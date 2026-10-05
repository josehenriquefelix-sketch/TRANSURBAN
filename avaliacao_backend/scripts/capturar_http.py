"""Executa HTTP real em banco descartável e guarda provas sem credenciais."""
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone

import httpx

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'evidencias' / 'http'

def executar():
    DEST.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
        env = os.environ.copy()
        env['DATABASE_URL'] = 'sqlite:///' + str(Path(tmp) / 'teste.db').replace('\\', '/')
        env['CSV_PATH'] = str(ROOT / 'data' / 'atrasos_analise.csv')
        evidencia = {'executado_em_utc': datetime.now(timezone.utc).isoformat(),
                     'banco': 'SQLite temporário; não Supabase', 'resultados': []}
        with (DEST / 'servidor.log').open('w', encoding='utf-8') as log:
            proc = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'backend.main:app',
                                     '--host', '127.0.0.1', '--port', str(port)],
                                    cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
            try:
                with httpx.Client(base_url=f'http://127.0.0.1:{port}', timeout=10, trust_env=False) as client:
                    for _ in range(100):
                        if proc.poll() is not None:
                            raise RuntimeError('Servidor encerrou antes de iniciar; confira servidor.log')
                        try:
                            if client.get('/health').status_code == 200: break
                        except httpx.HTTPError:
                            pass
                        time.sleep(0.1)
                    else:
                        raise RuntimeError('Tempo limite para iniciar o servidor')

                    def request(method, path, esperado, body=None):
                        response = client.request(method, path, json=body) if body is not None else client.request(method, path)
                        try:
                            saida = response.json()
                        except ValueError:
                            saida = {'tipo': response.headers.get('content-type'), 'bytes': len(response.content)}
                        evidencia['resultados'].append({'metodo': method, 'rota': path, 'entrada': body,
                                                       'status': response.status_code, 'esperado': esperado, 'resposta': saida})
                        assert response.status_code == esperado, (path, response.status_code, saida)
                        return saida

                    request('GET', '/docs', 200)
                    request('GET', '/health', 200)
                    cidade = request('POST', '/cidades', 201, {'nome': 'Maringá'})
                    request('GET', '/cidades', 200)
                    linha = request('POST', '/linhas', 201, {'id_cidade': cidade['id_cidade'], 'codigo': '001', 'nome': 'Linha acadêmica'})
                    assert linha['cidade'] == 'Maringá'
                    assert request('GET', '/linhas', 200) == [linha]
                    request('POST', '/linhas', 404, {'id_cidade': 999999, 'codigo': 'X', 'nome': 'Teste'})
                    request('POST', '/cidades', 409, {'nome': 'Maringá'})
                    request('POST', '/cidades', 422, {'nome': ' '})
                    for path in ['/ia/resumo', '/ia/qualidade', '/ia/maiores-atrasos']:
                        request('GET', path, 200)
                    for dim in ['linha', 'cidade', 'data', 'periodo', 'transito', 'clima', 'trecho']:
                        request('GET', '/ia/agrupamentos/' + dim, 200)
                    request('GET', '/ia/agrupamentos/invalido', 422)
                evidencia['concluido'] = True
            except Exception as exc:
                evidencia['concluido'] = False
                evidencia['erro'] = str(exc)
                raise
            finally:
                proc.terminate()
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()
                (DEST / 'respostas_http.json').write_text(json.dumps(evidencia, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
        print(f'{len(evidencia["resultados"])} requisições verificadas; servidor encerrado.')

if __name__ == '__main__':
    executar()
