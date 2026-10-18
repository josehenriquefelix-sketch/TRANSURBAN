"""Abre a API local e o navegador. Execute pelo ABRIR_TRANSURBAN.cmd."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.request import urlopen
import webbrowser
import uuid

ROOT = Path(__file__).resolve().parent

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--local',action='store_true')
    parser.add_argument('--sem-navegador',action='store_true')
    parser.add_argument('--verificar',action='store_true')
    parser.add_argument('--porta',type=int,default=8000)
    args=parser.parse_args()
    url=f'http://127.0.0.1:{args.porta}'
    env=os.environ.copy()
    instance=str(uuid.uuid4())
    env['TRANSURBAN_INSTANCIA']=instance
    local=args.local or not (ROOT/'.env').exists()
    env['TRANSURBAN_MODO']='local' if local else 'supabase'
    process=subprocess.Popen([sys.executable,'-m','uvicorn','main:app','--host','127.0.0.1','--port',str(args.porta)],cwd=ROOT,env=env)
    try:
        for _ in range(60):
            if process.poll() is not None:
                raise RuntimeError('A API não iniciou. Confira a mensagem acima e se a porta já está ocupada.')
            try:
                with urlopen(url+'/health',timeout=2) as r:
                    data=json.load(r)
                if data.get('status')=='ok' and data.get('instancia')==instance:break
            except Exception:
                time.sleep(.5)
        else:
            raise RuntimeError('A API não ficou disponível. Confira a conexão ou use ABRIR_MODO_LOCAL.cmd.')
        expected='sqlite' if local else 'postgresql'
        if data.get('banco')!=expected:
            raise RuntimeError('O banco ativo não corresponde ao modo escolhido. Confira se há outra API nessa porta.')
        print('\nTRANSURBAN PRONTO. Banco: '+data['banco'],flush=True)
        print('Painel: '+url+'/apresentacao',flush=True)
        if args.verificar:return
        if not args.sem_navegador:webbrowser.open(url+'/apresentacao')
        print('Mantenha esta janela aberta. Para encerrar, pressione Ctrl+C.',flush=True)
        process.wait()
    except KeyboardInterrupt:
        print('\nEncerrando a API.')
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=10)

if __name__=='__main__':
    try:main()
    except Exception as error:
        print('Não foi possível abrir a apresentação: '+str(error))
        sys.exit(1)
