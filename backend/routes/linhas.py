from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from database import get_db
from models import Cidade, LinhaOnibus
from schemas import LinhaCreate, LinhaResponse
from services import salvar

router = APIRouter(prefix="/linhas", tags=["Linhas"])

def representar(linha):
    return {"id_linha": linha.id_linha, "codigo": linha.codigo,
            "nome": linha.nome, "cidade": linha.cidade.nome}

@router.post("", response_model=LinhaResponse, status_code=201)
def criar_linha(dados: LinhaCreate, db: Session = Depends(get_db)):
    if db.get(Cidade, dados.id_cidade) is None:
        raise HTTPException(404, "Cidade não encontrada")
    return representar(salvar(db, LinhaOnibus(**dados.model_dump())))

@router.get("", response_model=list[LinhaResponse])
def listar_linhas(db: Session = Depends(get_db)):
    linhas = db.scalars(select(LinhaOnibus).options(
        joinedload(LinhaOnibus.cidade)).order_by(LinhaOnibus.id_linha)).all()
    return [representar(linha) for linha in linhas]
