"""Fluxos reais de banco do site. Serviços externos são simulados somente nos testes."""
import json
import os
from io import BytesIO
from uuid import uuid4
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
os.environ.setdefault('DATABASE_URL','sqlite://')
from database import Base
from main import app
import web_api as web
from models_web import ContaWeb, SessaoWeb, ViagemWeb

ORIGIN={'origin':'http://testserver'}
PASS=' SenhaTeste123! '
def post(client,path,data=None):return client.post('/web-api/'+path,json=data or {},headers=ORIGIN)
def signup(client,role,name):
    return post(client,'contas',{'nome':name,'email':name.lower()+'@exemplo.com','senha':PASS,'perfil':role})

@pytest.fixture
def clients(tmp_path):
    engine=create_engine('sqlite:///'+(tmp_path/'site.db').as_posix(),connect_args={'check_same_thread':False})
    Base.metadata.create_all(engine)
    factory=sessionmaker(bind=engine)
    def override():
        db=factory()
        try:yield db
        finally:db.close()
    app.dependency_overrides[web.banco]=override
    web.TENTATIVAS.clear();web.CACHE_CLIMA.clear()
    with TestClient(app) as passenger,TestClient(app) as driver,TestClient(app) as other:
        yield passenger,driver,other,factory
    app.dependency_overrides.pop(web.banco,None);web.TENTATIVAS.clear();web.CACHE_CLIMA.clear();engine.dispose()

def accounts(clients):
    p,d,o,f=clients
    assert signup(p,'passageiro','Passageiro').status_code==201
    assert signup(d,'motorista','Motorista').status_code==201
    assert signup(o,'passageiro','OutraPessoa').status_code==201
    return p,d,o,f

def start(driver,percurso=None):
    r=post(driver,'viagens',{'linha_id':'maringa-007','veiculo':'DEMO-01','sentido':'Ida de demonstração','percurso_id':percurso})
    assert r.status_code==201,r.text
    return r.json()

def test_login_senha_preservada_hash_sessao_e_logout(clients):
    p,d,o,f=clients
    assert signup(p,'passageiro','Passageiro').status_code==201
    me=p.get('/web-api/me').json()
    assert me['conta']['perfil']=='passageiro'
    assert 'senha_hash' not in me['conta']
    cookie=p.cookies.get(web.COOKIE)
    with f() as db:
        conta=db.scalar(select(ContaWeb))
        assert conta.senha_hash!=PASS and PASS not in conta.senha_hash
        assert web.senha_valida(PASS,conta.senha_hash)
        assert not web.senha_valida(PASS.strip(),conta.senha_hash)
        assert db.get(SessaoWeb,web.hash_token(cookie)) is not None
        assert db.get(SessaoWeb,cookie) is None
    r=post(p,'sair');assert r.status_code==200
    assert p.get('/web-api/me').status_code==401
    assert post(p,'entrar',{'email':'PASSAGEIRO@exemplo.com','senha':'errada'}).status_code==401
    r=post(p,'entrar',{'email':'PASSAGEIRO@exemplo.com','senha':PASS})
    assert r.status_code==200
    assert 'httponly' in r.headers['set-cookie'].lower()
    assert 'samesite=strict' in r.headers['set-cookie'].lower()


def test_origem_autenticacao_e_papeis(clients):
    p,d,o,f=clients
    payload={'nome':'Teste','email':'teste@exemplo.com','senha':PASS,'perfil':'passageiro'}
    assert p.post('/web-api/contas',json=payload).status_code==403
    assert p.post('/web-api/contas',json=payload,headers={'origin':'https://outra.example'}).status_code==403
    assert p.get('/web-api/me').status_code==401
    p,d,o,f=accounts(clients)
    assert post(p,'viagens',{'linha_id':'maringa-007','veiculo':'1','sentido':'Ida'}).status_code==403
    assert post(d,'carteira/recarga-demo',{'valor_centavos':2000,'metodo':'pix','chave_idempotencia':str(uuid4())}).status_code==403
    assert post(p,'contas',payload|{'email':'novo@exemplo.com','perfil':'administrador'}).status_code==422


def test_viagem_gps_fresco_expira_e_outro_usuario_nao_altera(clients,monkeypatch):
    p,d,o,f=accounts(clients)
    v=start(d)
    assert not v['gps_recente'] and v['latitude'] is None
    assert post(d,'viagens',{'linha_id':'maringa-007','veiculo':'2','sentido':'Ida'}).status_code==409
    data={'latitude':-23.42,'longitude':-51.93,'precisao_m':15,'velocidade_m_s':None,'consentimento':True}
    assert post(p,'viagens/'+v['id']+'/gps',data).status_code==403
    assert post(d,'viagens/'+v['id']+'/gps',data|{'consentimento':False}).status_code==422
    assert post(d,'viagens/'+v['id']+'/gps',data|{'precisao_m':500}).status_code==422
    assert post(d,'viagens/'+v['id']+'/gps',data).status_code==200
    active=p.get('/web-api/viagens').json()['viagens'][0]
    assert active['gps_recente'] is True and active['latitude']==-23.42
    assert active['previsao_chegada'] is None
    now=web.agora();monkeypatch.setattr(web,'agora',lambda:now+91)
    stale=p.get('/web-api/viagens').json()['viagens'][0]
    assert stale['gps_recente'] is False and stale['latitude'] is None and stale['longitude'] is None
    assert post(o,'viagens/'+v['id']+'/encerrar').status_code==404
    assert post(d,'viagens/'+v['id']+'/encerrar').status_code==200
    assert p.get('/web-api/viagens').json()['viagens']==[]
    with f() as db:
        row=db.get(ViagemWeb,v['id']);assert row.latitude is None and row.gps_em is None


