"""Trajetos, avaliações e carteira demonstrativa persistidos no Supabase."""
from datetime import date, datetime, timedelta
from uuid import UUID
from zoneinfo import ZoneInfo
import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, ConfigDict, Field
from postgrest.exceptions import APIError

from backend.auth import usuario_atual
from backend.database import get_supabase

router = APIRouter(prefix="/portal", tags=["Mobilidade e passe"])


@router.get("/contexto")
def contexto_oficial():
    arquivo = Path(__file__).resolve().parents[2] / "data" / "contexto_oficial.json"
    return json.loads(arquivo.read_text(encoding="utf-8"))


def executar(consulta):
    try:
        return consulta(get_supabase()).execute().data
    except APIError as erro:
        if erro.code in {"42P01", "PGRST205", "PGRST202"}:
            raise HTTPException(503, "Módulo aguardando migrações do banco. Confira os scripts 05 e 06 da pasta database.") from erro
        if erro.code == "23505":
            raise HTTPException(409, "Este registro já existe.") from erro
        if erro.code == "P0001":
            raise HTTPException(409, "Operação recusada. Confira se o registro está ativo e se os dados atendem às regras da operação.") from erro
        raise


@router.get("/trajetos")
def trajetos():
    return executar(lambda db: db.table("tu_trajeto").select("*").order("id"))


@router.get("/horarios")
def horarios(trajeto_id: int = Query(gt=0), dia: date | None = None):
    dia = dia or datetime.now(ZoneInfo("America/Sao_Paulo")).date()
    rotas = executar(lambda db: db.table("tu_trajeto").select("*").eq("id", trajeto_id).limit(1))
    if not rotas:
        raise HTTPException(404, "Trajeto não encontrado.")
    registros = executar(lambda db: db.table("tu_horario").select("*").eq("trajeto_id", trajeto_id).order("partida"))
    resultado = []
    for registro in registros:
        if dia.isoweekday() not in registro["dias_semana"]:
            continue
        embarque = datetime.fromisoformat(f"{dia}T{registro['partida']}").replace(tzinfo=ZoneInfo("America/Sao_Paulo"))
        chegada = embarque + timedelta(minutes=rotas[0]["duracao_min"])
        resultado.append({**registro, "embarque": embarque.isoformat(), "chegada": chegada.isoformat(),
                          "paradas": [{**parada, "horario": (embarque + timedelta(minutes=parada["minutos"])).isoformat()}
                                      for parada in rotas[0]["paradas"]]})
    return {"trajeto": rotas[0], "dia": str(dia), "fonte": "Programação sintética acadêmica", "horarios": resultado}


class Avaliacao(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    horario_id: int = Field(gt=0)
    dia: date
    nota_onibus: int = Field(ge=1, le=5)
    nota_motorista: int = Field(ge=1, le=5)
    comentario: str = Field(default="", max_length=1000)


@router.get("/avaliacoes")
def avaliacoes(usuario=Depends(usuario_atual)):
    return executar(lambda db: db.table("tu_avaliacao").select("id,horario_id,dia,nota_onibus,nota_motorista,comentario,criado_em")
                    .eq("usuario_id", usuario["id"]).order("criado_em", desc=True))


@router.post("/avaliacoes", status_code=201)
def avaliar(dados: Avaliacao, usuario=Depends(usuario_atual)):
    hoje = datetime.now(ZoneInfo("America/Sao_Paulo")).date()
    if dados.dia > hoje:
        raise HTTPException(422, "Escolha uma data de hoje ou anterior para avaliar.")
    registros = executar(lambda db: db.table("tu_horario").select("id,dias_semana").eq("id", dados.horario_id).limit(1))
    if not registros or dados.dia.isoweekday() not in registros[0]["dias_semana"]:
        raise HTTPException(422, "Não há esse horário na data informada.")
    return executar(lambda db: db.table("tu_avaliacao").insert({**dados.model_dump(mode="json"), "usuario_id": usuario["id"]}))[0]


@router.delete("/avaliacoes/{avaliacao_id}", status_code=204)
def excluir_avaliacao(avaliacao_id: int, usuario=Depends(usuario_atual)):
    resultado = executar(lambda db: db.table("tu_avaliacao").delete().eq("id", avaliacao_id).eq("usuario_id", usuario["id"]))
    if not resultado:
        raise HTTPException(404, "Avaliação não encontrada.")
    return Response(status_code=204)


class Recarga(BaseModel):
    valor_centavos: int = Field(ge=500, le=20000, strict=True)
    chave: UUID


@router.get("/passe")
def passe(response: Response, usuario=Depends(usuario_atual)):
    response.headers["Cache-Control"] = "no-store"
    carteira = executar(lambda db: db.table("tu_carteira").select("numero,saldo_centavos").eq("usuario_id", usuario["id"]).limit(1))
    if not carteira:
        raise HTTPException(409, "Carteira ainda não criada. Confira a migração de contas.")
    movimentos = executar(lambda db: db.table("tu_recarga").select("id,valor_centavos,criado_em,chave")
                          .eq("usuario_id", usuario["id"]).order("criado_em", desc=True).limit(50))
    return {**carteira[0], "modo": "demonstracao", "recargas": movimentos,
            "aviso": "Saldo fictício para apresentação acadêmica. Sem cobrança ou crédito na bilhetagem real."}


@router.post("/recargas")
def recarregar(dados: Recarga, usuario=Depends(usuario_atual)):
    resultado = executar(lambda db: db.rpc("tu_recarregar_demo", {"p_usuario": usuario["id"],
                         "p_valor": dados.valor_centavos, "p_chave": str(dados.chave)}))
    return {"mensagem": "Recarga demonstrativa registrada.", "resultado": resultado, "modo": "demonstracao"}
