"""Quatro rotas GET de totalização do CSV de atrasos."""
from fastapi import APIRouter, HTTPException
from backend import analise as calculos

router = APIRouter(prefix="/ia", tags=["Ciência de Dados · Totalizações"])


def _dados():
    try:
        dados, qualidade = calculos.carregar()
    except (OSError, ValueError) as erro:
        raise HTTPException(500, f"Não foi possível validar o CSV: {erro}") from erro
    if qualidade["registros_excluidos"] or qualidade["duplicatas_exatas_adicionais"]:
        raise HTTPException(500, "O CSV contém linhas inválidas ou duplicadas; revise a fonte antes das totalizações.")
    return dados, qualidade


@router.get("/resumo")
def resumo():
    dados, qualidade = _dados()
    return calculos.resumo(dados, qualidade)


@router.get("/totalizacao/cidade")
def totalizar_por_cidade():
    dados, _ = _dados()
    return calculos.agrupar(dados, "cidade")


@router.get("/totalizacao/periodo")
def totalizar_por_periodo():
    dados, _ = _dados()
    return calculos.agrupar(dados, "periodo")


@router.get("/totalizacao/transito")
def totalizar_por_transito():
    dados, _ = _dados()
    return calculos.agrupar(dados, "transito")


@router.get("/totalizacao/clima")
def totalizar_por_clima():
    dados, _ = _dados()
    return calculos.agrupar(dados, "clima")
