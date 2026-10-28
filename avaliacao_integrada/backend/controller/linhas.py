"""CRUD de linhas para a interface integrada; preserva a FK para cidade."""
from fastapi import APIRouter, HTTPException, Response, status
from postgrest.exceptions import APIError

from backend.database import get_supabase
from backend.models.linha import LinhaEntrada, LinhaSaida

router = APIRouter(prefix="/linhas", tags=["Linhas · integração"])
TABELA = "linha_onibus"
PK = "id_linha"
COLUNAS = "id_linha,id_cidade,codigo,nome,cidade(nome)"


def _executar(operacao):
    try:
        return operacao(get_supabase()).execute()
    except RuntimeError as erro:
        raise HTTPException(status_code=503, detail=str(erro)) from erro
    except APIError as erro:
        if getattr(erro, "code", None) in {"23505", "23503", "23514"}:
            raise HTTPException(409, "Conflito com uma regra de integridade do banco.") from erro
        raise


def _representar(registro):
    registro = dict(registro)
    cidade = registro.get("cidade")
    if isinstance(cidade, list):
        cidade = cidade[0] if cidade else None
    registro["cidade"] = cidade.get("nome", "") if isinstance(cidade, dict) else ""
    return registro


def _validar_cidade(id_cidade):
    resposta = _executar(
        lambda db: db.table("cidade").select("id_cidade").eq("id_cidade", id_cidade).limit(1)
    )
    if not resposta.data:
        raise HTTPException(404, "Cidade vinculada não encontrada.")


@router.post("", response_model=LinhaSaida, status_code=status.HTTP_201_CREATED)
def cadastrar_linha(dados: LinhaEntrada):
    _validar_cidade(dados.id_cidade)
    resposta = _executar(
        lambda db: db.table(TABELA).insert(dados.model_dump()).select(COLUNAS)
    )
    if not resposta.data:
        raise HTTPException(502, "O Supabase não retornou a linha cadastrada.")
    return _representar(resposta.data[0])


@router.get("", response_model=list[LinhaSaida])
def listar_linhas():
    resposta = _executar(
        lambda db: db.table(TABELA).select(COLUNAS).order(PK)
    )
    return [_representar(registro) for registro in resposta.data]


@router.get("/{id_linha}", response_model=LinhaSaida)
def consultar_linha(id_linha: int):
    resposta = _executar(
        lambda db: db.table(TABELA).select(COLUNAS).eq(PK, id_linha).limit(1)
    )
    if not resposta.data:
        raise HTTPException(404, "Linha não encontrada.")
    return _representar(resposta.data[0])


@router.put("/{id_linha}", response_model=LinhaSaida)
def atualizar_linha(id_linha: int, dados: LinhaEntrada):
    _validar_cidade(dados.id_cidade)
    resposta = _executar(
        lambda db: db.table(TABELA).update(dados.model_dump()).eq(PK, id_linha).select(COLUNAS)
    )
    if not resposta.data:
        raise HTTPException(404, "Linha não encontrada.")
    return _representar(resposta.data[0])


@router.delete("/{id_linha}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_linha(id_linha: int):
    resposta = _executar(
        lambda db: db.table(TABELA).delete().eq(PK, id_linha).select(PK)
    )
    if not resposta.data:
        raise HTTPException(404, "Linha não encontrada.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
