"""API acadêmica DS + IA. Executar: python -m uvicorn main:app."""
import os
from contextlib import asynccontextmanager
from typing import Annotated, Literal
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select, text, inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from database import ROOT, engine, SessionLocal, Base
from models import Cidade, Linha, Trecho, Percurso, Faixa, Atraso
from schemas import CidadeIn, LinhaIn, TrechoIn, PercursoIn, FaixaIn, AtrasoIn
import analise

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

app = FastAPI(title='TRANSURBAN — apresentação', version='2.2.0', lifespan=lifespan, description='Demonstração acadêmica. SQLite local ou PostgreSQL/Supabase configurado no backend. Sem login. CSV sintético.')
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

@app.get('/indicadores', tags=['IA'])
def indicadores():
    d, q = fonte()
    r = analise.resumo(d, q)
    grupos = analise.agrupar(d, 'cidade')
    return {
        'fonte': 'CSV sintético do projeto; não representa telemetria real',
        'total': r['observacoes_validas'],
        'media_minutos': round(r['atraso_medio_min'], 2),
        'mediana_minutos': r['atraso_mediano_min'],
        'soma_minutos_observacoes': r['atraso_total_min_observacoes'],
        'maior_atraso': r['maior_atraso_min'],
        'menor_atraso': float(d['minutos_atraso'].min()),
        'por_cidade': {g['cidade']: round(g['atraso_medio_min'], 2) for g in grupos},
        'sha256': q['sha256'],
        'limitacoes': r['limitacoes'],
    }
