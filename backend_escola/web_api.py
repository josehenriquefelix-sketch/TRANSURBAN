"""Site funcional em banco local. Operadora, pagamentos e VT reais não estão integrados."""
from collections import defaultdict, deque
import hashlib
import hmac
import json
import math
from pathlib import Path
import re
import secrets
import time
from typing import Annotated, Literal
from urllib.parse import urlencode
from urllib.request import Request as URLRequest, urlopen
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from database import SessionLocal
from models_web import ContaWeb, SessaoWeb, PercursoWeb, ViagemWeb, EmbarqueWeb, AvaliacaoWeb, RelatoLotacaoWeb, LancamentoWeb

router=APIRouter(prefix='/web-api',tags=['Site — contas, viagens e demonstração'])
ROOT=Path(__file__).resolve().parent
CATALOGO=json.loads((ROOT/'data/site/catalogo.json').read_text(encoding='utf-8'))
LINHAS={x['id']:x for x in CATALOGO['lines']}
COOKIE='transurban_sessao'
LOTACOES=['vazio','medio','cheio','superlotado']
CACHE_CLIMA={}
TENTATIVAS={}

class Entrada(BaseModel):
    model_config=ConfigDict(extra='forbid',str_strip_whitespace=True)

Nome=Annotated[str,StringConstraints(min_length=2,max_length=80)]
class Cadastro(Entrada):
    nome:Nome
    email:Annotated[str,StringConstraints(min_length=5,max_length=160)]
    senha:Annotated[str,StringConstraints(strip_whitespace=False,min_length=8,max_length=128)]
    perfil:Literal['passageiro','motorista']
class Login(Entrada):
    email:Annotated[str,StringConstraints(min_length=5,max_length=160)]
    senha:Annotated[str,StringConstraints(strip_whitespace=False,min_length=1,max_length=128)]
class Ponto(Entrada):
    nome:Annotated[str,StringConstraints(min_length=2,max_length=80)]
    latitude:float=Field(ge=-26.5,le=-22,allow_inf_nan=False)
    longitude:float=Field(ge=-53,le=-48,allow_inf_nan=False)
class Planejamento(Entrada):
    pontos:list[Ponto]=Field(min_length=2,max_length=8)
    calcular_vias:bool=True
class InicioViagem(Entrada):
    linha_id:Annotated[str,StringConstraints(min_length=1,max_length=100)]
    veiculo:Annotated[str,StringConstraints(min_length=1,max_length=20)]
    sentido:Annotated[str,StringConstraints(min_length=2,max_length=100)]
    percurso_id:str | None=None
class GPS(Entrada):
    latitude:float=Field(ge=-26.5,le=-22,allow_inf_nan=False)
    longitude:float=Field(ge=-53,le=-48,allow_inf_nan=False)
    precisao_m:float=Field(ge=0,le=100,allow_inf_nan=False)
    velocidade_m_s:float | None=Field(default=None,ge=0,le=50,allow_inf_nan=False)
    consentimento:Literal[True]
class Embarque(Entrada):
    viagem_id:str
    ponto_embarque:int | None=Field(default=None,ge=0)
    ponto_desembarque:int | None=Field(default=None,ge=1)
class Nota(Entrada):
    nota:int=Field(ge=1,le=5,strict=True)
    descricao:Annotated[str,StringConstraints(min_length=3,max_length=500)]
    lotacao:Literal['vazio','medio','cheio','superlotado']
class Lotacao(Entrada):
    lotacao:Literal['vazio','medio','cheio','superlotado']
class Recarga(Entrada):
    valor_centavos:int=Field(ge=100,le=50000,strict=True)
    metodo:Literal['pix','credito','debito']
    parcelas:int=Field(default=1,ge=1,le=12,strict=True)
    chave_idempotencia:Annotated[str,StringConstraints(min_length=16,max_length=80)]
class CreditoVT(Entrada):
    valor_centavos:int=Field(ge=100,le=50000,strict=True)
    empresa:Annotated[str,StringConstraints(min_length=2,max_length=100)]
    chave_idempotencia:Annotated[str,StringConstraints(min_length=16,max_length=80)]


