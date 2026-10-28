"""CRUD HTTP da entidade independente cidade (PK sem FK)."""
from fastapi import APIRouter, HTTPException, Response, status
from postgrest.exceptions import APIError

from backend.database import get_supabase
from backend.models.cidade import CidadeEntrada, CidadeSaida

router = APIRouter(prefix="/cidades", tags=["Cidades · CRUD"])
TABELA = "cidade"
PK = "id_cidade"


def _executar(operacao):
    try:
        return operacao(get_supabase()).execute()
    except RuntimeError as erro:
        raise HTTPException(status_code=503, detail=str(erro)) from erro
    except APIError as erro:
        if getattr(erro, "code", None) in {"23505", "23503", "23514"}:
            raise HTTPException(409, "Conflito com uma regra de integridade do banco.") from erro
        raise


@router.post("", response_model=CidadeSaida, status_code=status.HTTP_201_CREATED)
def cadastrar_cidade(dados: CidadeEntrada):
    resposta = _executar(lambda db: db.table(TABELA).insert(dados.model_dump()))
    if not resposta.data:
        raise HTTPException(502, "O Supabase não retornou a cidade cadastrada.")
    return resposta.data[0]


@router.get("", response_model=list[CidadeSaida])
def listar_cidades():
    resposta = _executar(lambda db: db.table(TABELA).select("*").order(PK))
    return resposta.data


@router.get("/{id_cidade}", response_model=CidadeSaida)
def consultar_cidade(id_cidade: int):
    resposta = _executar(lambda db: db.table(TABELA).select("*").eq(PK, id_cidade).limit(1))
    if not resposta.data:
        raise HTTPException(404, "Cidade não encontrada.")
    return resposta.data[0]


@router.put("/{id_cidade}", response_model=CidadeSaida)
def atualizar_cidade(id_cidade: int, dados: CidadeEntrada):
    resposta = _executar(lambda db: db.table(TABELA).update(dados.model_dump()).eq(PK, id_cidade))
    if not resposta.data:
        raise HTTPException(404, "Cidade não encontrada.")
    return resposta.data[0]


@router.delete("/{id_cidade}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_cidade(id_cidade: int):
    resposta = _executar(lambda db: db.table(TABELA).delete().eq(PK, id_cidade))
    if not resposta.data:
        raise HTTPException(404, "Cidade não encontrada.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
