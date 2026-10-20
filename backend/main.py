from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

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


@app.get("/")
def inicio():
    return {"mensagem": "API funcionando"}


@app.post(
    "/cidades",
    response_model=schemas.CidadeResponse
)
def criar_cidade(
    cidade: schemas.CidadeCreate,
    db: Session = Depends(get_db)
):
    nova_cidade = models.Cidade(
        nome=cidade.nome
    )

    db.add(nova_cidade)
    db.commit()
    db.refresh(nova_cidade)

    return nova_cidade


@app.get(
    "/cidades",
    response_model=list[schemas.CidadeResponse]
)
def listar_cidades(
    db: Session = Depends(get_db)
):
    return db.query(models.Cidade).all()
