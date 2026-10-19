"""Rotas analíticas independentes das tabelas de cadastro do banco."""
import os
from typing import Literal

from fastapi import APIRouter, HTTPException
import analise

router = APIRouter(prefix="/ia", tags=["IA — Ciência de Dados"])

def fonte(estrita=True):
    try:
        dados, qualidade = analise.carregar(os.getenv("CSV_PATH", str(analise.DEFAULT_CSV)))
    except OSError as error:
        raise HTTPException(503, "CSV indisponível. Confira a fonte.") from error
    except (ValueError, UnicodeError) as error:
        raise HTTPException(422, "CSV inválido. Confira cabeçalho, datas e números.") from error
    if estrita and (dados.empty or qualidade["registros_excluidos"]
                    or qualidade["duplicatas_exatas_adicionais"]
                    or qualidade["codigos_com_nomes_divergentes"]):
        raise HTTPException(422, "Indicadores interrompidos por problema na fonte. Consulte /ia/qualidade.")
    return dados, qualidade

@router.get("/qualidade")
def qualidade():
    return fonte(estrita=False)[1]

@router.get("/resumo")
def resumo():
    dados, auditoria = fonte()
    return analise.resumo(dados, auditoria)

@router.get("/agrupamentos/{dimensao}")
def agrupamentos(dimensao: Literal["linha", "cidade", "data", "periodo", "transito", "clima", "trecho"]):
    dados, auditoria = fonte()
    return {"dimensao": dimensao, "fonte": auditoria["arquivo"],
            "sha256": auditoria["sha256"], "observacoes_validas": len(dados),
            "resultados": analise.agrupar(dados, dimensao)}

@router.get("/maiores-atrasos")
def maiores():
    dados, auditoria = fonte()
    return {"fonte": auditoria["arquivo"], "sha256": auditoria["sha256"],
            "empates_incluidos": True, "resultados": analise.maiores(dados)}