def agora():return int(time.time())
def erro(status,msg):raise HTTPException(status,msg)
def banco():
    db=SessionLocal()
    try:yield db
    finally:db.close()
def gravar(db):
    try:db.commit()
    except IntegrityError:
        db.rollback();erro(409,'Registro já existe ou a operação conflita com o estado atual. Atualize a tela.')
def origem(request:Request):
    if request.headers.get('origin')!=str(request.base_url).rstrip('/'):
        erro(403,'Abra o site no mesmo endereço do servidor antes de enviar dados.')
    if not request.headers.get('content-type','').startswith('application/json'):
        erro(415,'Envie os dados em JSON.')
def hash_token(token):return hashlib.sha256(token.encode()).hexdigest()
def senha_hash(senha,salt=None):
    salt=salt or secrets.token_hex(16)
    digest=hashlib.pbkdf2_hmac('sha256',senha.encode(),salt.encode(),600000).hex()
    return f'pbkdf2_sha256$600000${salt}${digest}'
def senha_valida(senha,hash_salvo):
    try:
        _,_,salt,_=hash_salvo.split('$')
        return hmac.compare_digest(senha_hash(senha,salt),hash_salvo)
    except (ValueError,TypeError):return False

def limitar_login(request):
    chave=request.client.host if request.client else 'local'
    now=agora()
    if len(TENTATIVAS)>1000:
        for k in list(TENTATIVAS):
            if not TENTATIVAS[k] or TENTATIVAS[k][-1]<now-60:del TENTATIVAS[k]
        if len(TENTATIVAS)>1000:erro(429,'Muitas tentativas. Aguarde um minuto.')
    tent=TENTATIVAS.setdefault(chave,deque())
    while tent and tent[0]<now-60:tent.popleft()
    if len(tent)>=10:erro(429,'Muitas tentativas. Aguarde um minuto e tente novamente.')
    tent.append(now)

def conta_atual(request:Request,db:Session=Depends(banco)):
    token=request.cookies.get(COOKIE,'')
    sessao=db.get(SessaoWeb,hash_token(token)) if token else None
    if not sessao or sessao.expira_em<agora():erro(401,'Entre na sua conta para continuar.')
    conta=db.get(ContaWeb,sessao.conta_id)
    if not conta:erro(401,'Sessão inválida. Entre novamente.')
    return conta

def exigir(conta,perfil):
    if conta.perfil!=perfil:erro(403,'Esta operação não está disponível para seu perfil.')
def criar_sessao(db,conta,response,request):
    token=secrets.token_urlsafe(32)
    db.add(SessaoWeb(token_hash=hash_token(token),conta_id=conta.id,expira_em=agora()+28800))
    gravar(db)
    response.set_cookie(COOKIE,token,max_age=28800,httponly=True,samesite='strict',secure=request.url.scheme=='https',path='/')
def perfil(conta):return {'id':conta.id,'nome':conta.nome,'email':conta.email,'perfil':conta.perfil,'motorista_verificado':False}
def percurso_dict(p):
    if not p:return None
    return {'id':p.id,'pontos':p.pontos,'geometria':p.geometria,'instrucoes':p.instrucoes,
            'distancia_m':p.distancia_m,'fonte':p.fonte,'itinerario_oficial':False,
            'aviso':'Percurso escolhido pelo motorista. Rota viária de referência não é itinerário oficial nem considera restrições de ônibus.'}