def test_percurso_pontos_embarque_ordem_avaliacao_e_lotacao(clients):
    p,d,o,f=accounts(clients)
    pontos=[{'nome':'Ponto de teste A','latitude':-23.42,'longitude':-51.93},{'nome':'Ponto de teste B','latitude':-23.43,'longitude':-51.92},{'nome':'Ponto de teste C','latitude':-23.44,'longitude':-51.91}]
    r=post(d,'percursos',{'pontos':pontos,'calcular_vias':False});assert r.status_code==201
    route=r.json();assert route['geometria'] is None and route['itinerario_oficial'] is False
    v=start(d,route['id'])
    assert post(p,'embarques',{'viagem_id':v['id'],'ponto_embarque':2,'ponto_desembarque':1}).status_code==422
    b=post(p,'embarques',{'viagem_id':v['id'],'ponto_embarque':0,'ponto_desembarque':2})
    assert b.status_code==201;bid=b.json()['id']
    assert post(p,'embarques',{'viagem_id':v['id']}).status_code==409
    assert post(o,'embarques/'+bid+'/desembarcar').status_code==404
    nota={'nota':5,'descricao':'Viagem de teste registrada.','lotacao':'superlotado'}
    assert post(p,'embarques/'+bid+'/avaliar',nota).status_code==409
    assert post(p,'embarques/'+bid+'/lotacao',{'lotacao':'superlotado'}).status_code==200
    run=d.get('/web-api/me').json()['viagem'];assert run['lotacao']=='superlotado' and run['embarcados_no_app']==1
    assert post(p,'embarques/'+bid+'/desembarcar').status_code==200
    assert post(p,'embarques/'+bid+'/avaliar',nota|{'nota':6}).status_code==422
    assert post(p,'embarques/'+bid+'/avaliar',nota).status_code==201
    assert post(p,'embarques/'+bid+'/avaliar',nota).status_code==409
    own=d.get('/web-api/me').json()['viagem'];assert own['nota_media_motorista']==5 and own['total_avaliacoes_motorista']==1
    assert d.get('/web-api/minhas-avaliacoes').json()['avaliacoes'][0]['descricao']==nota['descricao']
    assert o.get('/web-api/minhas-avaliacoes').json()['avaliacoes']==[]


def test_encerrar_viagem_fecha_embarques_e_remove_gps(clients):
    p,d,o,f=accounts(clients);v=start(d)
    bid=post(p,'embarques',{'viagem_id':v['id']}).json()['id']
    assert post(d,'viagens/'+v['id']+'/encerrar').status_code==200
    me=p.get('/web-api/me').json();assert me['embarque'] is None
    assert me['ultimo_embarque']['id']==bid and me['ultimo_embarque']['ativo'] is False
    assert post(p,'embarques/'+bid+'/avaliar',{'nota':4,'descricao':'Teste concluído.','lotacao':'medio'}).status_code==201


def test_carteira_demo_idempotente_parcelas_e_vt_sem_cobranca(clients):
    p,d,o,f=accounts(clients)
    key=str(uuid4());data={'valor_centavos':12001,'metodo':'credito','parcelas':12,'chave_idempotencia':key}
    first=post(p,'carteira/recarga-demo',data);assert first.status_code==201
    assert first.json()['modo']=='demonstracao'
    parcelas=first.json()['parcelas_ilustrativas_centavos'];assert len(parcelas)==12 and sum(parcelas)==12001
    second=post(p,'carteira/recarga-demo',data);assert second.json()['id']==first.json()['id'] and second.json()['repeticao'] is True
    assert post(p,'carteira/recarga-demo',data|{'valor_centavos':2000}).status_code==409
    assert post(p,'carteira/recarga-demo',data|{'chave_idempotencia':str(uuid4()),'metodo':'pix','parcelas':2}).status_code==422
    assert post(p,'carteira/recarga-demo',data|{'chave_idempotencia':str(uuid4()),'valor_centavos':-100}).status_code==422
    assert post(p,'carteira/recarga-demo',data|{'chave_idempotencia':str(uuid4()),'valor_centavos':1.5}).status_code==422
    vt=post(p,'carteira/vt-demo',{'valor_centavos':10000,'empresa':'Empresa de teste','chave_idempotencia':str(uuid4())});assert vt.status_code==201
    wallet=p.get('/web-api/carteira').json()
    assert wallet['saldo_centavos']==22001 and wallet['credito_vt_centavos']==10000
    assert len(wallet['lancamentos'])==2 and wallet['passes_reais'] is None
    assert o.get('/web-api/carteira').json()['saldo_centavos']==0
    config=p.get('/web-api/configuracao').json();assert config['tarifa']['valor_centavos']==580 and config['pagamentos_reais'] is False
    assert config['tarifa']['vigente_desde']=='2026-07-12'
    assert wallet['equivalencia_demonstracao']['quantidade']==37
    assert wallet['equivalencia_demonstracao']['resto_centavos']==541


