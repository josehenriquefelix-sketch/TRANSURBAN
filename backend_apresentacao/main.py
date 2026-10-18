"""TRANSURBAN: API local de apresentação. Dados ilustrativos, sem autenticação."""
import csv
import os
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, UniqueConstraint, CheckConstraint, create_engine, event, select, text, inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / 'data' / 'transurban.db'
load_dotenv(ROOT / '.env', override=False)
modo = os.environ.get('TRANSURBAN_MODO', 'auto')
url = 'sqlite:///' + DB_PATH.as_posix() if modo == 'local' else os.environ.get('DATABASE_URL', 'sqlite:///' + DB_PATH.as_posix())
if modo == 'supabase' and not url.startswith(('postgresql:', 'postgresql+', 'postgres:')):
    raise RuntimeError('Configure DATABASE_URL no .env local para usar Supabase.')
if url.startswith('postgres://'):
    url = url.replace('postgres://', 'postgresql://', 1)
engine = create_engine(url, connect_args={'check_same_thread': False} if url.startswith('sqlite:') else {'sslmode': 'require', 'connect_timeout': 12}, pool_pre_ping=True)
if engine.dialect.name == 'sqlite':
    @event.listens_for(engine, 'connect')
    def foreign_keys(connection, _):
        connection.execute('PRAGMA foreign_keys=ON')
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

class Cidade(Base):
    __tablename__ = 'cidade'
    id_cidade = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False, unique=True)

class Linha(Base):
    __tablename__ = 'linha_onibus'
    id_linha = Column(Integer, primary_key=True)
    id_cidade = Column(Integer, ForeignKey('cidade.id_cidade'), nullable=False)
    codigo = Column(String(20), nullable=False)
    nome = Column(String(120), nullable=False)
    __table_args__ = (UniqueConstraint('id_cidade', 'codigo'),)

class Trecho(Base):
    __tablename__ = 'trecho'
    id_trecho = Column(Integer, primary_key=True)
    id_cidade_origem = Column(Integer, ForeignKey('cidade.id_cidade'), nullable=False)
    id_cidade_destino = Column(Integer, ForeignKey('cidade.id_cidade'), nullable=False)
    nome = Column(String(150), nullable=False)
    distancia_km = Column(Float, nullable=False)
    __table_args__ = (CheckConstraint('distancia_km > 0'), CheckConstraint('id_cidade_origem <> id_cidade_destino'))

class Percurso(Base):
    __tablename__ = 'linha_trecho'
    id_linha = Column(Integer, ForeignKey('linha_onibus.id_linha'), primary_key=True)
    id_trecho = Column(Integer, ForeignKey('trecho.id_trecho'), primary_key=True)
    ordem = Column(Integer, nullable=False)
    __table_args__ = (UniqueConstraint('id_linha', 'ordem'), CheckConstraint('ordem > 0'))

class Faixa(Base):
    __tablename__ = 'faixa_exclusiva'
    id_faixa = Column(Integer, primary_key=True)
    id_trecho = Column(Integer, ForeignKey('trecho.id_trecho'), nullable=False)
    tipo = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False)
    __table_args__ = (CheckConstraint("tipo IN ('EXCLUSIVA','PREFERENCIAL')"), CheckConstraint("status IN ('ATIVA','INATIVA','PLANEJADA')"))

class Atraso(Base):
    __tablename__ = 'registro_atraso'
    id_atraso = Column(Integer, primary_key=True)
    id_linha = Column(Integer, ForeignKey('linha_onibus.id_linha'), nullable=False)
    id_trecho = Column(Integer, ForeignKey('trecho.id_trecho'), nullable=False)
    data_registro = Column(Date, nullable=False)
    minutos_atraso = Column(Integer, nullable=False)
    observacao = Column(String(255), nullable=False, default='')
    __table_args__ = (CheckConstraint('minutos_atraso >= 0'),)

Nome = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
Positivo = Annotated[int, Field(gt=0, strict=True)]
class Entrada(BaseModel):
    model_config = ConfigDict(extra='forbid')
class CidadeIn(Entrada):
    nome: Nome
class LinhaIn(Entrada):
    id_cidade: Positivo
    codigo: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20)]
    nome: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
class TrechoIn(Entrada):
    id_cidade_origem: Positivo
    id_cidade_destino: Positivo
    nome: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=150)]
    distancia_km: float = Field(gt=0, le=9999.99, allow_inf_nan=False)
    @model_validator(mode='after')
    def cidades_diferentes(self):
        if self.id_cidade_origem == self.id_cidade_destino:
            raise ValueError('O modelo acadêmico exige cidades de origem e destino diferentes.')
        return self
class PercursoIn(Entrada):
    id_linha: Positivo
    id_trecho: Positivo
    ordem: Positivo
class FaixaIn(Entrada):
    id_trecho: Positivo
    tipo: Literal['EXCLUSIVA', 'PREFERENCIAL']
    status: Literal['ATIVA', 'INATIVA', 'PLANEJADA']
class AtrasoIn(Entrada):
    id_linha: Positivo
    id_trecho: Positivo
    data_registro: date
    minutos_atraso: int = Field(ge=0, strict=True)
    observacao: str = Field(default='', max_length=255)