def viagem_dict(v,db):
    now=agora();recente=bool(v.ativa and v.gps_em and 0<=now-v.gps_em<=90)
    reports=db.scalars(select(RelatoLotacaoWeb).where(RelatoLotacaoWeb.viagem_id==v.id,RelatoLotacaoWeb.atualizado_em>=now-900)).all()
    valores=[x.lotacao for x in reports]
    if v.lotacao_em and v.lotacao_em>=now-900 and v.lotacao_motorista:valores.append(v.lotacao_motorista)
    # Apresenta o relato mais conservador recebido, não uma medição da lotação.
    ocup=max(valores,key=lambda x:LOTACOES.index(x)) if valores else None
    motorista=db.get(ContaWeb,v.motorista_id)
    media,total=db.execute(select(func.avg(AvaliacaoWeb.nota),func.count(AvaliacaoWeb.id)).join(ViagemWeb,AvaliacaoWeb.viagem_id==ViagemWeb.id).where(ViagemWeb.motorista_id==v.motorista_id)).one()
    quantidade=db.scalar(select(func.count()).select_from(EmbarqueWeb).where(EmbarqueWeb.viagem_id==v.id,EmbarqueWeb.ativo==True))
    return {'id':v.id,'linha_id':v.linha_id,'linha':LINHAS.get(v.linha_id),'veiculo':v.veiculo,'sentido':v.sentido,
            'ativa':v.ativa,'motorista':motorista.nome if motorista else 'Motorista','motorista_verificado':False,
            'nota_media_motorista':round(float(media),2) if media is not None else None,'total_avaliacoes_motorista':total,
            'embarcados_no_app':quantidade,'lotacao':ocup,'relatos_recentes':len(valores),
            'lotacao_aviso':'Relatos colaborativos dos últimos 15 minutos; não é contagem de passageiros.',
            'gps_recente':recente,'gps_em':v.gps_em if recente else None,
            'latitude':v.latitude if recente else None,'longitude':v.longitude if recente else None,
            'precisao_m':v.precisao_m if recente else None,'velocidade_m_s':v.velocidade_m_s if recente else None,
            'percurso':percurso_dict(db.get(PercursoWeb,v.percurso_id)) if v.percurso_id else None,
            'iniciada_em':v.iniciada_em,'encerrada_em':v.encerrada_em,
            'previsao_chegada':None,'aviso':'Viagem autodeclarada de demonstração. Não é integração à frota da operadora.'}

def embarque_dict(b,db):
    nota=db.scalar(select(AvaliacaoWeb).where(AvaliacaoWeb.embarque_id==b.id))
    return {'id':b.id,'ativo':b.ativo,'ponto_embarque':b.ponto_embarque,'ponto_desembarque':b.ponto_desembarque,
            'viagem':viagem_dict(db.get(ViagemWeb,b.viagem_id),db),'criado_em':b.criado_em,'encerrado_em':b.encerrado_em,
            'avaliacao':{'nota':nota.nota,'descricao':nota.descricao,'lotacao':nota.lotacao} if nota else None}

@router.get('/configuracao')
def configuracao():
    tarifa=json.loads((ROOT/'data/site/tarifa.json').read_text(encoding='utf-8'))
    return {'modo':'demonstracao','pagamentos_reais':False,'vt_empresarial_real':False,'tarifa':tarifa,
            'catalogo_status':CATALOGO['status_verificacao'],'catalogo_consulta_declarada':CATALOGO['checkedAt'],
            'itinerarios_oficiais':False,'gps':'Compartilhamento voluntário; página aberta e permissão do navegador. Expira após 90 segundos.',
            'mapa_fonte':'OpenStreetMap','clima_fonte':'Open-Meteo','roteamento_fonte':'OSRM, perfil driving; não substitui itinerário de ônibus.'}

@router.get('/linhas')
def linhas():return {'linhas':list(LINHAS.values()),'status':CATALOGO['status_verificacao']}

@router.post('/contas',status_code=201,dependencies=[Depends(origem)])
def cadastrar(data:Cadastro,request:Request,response:Response,db:Session=Depends(banco)):
    limitar_login(request)
    email=data.email.lower()
    if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',email):erro(422,'Informe um e-mail válido.')
    if db.scalar(select(ContaWeb).where(ContaWeb.email==email)):erro(409,'Este e-mail já está cadastrado. Entre na conta.')
    conta=ContaWeb(id=str(uuid4()),nome=data.nome,email=email,senha_hash=senha_hash(data.senha),perfil=data.perfil,criada_em=agora())
    db.add(conta)
    try:db.flush()
    except IntegrityError:
        db.rollback();erro(409,'Este e-mail já está cadastrado. Entre na conta.')
    criar_sessao(db,conta,response,request)
    return {'conta':perfil(conta)}

