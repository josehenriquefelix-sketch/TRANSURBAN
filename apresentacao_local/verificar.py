"""Testes HTTP reais em banco temporário, sem alterar os cadastros da apresentação."""
import csv, json, os, socket, sqlite3, statistics, subprocess, sys, tempfile, time
from contextlib import closing
import urllib.request, urllib.error
from pathlib import Path

BASE=Path(__file__).resolve().parent
checks=[]
def check(cond, desc):
    if not cond: raise AssertionError(desc)
    checks.append(desc)

def main():
    with tempfile.TemporaryDirectory(dir=BASE) as temp:
        db=Path(temp)/'teste.sqlite3'
        with socket.socket() as sock:
            sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
        url=f'http://127.0.0.1:{port}'
        env={**os.environ,'TRANSURBAN_DB':str(db),'PYTHONIOENCODING':'utf-8',
             'PYTHONPATH':str(Path(sys.prefix)/'Lib'/'site-packages') if os.name=='nt' else os.environ.get('PYTHONPATH','')}
        with open(Path(temp)/'teste.log','w',encoding='utf-8') as log:
            interpreter=getattr(sys,'_base_executable',sys.executable) if os.name=='nt' else sys.executable
            proc=subprocess.Popen([interpreter,'-m','uvicorn','apresentacao:app','--host','127.0.0.1','--port',str(port)],cwd=BASE/'backend',env=env,stdout=log,stderr=log)
            def req(route,body=None):
                r=urllib.request.Request(url+route,data=json.dumps(body).encode() if body is not None else None,headers={'Content-Type':'application/json'})
                try:
                    with urllib.request.urlopen(r,timeout=5) as response:
                        raw=response.read();status=response.status
                except urllib.error.HTTPError as e:status=e.code;raw=e.read()
                try:return status,json.loads(raw)
                except ValueError:return status,raw.decode('utf-8')
            try:
                for _ in range(60):
                    try:
                        if req('/health')[0]==200:break
                    except OSError:pass
                    if proc.poll() is not None:raise RuntimeError('Servidor de teste encerrou.')
                    time.sleep(.2)
                else:raise RuntimeError('Servidor de teste não respondeu.')
                for route in ['/','/health','/docs','/openapi.json','/app/','/apresentacao','/console','/app/03-ROTEIRO.html','/app/04-DADOS-ACADEMICOS.html']:
                    check(req(route)[0]==200,'GET '+route+' retorna 200')
                check(req('/cidades')[1]==[],'Banco temporário inicia vazio')
                status,cidade=req('/cidades',{'nome':' Maringá '})
                check(status==201 and cidade['nome']=='Maringá','Cidade criada e espaços removidos')
                linha={'codigo':'010','nome':'Universidade (teste)','id_cidade':cidade['id_cidade']}
                status,record=req('/linhas',linha)
                check(status==201 and record['cidade']=='Maringá','Linha vinculada à cidade: 201')
                check(req('/linhas')[1]==[record],'Consulta devolve linha persistida')
                check(req('/linhas',{**linha,'id_cidade':999999})[0]==404,'Cidade inexistente: 404')
                for body in [{'nome':''},{'nome':'   '},{'nome':'a'*101},{}]:
                    check(req('/cidades',body)[0]==422,'Cidade inválida rejeitada: '+str(body)[:50])
                for body in [{**linha,'id_cidade':0},{**linha,'codigo':''},{**linha,'id_cidade':'abc'}]:
                    check(req('/linhas',body)[0]==422,'Linha inválida rejeitada: '+str(body))
                with closing(sqlite3.connect(db)) as conn:
                    conn.execute('PRAGMA foreign_keys=ON')
                    try:conn.execute("INSERT INTO linha_onibus(codigo,nome,id_cidade) VALUES ('X','Teste',999999)")
                    except sqlite3.IntegrityError:check(True,'Banco rejeita FK inválida diretamente')
                    else:check(False,'Banco rejeita FK inválida diretamente')
                rows=list(csv.DictReader((BASE/'dados'/'atrasos.csv').open(encoding='utf-8-sig')))
                atrasos=[int(r['minutos_atraso']) for r in rows]
                resumo=req('/ia/resumo')[1]
                check(resumo['registros']==len(rows),'Contagem da API coincide com CSV')
                check(resumo['atraso_medio_min']==round(statistics.mean(atrasos),2),'Média conferida independentemente')
                check(resumo['mediana_atraso_min']==statistics.median(atrasos),'Mediana conferida independentemente')
                check(req('/ia/fonte')[1]['telemetria_real'] is False,'Fonte identifica dados sintéticos')
                qualidade=req('/ia/qualidade')[1]
                check(qualidade['registros']==len(rows) and qualidade['datas_invalidas']==0,'Qualidade e datas conferidas')
                for campo in ['cidade','periodo','condicao_transito','clima','codigo_linha']:
                    grupos=req('/ia/agrupamentos/'+campo)[1]['grupos']
                    check(sum(r['registros'] for r in grupos)==len(rows),'Agrupamento preserva total: '+campo)
                check(req('/ia/agrupamentos/indevido')[0]==422,'Agrupamento desconhecido rejeitado')
                for arquivo in ['assistir-videoaula.html','videoaula.vtt','GUIA-DA-EQUIPE.md']:
                    check(req('/material/'+arquivo)[0]==200,'Material acessível: '+arquivo)
                check(req('/material/apresentacao.sqlite3')[0]==404,'Rota de material não expõe o banco')
                with urllib.request.urlopen(urllib.request.Request(url+'/material/videoaula.mp4',headers={'Range':'bytes=0-1023'})) as video:
                    check(video.status==206,'MP4 aceita requisição parcial para reprodução')
                    check(len(video.read())==1024,'Trecho MP4 possui tamanho esperado')
                relatorio={'verificacoes_aprovadas':len(checks),'banco':'temporário isolado','resumo_conferido':resumo,'qualidade':qualidade,'verificacoes':checks}
                (BASE/'EVIDENCIAS-TESTES.json').write_text(json.dumps(relatorio,ensure_ascii=False,indent=2),encoding='utf-8')
                print(json.dumps(relatorio,ensure_ascii=False,indent=2))
            finally:
                proc.terminate();proc.wait(timeout=10)

if __name__=='__main__':main()