@asynccontextmanager
async def lifespan(app):
    ROOT.joinpath('data').mkdir(exist_ok=True)
    if engine.dialect.name == 'sqlite':
        Base.metadata.create_all(engine)
    else:
        faltam = set(Base.metadata.tables) - set(inspect(engine).get_table_names(schema='public'))
        if faltam:
            raise RuntimeError('Tabelas ausentes no PostgreSQL: ' + ', '.join(sorted(faltam)))
    yield

app = FastAPI(title='TRANSURBAN — apresentação', version='2.1.0', lifespan=lifespan, description='Demonstração acadêmica. SQLite local ou PostgreSQL/Supabase configurado no backend. Sem login. CSV sintético.')
app.mount('/static', StaticFiles(directory=ROOT / 'static'), name='static')

def get_db():
    with SessionLocal() as db:
        yield db
Db = Annotated[Session, Depends(get_db)]
def exigir(db, modelo, ident):
    registro = db.get(modelo, ident)
    if registro is None:
        raise HTTPException(404, f'{modelo.__name__} não encontrado(a).')
    return registro
def serializar(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
def salvar(db, obj):
    try:
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return serializar(obj)
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, 'Cadastro duplicado ou incompatível com as regras do banco.')
def listar(db, modelo):
    return [serializar(o) for o in db.scalars(select(modelo).order_by(*modelo.__table__.primary_key.columns)).all()]

@app.get('/', include_in_schema=False)
def raiz():
    return RedirectResponse('/apresentacao')
@app.get('/apresentacao', include_in_schema=False)
def painel():
    return FileResponse(ROOT / 'static' / 'index.html')
@app.get('/health')
def health(db: Db):
    db.execute(text('SELECT 1'))
    return {'status': 'ok', 'banco': engine.dialect.name, 'modo': 'demonstração acadêmica', 'autenticacao': False, 'aplicacao': 'transurban', 'instancia': os.environ.get('TRANSURBAN_INSTANCIA', '')}
@app.get('/cidades')
def cidades(db: Db):
    return listar(db, Cidade)
@app.post('/cidades', status_code=201)
def cidade(dados: CidadeIn, db: Db):
    return salvar(db, Cidade(**dados.model_dump()))
@app.get('/linhas')
def linhas(db: Db):
    return [{**serializar(l), 'cidade': c.nome} for l,c in db.execute(select(Linha,Cidade).join(Cidade).order_by(Linha.id_linha))]
@app.post('/linhas', status_code=201)
def linha(dados: LinhaIn, db: Db):
    c = exigir(db, Cidade, dados.id_cidade)
    return {**salvar(db, Linha(**dados.model_dump())), 'cidade': c.nome}
@app.get('/trechos')
def trechos(db: Db):
    return listar(db, Trecho)
@app.post('/trechos', status_code=201)
def trecho(dados: TrechoIn, db: Db):
    exigir(db, Cidade, dados.id_cidade_origem)
    exigir(db, Cidade, dados.id_cidade_destino)
    return salvar(db, Trecho(**dados.model_dump()))
@app.get('/linhas/{id_linha}/percurso')
def percurso(id_linha: int, db: Db):
    exigir(db, Linha, id_linha)
    return [{**serializar(p), 'trecho': t.nome} for p,t in db.execute(select(Percurso,Trecho).join(Trecho).where(Percurso.id_linha==id_linha).order_by(Percurso.ordem))]
@app.post('/percursos', status_code=201)
def vincular(dados: PercursoIn, db: Db):
    exigir(db, Linha, dados.id_linha)
    exigir(db, Trecho, dados.id_trecho)
    return salvar(db, Percurso(**dados.model_dump()))
@app.get('/faixas')
def faixas(db: Db):
    return listar(db, Faixa)
@app.post('/faixas', status_code=201)
def faixa(dados: FaixaIn, db: Db):
    exigir(db, Trecho, dados.id_trecho)
    return salvar(db, Faixa(**dados.model_dump()))
@app.get('/atrasos')
def atrasos(db: Db):
    return listar(db, Atraso)
@app.post('/atrasos', status_code=201)
def atraso(dados: AtrasoIn, db: Db):
    exigir(db, Linha, dados.id_linha)
    exigir(db, Trecho, dados.id_trecho)
    if db.get(Percurso, (dados.id_linha, dados.id_trecho)) is None:
        raise HTTPException(404, 'Trecho não vinculado ao percurso desta linha.')
    return salvar(db, Atraso(**dados.model_dump()))
@app.get('/indicadores')
def indicadores():
    with (ROOT/'data'/'atrasos_analise.csv').open(encoding='utf-8-sig', newline='') as f:
        registros = list(csv.DictReader(f))
    valores = [int(r['minutos_atraso']) for r in registros]
    por_cidade = {}
    for r in registros:
        por_cidade.setdefault(r['cidade'], []).append(int(r['minutos_atraso']))
    return {'fonte': 'CSV sintético do projeto; não representa telemetria real', 'total': len(valores), 'media_minutos': round(sum(valores)/len(valores),2) if valores else None, 'maior_atraso': max(valores, default=None), 'menor_atraso': min(valores, default=None), 'por_cidade': {k: round(sum(v)/len(v),2) for k,v in por_cidade.items()}}