def test_servicos_externos_nao_fabricam_clima_ou_geometria(clients,monkeypatch):
    p,d,o,f=accounts(clients)
    def unavailable(*args,**kwargs):raise OSError('Serviço indisponível no teste')
    monkeypatch.setattr(web,'urlopen',unavailable)
    assert p.get('/web-api/clima').status_code==503
    pontos=[{'nome':'Ponto A','latitude':-23.42,'longitude':-51.93},{'nome':'Ponto B','latitude':-23.43,'longitude':-51.92}]
    assert post(d,'percursos',{'pontos':pontos,'calcular_vias':True}).status_code==503
    assert post(d,'percursos',{'pontos':pontos,'calcular_vias':False}).json()['geometria'] is None


def test_previsao_real_recebida_preserva_probabilidade_e_fonte(clients,monkeypatch):
    p,d,o,f=clients
    fixture={'current':{'temperature_2m':23,'apparent_temperature':24,'weather_code':3,'is_day':1,'time':'2026-10-19T12:00'},'daily':{'precipitation_probability_max':[70],'temperature_2m_max':[28],'temperature_2m_min':[19]}}
    monkeypatch.setattr(web,'urlopen',lambda *a,**kw:BytesIO(json.dumps(fixture).encode()))
    data=p.get('/web-api/clima').json();assert data['probabilidade_chuva_percentual']==70 and data['sugere_guarda_chuva'] is True
    assert data['fonte']=='Open-Meteo' and data['instante_previsao']=='2026-10-19T12:00'
    assert p.get('/web-api/clima?cidade=desconhecida').status_code==422


def test_site_e_recursos_locais_acessiveis(clients):
    p,d,o,f=clients
    for path in ['/app/','/app/styles.css','/app/app.js','/app/vendor/leaflet/leaflet.js','/app/manifest.webmanifest']:
        r=p.get(path);assert r.status_code==200,path
    assert 'senha_hash' not in p.get('/web-api/linhas').text
    assert len(p.get('/web-api/linhas').json()['linhas'])==84


def test_validacao_nao_devolve_senha_enviada(clients):
    p,d,o,f=clients
    secret='SenhaQueNaoDeveVoltar!'
    response=post(p,'contas',{'nome':'X','email':'a@exemplo.com','senha':secret,'perfil':'passageiro'})
    assert response.status_code==422
    assert secret not in response.text
    assert all('input' not in x for x in response.json()['detail'])


def test_limite_de_tentativas_de_login(clients):
    p,d,o,f=clients
    assert signup(p,'passageiro','Passageiro').status_code==201
    web.TENTATIVAS.clear()
    for _ in range(10):
        assert post(p,'entrar',{'email':'passageiro@exemplo.com','senha':'incorreta'}).status_code==401
    assert post(p,'entrar',{'email':'passageiro@exemplo.com','senha':'incorreta'}).status_code==429


def test_percurso_recebido_do_servico_e_cabecalhos(clients,monkeypatch):
    p,d,o,f=accounts(clients)
    geometry={'type':'LineString','coordinates':[[-51.93,-23.42],[-51.925,-23.425],[-51.92,-23.43]]}
    fixture={'routes':[{'geometry':geometry,'distance':1750.5,'legs':[{'steps':[{'name':'Rua de teste','distance':150,'maneuver':{'type':'turn','modifier':'right','location':[-51.925,-23.425]}}]}]}]}
    monkeypatch.setattr(web,'urlopen',lambda *a,**kw:BytesIO(json.dumps(fixture).encode()))
    pontos=[{'nome':'Início de teste','latitude':-23.42,'longitude':-51.93},{'nome':'Fim de teste','latitude':-23.43,'longitude':-51.92}]
    response=post(d,'percursos',{'pontos':pontos,'calcular_vias':True})
    assert response.status_code==201
    route=response.json();assert route['geometria']==geometry and route['distancia_m']==1750.5
    assert 'não itinerário oficial' in route['fonte']
    assert route['instrucoes'][0]['direcao']=='right'
    assert d.get('/web-api/me').headers['cache-control']=='no-store'
    assert "script-src 'self'" in d.get('/app/').headers['content-security-policy']
