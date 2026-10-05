"""Executar na raiz: python -m uvicorn backend.main:app --reload."""
import os
from contextlib import asynccontextmanager
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from . import analise, models, schemas
from .database import Base, engine, get_db, IS_LOCAL

@asynccontextmanager
async def lifespan(app):
    # Só SQLite local recebe tabelas automaticamente. Supabase é inspecionado antes.
    if IS_LOCAL:
        Base.metadata.create_all(engine)
    yield
    engine.dispose()

app = FastAPI(title='TRANSURBAN — Avaliação Backend DS + IA', version='1.0.0', lifespan=lifespan)
DB = Annotated[Session, Depends(get_db)]

@app.exception_handler(SQLAlchemyError)
async def erro_banco(_request, _exception):
    return JSONResponse(status_code=503, content={'detail': 'Banco indisponível ou estrutura incompatível. Verifique a conexão e sql/01_auditar_supabase.sql.'})

@app.get('/', tags=['Sistema'])
def inicio():
    return {'projeto': 'TRANSURBAN', 'escopo': 'avaliação acadêmica DS + IA',
            'modo_banco': 'sqlite_local' if IS_LOCAL else 'postgresql',
            'docs': '/docs', 'dados_ia': 'CSV sintético; não é GPS em tempo real'}

@app.get('/health', tags=['Sistema'])
def health(db: DB):
    db.execute(text('SELECT 1'))
    return {'status': 'ok', 'banco': 'sqlite_local' if IS_LOCAL else 'postgresql'}

def salvar(db, registro):
    try:
        db.add(registro)
        db.commit()
        db.refresh(registro)
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, 'Registro duplicado ou conflito de integridade.')
    return registro

@app.post('/cidades', response_model=schemas.CidadeResponse, status_code=201, tags=['DS'])
def criar_cidade(v: schemas.CidadeCreate, db: DB):
    return salvar(db, models.Cidade(**v.model_dump()))

@app.get('/cidades', response_model=list[schemas.CidadeResponse], tags=['DS'])
def listar_cidades(db: DB, limite: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0)):
    return db.scalars(select(models.Cidade).order_by(models.Cidade.id_cidade).offset(offset).limit(limite)).all()

def linha_json(linha):
    return {'id_linha': linha.id_linha, 'id_cidade': linha.id_cidade,
            'codigo': linha.codigo, 'nome': linha.nome, 'cidade': linha.cidade.nome}

@app.post('/linhas', response_model=schemas.LinhaResponse, status_code=201, tags=['DS'])
def criar_linha(v: schemas.LinhaCreate, db: DB):
    cidade = db.get(models.Cidade, v.id_cidade)
    if cidade is None:
        raise HTTPException(404, 'Cidade não encontrada.')
    linha = salvar(db, models.LinhaOnibus(**v.model_dump()))
    return linha_json(linha)

@app.get('/linhas', response_model=list[schemas.LinhaResponse], tags=['DS'])
def listar_linhas(db: DB, id_cidade: int | None = Query(None, gt=0),
                  limite: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0)):
    query = select(models.LinhaOnibus).options(joinedload(models.LinhaOnibus.cidade))
    if id_cidade is not None:
        query = query.where(models.LinhaOnibus.id_cidade == id_cidade)
    linhas = db.scalars(query.order_by(models.LinhaOnibus.id_linha).offset(offset).limit(limite)).all()
    return [linha_json(linha) for linha in linhas]

@app.get('/linhas/{id_linha}', response_model=schemas.LinhaResponse, tags=['DS'])
def obter_linha(id_linha: int, db: DB):
    linha = db.get(models.LinhaOnibus, id_linha)
    if linha is None:
        raise HTTPException(404, 'Linha não encontrada.')
    return linha_json(linha)

def fonte(estrita=True):
    try:
        dados, qualidade = analise.carregar(os.getenv('CSV_PATH', str(analise.DEFAULT_CSV)))
    except OSError as exc:
        # Não expor caminho local, credenciais ou conteúdo bruto em resposta.
        raise HTTPException(503, 'CSV indisponível. Confira a fonte.') from exc
    except (ValueError, UnicodeError) as exc:
        raise HTTPException(422, 'CSV inválido. Confira cabeçalho, datas e números.') from exc
    if estrita and (qualidade['registros_lidos'] == 0 or qualidade['registros_excluidos'] > 0
                   or qualidade['duplicatas_exatas_adicionais'] > 0
                   or qualidade['codigos_com_nomes_divergentes'] > 0):
        raise HTTPException(422, 'Análise interrompida por problema na fonte. Consulte /ia/qualidade e corrija ou justifique os registros.')
    return dados, qualidade

@app.get('/ia/qualidade', tags=['IA'])
def qualidade():
    _, q = fonte(estrita=False)
    return q

@app.get('/ia/resumo', tags=['IA'])
def resumo():
    d, q = fonte()
    return analise.resumo(d, q)

@app.get('/ia/agrupamentos/{dimensao}', tags=['IA'])
def agrupamentos(dimensao: Literal['linha', 'cidade', 'data', 'periodo', 'transito', 'clima', 'trecho']):
    d, q = fonte()
    return {'dimensao': dimensao, 'fonte': q['arquivo'], 'sha256': q['sha256'],
            'observacoes_validas': len(d), 'resultados': analise.agrupar(d, dimensao)}

@app.get('/ia/maiores-atrasos', tags=['IA'])
def maiores_atrasos():
    d, q = fonte()
    return {'fonte': q['arquivo'], 'sha256': q['sha256'], 'empates_incluidos': True,
            'resultados': analise.maiores(d)}
