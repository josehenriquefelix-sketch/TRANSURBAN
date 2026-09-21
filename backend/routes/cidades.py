from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from models import Cidade
from schemas import CidadeCreate, CidadeResponse

router = APIRouter(prefix="/cidades", tags=["cidades"])


@router.get("/", response_model=list[CidadeResponse])
def listar_cidades(db: Session = Depends(get_db)):
    return db.scalars(
        select(Cidade).order_by(Cidade.id_cidade)
    ).all()


@router.post(
    "/",
    response_model=CidadeResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_cidade(
    dados: CidadeCreate,
    db: Session = Depends(get_db),
):
    if db.get(Cidade, dados.id_cidade):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe uma cidade com esse id_cidade.",
        )

    nome_existente = db.scalar(
        select(Cidade).where(Cidade.nome == dados.nome)
    )
    if nome_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe uma cidade com esse nome.",
        )

    cidade = Cidade(
        id_cidade=dados.id_cidade,
        nome=dados.nome,
    )
    db.add(cidade)

    try:
        db.commit()
        db.refresh(cidade)
        return cidade
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Não foi possível cadastrar a cidade. "
                "Verifique os dados enviados."
            ),
        )