@router.post('/entrar',dependencies=[Depends(origem)])
def entrar(data:Login,request:Request,response:Response,db:Session=Depends(banco)):
    limitar_login(request)
    conta=db.scalar(select(ContaWeb).where(ContaWeb.email==data.email.lower()))
    if not conta:
        senha_hash(data.senha)  # Trabalho semelhante ao caso de senha incorreta.
        erro(401,'E-mail ou senha incorretos.')
    if not senha_valida(data.senha,conta.senha_hash):erro(401,'E-mail ou senha incorretos.')
    criar_sessao(db,conta,response,request);return {'conta':perfil(conta)}

@router.post('/sair',dependencies=[Depends(origem)])
def sair(request:Request,response:Response,conta=Depends(conta_atual),db:Session=Depends(banco)):
    token=request.cookies.get(COOKIE,'')
    db.execute(delete(SessaoWeb).where(SessaoWeb.token_hash==hash_token(token)))
    # Sair do perfil de motorista remove GPS, mas não inventa encerramento de viagem.
    if conta.perfil=='motorista':
        db.execute(update(ViagemWeb).where(ViagemWeb.motorista_id==conta.id,ViagemWeb.ativa==True).values(latitude=None,longitude=None,precisao_m=None,velocidade_m_s=None,gps_em=None))
    gravar(db);response.delete_cookie(COOKIE,path='/');return {'ok':True}

@router.get('/me')
def me(conta=Depends(conta_atual),db:Session=Depends(banco)):
    viagem=db.scalar(select(ViagemWeb).where(ViagemWeb.motorista_id==conta.id,ViagemWeb.ativa==True)) if conta.perfil=='motorista' else None
    embarque=db.scalar(select(EmbarqueWeb).where(EmbarqueWeb.passageiro_id==conta.id,EmbarqueWeb.ativo==True))
    ultimo=db.scalar(select(EmbarqueWeb).where(EmbarqueWeb.passageiro_id==conta.id).order_by(EmbarqueWeb.criado_em.desc(),EmbarqueWeb.id.desc()))
    resumo_motorista=None
    if conta.perfil=='motorista':
        media,total=db.execute(select(func.avg(AvaliacaoWeb.nota),func.count(AvaliacaoWeb.id)).join(ViagemWeb,AvaliacaoWeb.viagem_id==ViagemWeb.id).where(ViagemWeb.motorista_id==conta.id)).one()
        resumo_motorista={'nota_media':round(float(media),2) if media is not None else None,'total_avaliacoes':total}
    return {'conta':perfil(conta),'viagem':viagem_dict(viagem,db) if viagem else None,
            'embarque':embarque_dict(embarque,db) if embarque else None,
            'ultimo_embarque':embarque_dict(ultimo,db) if ultimo else None,'resumo_motorista':resumo_motorista}

@router.get('/viagens')
def viagens(conta=Depends(conta_atual),db:Session=Depends(banco)):
    rows=db.scalars(select(ViagemWeb).where(ViagemWeb.ativa==True,ViagemWeb.iniciada_em>=agora()-28800).order_by(ViagemWeb.iniciada_em.desc())).all()
    return {'viagens':[viagem_dict(v,db) for v in rows]}

