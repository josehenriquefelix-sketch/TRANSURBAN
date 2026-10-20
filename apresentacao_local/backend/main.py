from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
import models
import schemas
from database import Base, SessionLocal, engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="API TRANSURBAN", version="1.0.0", lifespan=lifespan)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def salvar(db, registro):
    try:
        db.add(registro)
        db.commit()
        db.refresh(registro)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Cadastro viola uma restrição do banco.")

def resposta_linha(linha):
    return {"id_linha": linha.id_linha, "codigo": linha.codigo, "nome": linha.nome,
            "id_cidade": linha.id_cidade, "cidade": linha.cidade.nome}

@app.get("/")
def inicio():
    return {"mensagem": "API TRANSURBAN funcionando"}

@app.post("/cidades", response_model=schemas.CidadeResponse, status_code=201)
def criar_cidade(cidade: schemas.CidadeCreate, db: Session = Depends(get_db)):
    nova = models.Cidade(nome=cidade.nome)
    salvar(db, nova)
    return nova

@app.get("/cidades", response_model=list[schemas.CidadeResponse])
def listar_cidades(db: Session = Depends(get_db)):
    return db.scalars(select(models.Cidade).order_by(models.Cidade.id_cidade)).all()

@app.post("/linhas", response_model=schemas.LinhaResponse, status_code=201)
def criar_linha(linha: schemas.LinhaCreate, db: Session = Depends(get_db)):
    cidade = db.get(models.Cidade, linha.id_cidade)
    if cidade is None:
        raise HTTPException(status_code=404, detail="Cidade não encontrada")
    nova = models.LinhaOnibus(codigo=linha.codigo, nome=linha.nome, id_cidade=cidade.id_cidade)
    salvar(db, nova)
    return resposta_linha(nova)

@app.get("/linhas", response_model=list[schemas.LinhaResponse])
def listar_linhas(db: Session = Depends(get_db)):
    consulta = select(models.LinhaOnibus).options(joinedload(models.LinhaOnibus.cidade)).order_by(models.LinhaOnibus.id_linha)
    return [resposta_linha(linha) for linha in db.scalars(consulta).all()]
