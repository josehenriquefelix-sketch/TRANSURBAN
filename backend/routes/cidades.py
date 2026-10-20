from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from database import get_db
from models import Cidade
from schemas import CidadeCreate, CidadeResponse
from services import salvar

router = APIRouter(prefix="/cidades", tags=["Cidades"], responses={503: {"description": "Banco indisponível ou estrutura incompatível"}})

@router.get("", response_model=list[CidadeResponse])
def listar_cidades(db: Session = Depends(get_db)):
    return db.scalars(select(Cidade).order_by(Cidade.id_cidade)).all()

@router.post("", response_model=CidadeResponse, status_code=201,
             responses={409: {"description": "Já existe uma cidade com esse nome"}})
def criar_cidade(dados: CidadeCreate, db: Session = Depends(get_db)):
    return salvar(db, Cidade(**dados.model_dump()))