@router.post('/percursos',status_code=201,dependencies=[Depends(origem)])
def planejar(data:Planejamento,conta=Depends(conta_atual),db:Session=Depends(banco)):
    exigir(conta,'motorista')
    pontos=[p.model_dump() for p in data.pontos]
    geometria=None;instrucoes=[];distancia=None
    fonte='Pontos escolhidos pelo motorista; sem trajeto viário calculado.'
    if data.calcular_vias:
        coords=';'.join(f'{p.longitude},{p.latitude}' for p in data.pontos)
        url=f'https://router.project-osrm.org/route/v1/driving/{coords}?overview=full&geometries=geojson&steps=true'
        try:
            with urlopen(URLRequest(url,headers={'User-Agent':'TRANSURBAN-academic/1.0'}),timeout=10) as result:
                raw=json.load(result)
            rota=raw['routes'][0]
            geometria=rota['geometry']
            if not isinstance(geometria,dict) or geometria.get('type')!='LineString' or not 2<=len(geometria.get('coordinates',[]))<=30000:raise ValueError('Geometria inválida')
            for coord in geometria['coordinates']:
                if not isinstance(coord,list) or len(coord)!=2 or not all(isinstance(n,(int,float)) and math.isfinite(n) for n in coord):raise ValueError('Coordenada inválida')
                if not (-53<=coord[0]<=-48 and -26.5<=coord[1]<=-22):raise ValueError('Geometria fora da região')
            distancia=float(rota['distance'])
            if not math.isfinite(distancia) or distancia<0:raise ValueError('Distância inválida')
            for leg in rota.get('legs',[]):
                for step in leg.get('steps',[]):
                    m=step.get('maneuver',{})
                    instrucoes.append({'via':str(step.get('name',''))[:160],'tipo':str(m.get('type',''))[:40],
                        'direcao':str(m.get('modifier',''))[:40],'distancia_m':round(float(step.get('distance',0)),1),
                        'posicao':m.get('location')})
            fonte='OSRM sobre OpenStreetMap, perfil driving. Rota viária, não itinerário oficial de ônibus.'
        except (OSError,ValueError,KeyError,IndexError,TypeError):
            erro(503,'Não foi possível consultar as vias. Tente com internet ou salve somente os pontos, sem desenhar um trajeto inventado.')
    p=PercursoWeb(id=str(uuid4()),conta_id=conta.id,pontos=pontos,geometria=geometria,instrucoes=instrucoes,distancia_m=distancia,fonte=fonte,criado_em=agora())
    db.add(p);gravar(db);return percurso_dict(p)

@router.post('/viagens',status_code=201,dependencies=[Depends(origem)])
def iniciar(data:InicioViagem,conta=Depends(conta_atual),db:Session=Depends(banco)):
    exigir(conta,'motorista')
    if data.linha_id not in LINHAS:erro(422,'Escolha uma linha do catálogo.')
    if db.scalar(select(ViagemWeb).where(ViagemWeb.motorista_id==conta.id,ViagemWeb.ativa==True)):erro(409,'Você já tem uma viagem em andamento.')
    if data.percurso_id:
        percurso=db.get(PercursoWeb,data.percurso_id)
        if not percurso or percurso.conta_id!=conta.id:erro(404,'Percurso não encontrado na sua conta.')
    v=ViagemWeb(id=str(uuid4()),motorista_id=conta.id,linha_id=data.linha_id,veiculo=data.veiculo,sentido=data.sentido,
                percurso_id=data.percurso_id,ativa=True,iniciada_em=agora())
    db.add(v);gravar(db);return viagem_dict(v,db)

def propria_viagem(viagem_id,conta,db):
    v=db.get(ViagemWeb,viagem_id)
    if not v or v.motorista_id!=conta.id:erro(404,'Viagem não encontrada na sua conta.')
    if not v.ativa:erro(409,'Esta viagem já foi encerrada.')
    return v

@router.post('/viagens/{viagem_id}/gps',dependencies=[Depends(origem)])
def gps(viagem_id:str,data:GPS,conta=Depends(conta_atual),db:Session=Depends(banco)):
    exigir(conta,'motorista');v=propria_viagem(viagem_id,conta,db)
    v.latitude=data.latitude;v.longitude=data.longitude;v.precisao_m=data.precisao_m
    v.velocidade_m_s=data.velocidade_m_s;v.gps_em=agora();gravar(db)
    return {'ok':True,'gps_em':v.gps_em,'expira_em_segundos':90}

