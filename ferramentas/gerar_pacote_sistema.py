"""Pacote independente somente da API/site e seus testes, sem apresentação/evidências."""
from pathlib import Path
import hashlib
import json
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'pacotes/TRANSURBAN-SOMENTE-API-E-SITE.zip'
PREFIX='TRANSURBAN_API_SITE/'
files={}
for name in subprocess.check_output(['git','ls-files','-z','backend_escola'],cwd=ROOT).decode().split('\0'):
    if not name:continue
    path=Path(name);rel=path.relative_to('backend_escola')
    allowed=(rel.parts[0] in {'data','web','frontend','swagger_static','sql'} or
             (len(rel.parts)==1 and (rel.suffix in {'.py','.cmd','.sh'} or rel.name in {'requirements.txt','requirements-dev.txt','.gitignore'})))
    if not allowed:continue
    if path.name=='.env' or path.suffix in {'.db','.pyc','.sqlite','.zip'} or (ROOT/path).is_symlink():raise ValueError(name)
    files[rel.as_posix()]=(ROOT/path).read_bytes()
files['COMECE_AQUI.txt']='''TRANSURBAN — SOMENTE API E SITE

Extraia o ZIP e abra a pasta TRANSURBAN_API_SITE no VS Code.
Ela contém main.py, as dependências, o site e os dados da análise IA.
Não há roteiros, slides, falas, documentos da apresentação ou evidências antigas.

Python 3.12 é necessário. Primeira instalação: internet.
WINDOWS: execute PREPARAR-WINDOWS.cmd; depois APRESENTAR-WINDOWS.cmd.
LINUX, terminal dentro desta pasta:
  python3 iniciar_apresentacao.py --preparar
  python3 iniciar_apresentacao.py --testar
  python3 iniciar_apresentacao.py --diagnostico
  python3 iniciar_apresentacao.py

Depois de Application startup complete, no navegador deste computador:
  API: http://127.0.0.1:8000/docs
  SITE: http://127.0.0.1:8000/app/
Deixe o terminal aberto. Ctrl+C encerra.

Usa banco SQLite local, criado ao iniciar. Não exige .env nem senha Supabase.
O banco pessoal e as contas de outro computador não são incluídos.
Use janela normal e anônima para testar passageiro e motorista separadamente.
Mapa, clima e cálculo de vias exigem internet; GPS exige permissão e sinal.
Itinerário oficial e frota não estão integrados; carteira e VT são demonstrações.
Os testes e diagnósticos são incluídos para conferir a instalação.
'''.encode('utf-8')
files['MANIFESTO_SHA256.json']=json.dumps({'codigo_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),'arquivos_sha256':{n:hashlib.sha256(b).hexdigest() for n,b in files.items()},'conteudo':'Somente sistema, dependências declaradas, dados e testes. Sem ambientes virtuais, banco pessoal, roteiros ou evidências prévias.'},ensure_ascii=False,indent=2).encode('utf-8')
with zipfile.ZipFile(DEST,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for name,body in sorted(files.items()):z.writestr(PREFIX+name,body)
with zipfile.ZipFile(DEST) as z:assert z.testzip() is None
DEST.with_suffix('.zip.sha256').write_text(hashlib.sha256(DEST.read_bytes()).hexdigest()+'  '+DEST.name+'\n')
print(f'{len(files)} arquivos; {DEST.stat().st_size/1024**2:.2f} MiB; integridade do ZIP conferida.')
