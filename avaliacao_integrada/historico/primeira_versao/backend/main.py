from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import models
import schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API do Projeto Integrador",
    version="1.0.0"
)


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
    except IntegrityError as erro:
        db.rollback()
        if getattr(erro.orig, "pgcode", None) == "23505":
            raise HTTPException(409, "Registro já cadastrado") from erro
        if getattr(erro.orig, "pgcode", None) == "23503":
            raise HTTPException(404, "Cidade não encontrada") from erro
        raise


@app.get("/")
def inicio():
    return {"mensagem": "API funcionando"}


@app.post(
    "/cidades",
    response_model=schemas.CidadeResponse,
    responses={409: {"model": schemas.ErroResponse, "description": "Registro já cadastrado"}}
)
def criar_cidade(
    cidade: schemas.CidadeCreate,
    db: Session = Depends(get_db)
):
    nova_cidade = models.Cidade(
        nome=cidade.nome
    )

    salvar(db, nova_cidade)

    return nova_cidade


@app.get(
    "/cidades",
    response_model=list[schemas.CidadeResponse]
)
def listar_cidades(
    db: Session = Depends(get_db)
):
    return db.query(models.Cidade).all()


@app.post(
    "/linhas",
    response_model=schemas.LinhaOnibusResponse,
    responses={
        404: {"model": schemas.ErroResponse, "description": "Cidade não encontrada"},
        409: {"model": schemas.ErroResponse, "description": "Registro já cadastrado"}
    }
)
def criar_linha(
    linha: schemas.LinhaOnibusCreate,
    db: Session = Depends(get_db)
):
    cidade = (
        db.query(models.Cidade)
        .filter(
            models.Cidade.id_cidade
            == linha.id_cidade
        )
        .first()
    )

    if cidade is None:
        raise HTTPException(
            status_code=404,
            detail="Cidade não encontrada"
        )

    nova_linha = models.LinhaOnibus(
        nome=linha.nome,
        codigo=linha.codigo,
        id_cidade=linha.id_cidade
    )

    salvar(db, nova_linha)

    return {
        "id_linha": nova_linha.id_linha,
        "nome": nova_linha.nome,
        "codigo": nova_linha.codigo,
        "cidade": cidade.nome
    }


@app.get(
    "/linhas",
    response_model=list[schemas.LinhaOnibusResponse]
)
def listar_linhas(
    db: Session = Depends(get_db)
):
    linhas = db.query(models.LinhaOnibus).all()

    return [
        {
            "id_linha": linha.id_linha,
            "nome": linha.nome,
            "codigo": linha.codigo,
            "cidade": linha.cidade.nome
        }
        for linha in linhas
    ]