@router.post('/viagens/{viagem_id}/parar-gps',dependencies=[Depends(origem)])
def parar_gps(viagem_id:str,conta=Depends(conta_atual),db:Session=Depends(banco)):
    v=propria_viagem(viagem_id,conta,db)
    v.latitude=None;v.longitude=None;v.precisao_m=None;v.velocidade_m_s=None;v.gps_em=None
    gravar(db);return {'ok':True}

@router.post('/viagens/{viagem_id}/encerrar',dependencies=[Depends(origem)])
def encerrar(viagem_id:str,conta=Depends(conta_atual),db:Session=Depends(banco)):
    v=propria_viagem(viagem_id,conta,db)
    v.ativa=False;v.encerrada_em=agora();v.latitude=None;v.longitude=None;v.precisao_m=None;v.velocidade_m_s=None;v.gps_em=None
    db.execute(update(EmbarqueWeb).where(EmbarqueWeb.viagem_id==v.id,EmbarqueWeb.ativo==True).values(ativo=False,encerrado_em=agora()))
    gravar(db);return {'ok':True}

@router.post('/viagens/{viagem_id}/lotacao',dependencies=[Depends(origem)])
def lotacao_motorista(viagem_id:str,data:Lotacao,conta=Depends(conta_atual),db:Session=Depends(banco)):
    v=propria_viagem(viagem_id,conta,db);v.lotacao_motorista=data.lotacao;v.lotacao_em=agora();gravar(db)
    return {'ok':True}

@router.post('/embarques',status_code=201,dependencies=[Depends(origem)])
def embarcar(data:Embarque,conta=Depends(conta_atual),db:Session=Depends(banco)):
    exigir(conta,'passageiro');v=db.get(ViagemWeb,data.viagem_id)
    if not v or not v.ativa or v.iniciada_em<agora()-28800:erro(404,'Esta viagem não está disponível.')
    if db.scalar(select(EmbarqueWeb).where(EmbarqueWeb.passageiro_id==conta.id,EmbarqueWeb.ativo==True)):erro(409,'Você já está em uma viagem. Registre o desembarque primeiro.')
    percurso=db.get(PercursoWeb,v.percurso_id) if v.percurso_id else None
    if data.ponto_embarque is not None or data.ponto_desembarque is not None:
        if not percurso or data.ponto_embarque is None or data.ponto_desembarque is None:erro(422,'Escolha os dois pontos do percurso informado.')
        if not 0<=data.ponto_embarque<data.ponto_desembarque<len(percurso.pontos):erro(422,'O desembarque precisa vir depois do embarque no percurso.')
    # ID ordenável resolve empates entre dois embarques registrados no mesmo segundo.
    b=EmbarqueWeb(id=f'{time.time_ns():019d}-{secrets.token_hex(8)}',passageiro_id=conta.id,viagem_id=v.id,ponto_embarque=data.ponto_embarque,
                  ponto_desembarque=data.ponto_desembarque,ativo=True,criado_em=agora())
    db.add(b);gravar(db);return embarque_dict(b,db)

def proprio_embarque(embarque_id,conta,db):
    b=db.get(EmbarqueWeb,embarque_id)
    if not b or b.passageiro_id!=conta.id:erro(404,'Embarque não encontrado na sua conta.')
    return b

@router.post('/embarques/{embarque_id}/desembarcar',dependencies=[Depends(origem)])
def desembarcar(embarque_id:str,conta=Depends(conta_atual),db:Session=Depends(banco)):
    b=proprio_embarque(embarque_id,conta,db)
    if not b.ativo:erro(409,'O desembarque já foi registrado.')
    b.ativo=False;b.encerrado_em=agora();gravar(db);return embarque_dict(b,db)

@router.post('/embarques/{embarque_id}/lotacao',dependencies=[Depends(origem)])
def relatar(embarque_id:str,data:Lotacao,conta=Depends(conta_atual),db:Session=Depends(banco)):
    b=proprio_embarque(embarque_id,conta,db)
    if not b.ativo:erro(409,'Relate a lotação durante o embarque ativo.')
    item=db.scalar(select(RelatoLotacaoWeb).where(RelatoLotacaoWeb.embarque_id==b.id))
    if not item:item=RelatoLotacaoWeb(id=str(uuid4()),embarque_id=b.id,viagem_id=b.viagem_id);db.add(item)
    item.lotacao=data.lotacao;item.atualizado_em=agora();gravar(db);return {'ok':True}

@router.post('/embarques/{embarque_id}/avaliar',status_code=201,dependencies=[Depends(origem)])
def avaliar(embarque_id:str,data:Nota,conta=Depends(conta_atual),db:Session=Depends(banco)):
    b=proprio_embarque(embarque_id,conta,db)
    if b.ativo:erro(409,'Registre o desembarque antes de avaliar.')
    if db.scalar(select(AvaliacaoWeb).where(AvaliacaoWeb.embarque_id==b.id)):erro(409,'Você já avaliou este embarque.')
    nota=AvaliacaoWeb(id=str(uuid4()),embarque_id=b.id,passageiro_id=conta.id,viagem_id=b.viagem_id,
        nota=data.nota,descricao=data.descricao,lotacao=data.lotacao,criada_em=agora())
    db.add(nota);gravar(db);return {'ok':True,'nota':nota.nota,'descricao':nota.descricao,'lotacao':nota.lotacao}

@router.get('/minhas-avaliacoes')
def minhas_avaliacoes(conta=Depends(conta_atual),db:Session=Depends(banco)):
    q=select(AvaliacaoWeb).join(ViagemWeb,AvaliacaoWeb.viagem_id==ViagemWeb.id).where(ViagemWeb.motorista_id==conta.id) if conta.perfil=='motorista' else select(AvaliacaoWeb).where(AvaliacaoWeb.passageiro_id==conta.id)
    rows=db.scalars(q.order_by(AvaliacaoWeb.criada_em.desc()).limit(50)).all()
    return {'avaliacoes':[{'id':r.id,'nota':r.nota,'descricao':r.descricao,'lotacao':r.lotacao,'criada_em':r.criada_em,'viagem_id':r.viagem_id} for r in rows]}

@router.get('/carteira')
def carteira(conta=Depends(conta_atual),db:Session=Depends(banco)):
    exigir(conta,'passageiro')
    rows=db.scalars(select(LancamentoWeb).where(LancamentoWeb.conta_id==conta.id).order_by(LancamentoWeb.criado_em.desc(),LancamentoWeb.id.desc())).all()
    saldo=sum(x.valor_centavos for x in rows)
    tarifa=json.loads((ROOT/'data/site/tarifa.json').read_text(encoding='utf-8'))
    valor=tarifa.get('valor_centavos')
    referencia=valor if tarifa.get('verificada') and type(valor) is int and valor>0 else None
    return {'modo':'demonstracao','saldo_centavos':saldo,'credito_vt_centavos':sum(x.valor_centavos for x in rows if x.tipo=='vt_demo'),
            'passes_reais':None,'equivalencia_demonstracao':({
                'tarifa_integral_centavos':referencia,'quantidade':saldo//referencia,
                'resto_centavos':saldo%referencia,'cidade':'Maringá','fonte_url':tarifa['fonte_url'],
                'aviso':'Equivalência matemática em tarifa integral urbana de Maringá; não são bilhetes ou passes disponíveis para embarque.'
            } if referencia else None),'aviso':'Créditos de demonstração: não compram passagens e não são depósitos de empresas ou cobranças bancárias.',
            'lancamentos':[{'id':x.id,'tipo':x.tipo,'valor_centavos':x.valor_centavos,'metodo':x.metodo,'parcelas':x.parcelas,'origem':x.origem,'criado_em':x.criado_em} for x in rows]}

def lancar(db,conta,valor,tipo,metodo,parcelas,chave,origem_credito=None):
    anterior=db.scalar(select(LancamentoWeb).where(LancamentoWeb.conta_id==conta.id,LancamentoWeb.chave_idempotencia==chave))
    if anterior:
        if (anterior.valor_centavos,anterior.tipo,anterior.metodo,anterior.parcelas,anterior.origem)!=(valor,tipo,metodo,parcelas,origem_credito):erro(409,'A chave já foi usada com outros dados. Atualize a solicitação.')
        return {'id':anterior.id,'modo':'demonstracao','repeticao':True}
    item=LancamentoWeb(id=str(uuid4()),conta_id=conta.id,tipo=tipo,valor_centavos=valor,metodo=metodo,
        parcelas=parcelas,origem=origem_credito,chave_idempotencia=chave,criado_em=agora())
    db.add(item);gravar(db)
    base,resto=divmod(valor,parcelas)
    return {'id':item.id,'modo':'demonstracao','repeticao':False,
            'parcelas_ilustrativas_centavos':[base+(1 if i<resto else 0) for i in range(parcelas)],
            'aviso':'Sem cobrança, cartão ou PIX processado. Parcelamento ilustrativo, sem cotação de juros e sem vínculo com a operadora.'}

@router.post('/carteira/recarga-demo',status_code=201,dependencies=[Depends(origem)])
def recarga(data:Recarga,conta=Depends(conta_atual),db:Session=Depends(banco)):
    exigir(conta,'passageiro')
    if data.metodo!='credito' and data.parcelas!=1:erro(422,'Parcelamento só pode ser selecionado no crédito da demonstração.')
    return lancar(db,conta,data.valor_centavos,'recarga_demo',data.metodo,data.parcelas,data.chave_idempotencia)

@router.post('/carteira/vt-demo',status_code=201,dependencies=[Depends(origem)])
def vt_demo(data:CreditoVT,conta=Depends(conta_atual),db:Session=Depends(banco)):
    exigir(conta,'passageiro')
    return lancar(db,conta,data.valor_centavos,'vt_demo','vt',1,data.chave_idempotencia,data.empresa)

@router.get('/clima')
def clima(cidade:Literal['Maringá','Sarandi']='Maringá'):
    now=agora();cache=CACHE_CLIMA.get(cidade)
    if cache and now-cache['consultado_em']<600:return cache
    latitude,longitude={'Maringá':(-23.4205,-51.9333),'Sarandi':(-23.4441,-51.8767)}[cidade]
    query=urlencode({'latitude':latitude,'longitude':longitude,'current':'temperature_2m,apparent_temperature,is_day,weather_code',
        'daily':'precipitation_probability_max,temperature_2m_max,temperature_2m_min','forecast_days':1,'timezone':'America/Sao_Paulo'})
    url='https://api.open-meteo.com/v1/forecast?'+query
    try:
        with urlopen(URLRequest(url,headers={'User-Agent':'TRANSURBAN-academic/1.0'}),timeout=8) as response:raw=json.load(response)
        atual=raw['current'];dia=raw['daily'];prob=dia['precipitation_probability_max'][0]
        codigo=atual['weather_code'];temperatura=atual['temperature_2m']
        if temperatura is None or not math.isfinite(float(temperatura)):raise ValueError('Sem temperatura')
        guarda_chuva=bool((prob is not None and prob>=40) or 51<=codigo<=99)
        result={'cidade':cidade,'fonte':'Open-Meteo','fonte_url':'https://open-meteo.com/','consultado_em':now,
            'instante_previsao':atual['time'],'temperatura_c':temperatura,'sensacao_c':atual.get('apparent_temperature'),
            'codigo_tempo':codigo,'dia':bool(atual['is_day']),'probabilidade_chuva_percentual':prob,
            'maxima_c':dia['temperature_2m_max'][0],'minima_c':dia['temperature_2m_min'][0],
            'sugere_guarda_chuva':guarda_chuva,'aviso':'Previsão meteorológica, não garantia. Probabilidade diária; não indica chuva em cada ponto da cidade.'}
        CACHE_CLIMA[cidade]=result;return result
    except (OSError,ValueError,KeyError,IndexError,TypeError):
        erro(503,'Previsão indisponível agora. Nenhum dado de clima foi inventado; confira sua conexão.')
