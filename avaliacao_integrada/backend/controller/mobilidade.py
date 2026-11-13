"""Catálogo documentado, favoritos, rastreamento consentido e atendimento."""
import json
import os
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.auth import usuario_atual, motorista_autorizado, gestor_autorizado
from backend.controller.portal import executar

router = APIRouter(prefix="/mobilidade", tags=["TRANSURBAN · Mobilidade"])
CATALOGO = Path(__file__).resolve().parents[2] / "data" / "catalogo_publico_verificado.json"
SENTIDOS = ("Maringá → Sarandi", "Sarandi → Maringá")


def catalogo():
    return json.loads(CATALOGO.read_text(encoding="utf-8"))


def linha_validada(linha_id):
    linha = next((linha for linha in catalogo()["linhas"] if linha["id"] == linha_id), None)
    if not linha:
        raise HTTPException(404, "Linha não encontrada no catálogo documentado.")
    return linha


@router.get("/catalogo")
def consultar_catalogo():
    return catalogo()


@router.get("/horarios/{linha_id}")
def consultar_horarios(linha_id: str, tipo_dia: Literal["dias_uteis", "sabado", "domingo_feriado"] = "dias_uteis", sentido: str | None = None):
    linha = linha_validada(linha_id)
    sentido = sentido or linha.get("sentidos", SENTIDOS)[0]
    if sentido not in linha.get("sentidos", SENTIDOS):
        raise HTTPException(422, "Selecione um sentido válido.")
    horarios = [horario for horario in linha["horarios"] if horario["sentido"] == sentido and horario["tipo_dia"] == tipo_dia]
    horarios.sort(key=lambda horario: horario["partida"])
    return {"linha": linha, "horarios": horarios, "previsao_ao_vivo": None,
            "aviso": "Partidas do documento oficial. Confirme feriados e alterações com a operadora. A previsão de chegada ao ponto depende de telemetria e rota validadas."}


@router.get("/favoritos")
def favoritos(usuario=Depends(usuario_atual)):
    ids = executar(lambda db: db.table("tu_favorito").select("linha_id").eq("usuario_id", usuario["id"]))
    return [linha for linha in catalogo()["linhas"] if linha["id"] in {registro["linha_id"] for registro in ids}]


@router.put("/favoritos/{linha_id}")
def favoritar(linha_id: str, usuario=Depends(usuario_atual)):
    linha_validada(linha_id)
    executar(lambda db: db.table("tu_favorito").upsert({"usuario_id": usuario["id"], "linha_id": linha_id}, on_conflict="usuario_id,linha_id"))
    return {"mensagem": "Linha salva em Minhas linhas."}


@router.delete("/favoritos/{linha_id}", status_code=204)
def desfavoritar(linha_id: str, usuario=Depends(usuario_atual)):
    executar(lambda db: db.table("tu_favorito").delete().eq("usuario_id", usuario["id"]).eq("linha_id", linha_id))
    return Response(status_code=204)


class PerfilMotorista(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    nome_publico: str = Field(min_length=2, max_length=100)
    ano_nascimento: int | None = None
    bio: str = Field(default="", max_length=240)
    exibir_perfil: bool = False
    modelo: str = Field(min_length=2, max_length=100)
    prefixo: str = Field(min_length=1, max_length=30)

    @field_validator("ano_nascimento")
    @classmethod
    def validar_idade(cls, valor):
        if valor is not None and not 18 <= date.today().year - valor <= 100:
            raise ValueError("Informe um ano de nascimento compatível com um motorista adulto.")
        return valor


def indicadores_motorista(usuario_id):
    registros = executar(lambda db: db.table("tu_manifestacao").select("tipo,nota_motorista").eq("motorista_id", usuario_id))
    notas = [registro["nota_motorista"] for registro in registros if registro["nota_motorista"] is not None]
    return {"avaliacao": round(sum(notas) / len(notas), 1) if notas else None,
            "quantidade_notas": len(notas), "elogios": sum(r["tipo"] == "elogio" for r in registros),
            "reclamacoes": sum(r["tipo"] == "reclamacao" for r in registros)}


@router.get("/motorista")
def painel_motorista(usuario=Depends(motorista_autorizado)):
    perfil = executar(lambda db: db.table("tu_motorista").select("*").eq("usuario_id", usuario["id"]).limit(1))
    viagens = executar(lambda db: db.table("tu_viagem_operacional").select("*").eq("motorista_id", usuario["id"]).eq("status", "ativa").limit(1))
    relatos = executar(lambda db: db.table("tu_manifestacao").select("numero,tipo,categoria,relato,nota_motorista,criada_em,status")
                       .eq("motorista_id", usuario["id"]).order("criada_em", desc=True).limit(50))
    return {"perfil": perfil[0] if perfil else None, "viagem": viagens[0] if viagens else None,
            "indicadores": indicadores_motorista(usuario["id"]), "avaliacoes": relatos}


@router.put("/motorista/perfil")
def atualizar_perfil(dados: PerfilMotorista, usuario=Depends(motorista_autorizado)):
    ativa = executar(lambda db: db.table("tu_viagem_operacional").select("id").eq("motorista_id", usuario["id"]).eq("status", "ativa").limit(1))
    if ativa:
        raise HTTPException(409, "Encerre a viagem antes de alterar o veículo ou o perfil.")
    return executar(lambda db: db.table("tu_motorista").upsert({"usuario_id": usuario["id"], **dados.model_dump(), "atualizado_em": datetime.now(timezone.utc).isoformat()}))[0]


class InicioViagem(BaseModel):
    linha_id: str
    sentido: str = Field(min_length=1, max_length=100)


@router.post("/motorista/viagens", status_code=201)
def iniciar_viagem(dados: InicioViagem, usuario=Depends(motorista_autorizado)):
    linha = linha_validada(dados.linha_id)
    if dados.sentido not in linha.get("sentidos", SENTIDOS):
        raise HTTPException(422, "Selecione um sentido válido para esta linha.")
    perfis = executar(lambda db: db.table("tu_motorista").select("*").eq("usuario_id", usuario["id"]).limit(1))
    if not perfis:
        raise HTTPException(409, "Configure seu perfil e o veículo antes de iniciar.")
    perfil = perfis[0]
    return executar(lambda db: db.table("tu_viagem_operacional").insert({"motorista_id": usuario["id"],
                    "linha_id": dados.linha_id, "sentido": dados.sentido, "prefixo": perfil["prefixo"], "modelo": perfil["modelo"]}))[0]


@router.post("/motorista/viagens/{viagem_id}/encerrar")
def encerrar_viagem(viagem_id: UUID, usuario=Depends(motorista_autorizado)):
    registros = executar(lambda db: db.table("tu_viagem_operacional").update({"status": "encerrada", "encerrada_em": datetime.now(timezone.utc).isoformat()})
                         .eq("id", str(viagem_id)).eq("motorista_id", usuario["id"]).eq("status", "ativa"))
    if not registros:
        raise HTTPException(409, "A viagem não está ativa ou não pertence à sua conta.")
    return {"mensagem": "Trajeto encerrado. Compartilhamento de posição finalizado."}


class Posicao(BaseModel):
    latitude: float = Field(ge=-90, le=90, allow_inf_nan=False)
    longitude: float = Field(ge=-180, le=180, allow_inf_nan=False)
    precisao_m: float = Field(ge=0, le=1000, allow_inf_nan=False)
    direcao: float | None = Field(default=None, ge=0, le=360, allow_inf_nan=False)


@router.post("/motorista/viagens/{viagem_id}/posicao")
def compartilhar_posicao(viagem_id: UUID, dados: Posicao, usuario=Depends(motorista_autorizado)):
    executar(lambda db: db.rpc("tu_registrar_posicao", {"p_viagem": str(viagem_id), "p_motorista": usuario["id"],
             "p_lat": dados.latitude, "p_lon": dados.longitude, "p_precisao": dados.precisao_m, "p_direcao": dados.direcao}))
    return {"mensagem": "Posição recebida."}


@router.get("/viagens")
def viagens_publicas(linha_id: str | None = None):
    def consulta(db):
        query = db.table("tu_viagem_operacional").select("id,motorista_id,linha_id,sentido,prefixo,modelo,iniciada_em").eq("status", "ativa")
        return query.eq("linha_id", linha_id) if linha_id else query
    viagens = executar(consulta)
    if not viagens:
        return []
    ids = [viagem["id"] for viagem in viagens]
    posicoes = executar(lambda db: db.table("tu_posicao_atual").select("*").in_("viagem_id", ids))
    perfis = executar(lambda db: db.table("tu_motorista").select("usuario_id,nome_publico,bio,ano_nascimento,exibir_perfil").in_("usuario_id", [v["motorista_id"] for v in viagens]))
    perfis = {p["usuario_id"]: p for p in perfis}
    por_viagem = {posicao["viagem_id"]: posicao for posicao in posicoes}
    for viagem in viagens:
        motorista_id = viagem.pop("motorista_id")
        perfil = perfis.get(motorista_id, {})
        viagem["motorista"] = None
        if perfil.get("exibir_perfil"):
            viagem["motorista"] = {"nome": perfil["nome_publico"], "bio": perfil["bio"],
                "idade_aproximada": date.today().year - perfil["ano_nascimento"] if perfil.get("ano_nascimento") else None,
                **indicadores_motorista(motorista_id)}
        posicao = por_viagem.get(viagem["id"])
        if posicao:
            instante = datetime.fromisoformat(posicao["registrada_em"].replace("Z", "+00:00"))
            posicao["recente"] = (datetime.now(timezone.utc) - instante).total_seconds() < 90
        viagem["posicao"] = posicao
    return viagens


class Manifestacao(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    linha_id: str
    viagem_id: UUID | None = None
    cidade: Literal["Maringá", "Sarandi"]
    tipo: Literal["elogio", "reclamacao", "sugestao"]
    categoria: Literal["Pontualidade", "Conforto", "Acessibilidade", "Atendimento", "Segurança", "Outros"]
    nota_onibus: int | None = Field(default=None, ge=1, le=5)
    nota_motorista: int | None = Field(default=None, ge=1, le=5)
    relato: str = Field(min_length=10, max_length=2000)


@router.post("/manifestacoes", status_code=201)
def enviar_manifestacao(dados: Manifestacao, usuario=Depends(usuario_atual)):
    linha = linha_validada(dados.linha_id)
    if dados.cidade not in linha["cidades"]:
        raise HTTPException(422, "A linha selecionada não atende à cidade informada.")
    motorista_id = None
    if dados.viagem_id:
        viagens = executar(lambda db: db.table("tu_viagem_operacional").select("motorista_id,linha_id").eq("id", str(dados.viagem_id)).limit(1))
        if not viagens or viagens[0]["linha_id"] != dados.linha_id:
            raise HTTPException(422, "A viagem selecionada não pertence à linha informada.")
        motorista_id = viagens[0]["motorista_id"]
        if motorista_id == usuario["id"]:
            raise HTTPException(422, "O motorista não pode avaliar a própria viagem.")
    elif dados.nota_motorista is not None:
        raise HTTPException(422, "Vincule uma viagem para avaliar um motorista identificado.")
    registro = executar(lambda db: db.table("tu_manifestacao").insert({**dados.model_dump(mode="json"),
                        "usuario_id": usuario["id"], "motorista_id": motorista_id,
                        "competencia": linha["ambito"]}))[0]
    return {"id": registro["id"], "protocolo": f"TU-{registro['numero']:06d}", "status": registro["status"],
            "mensagem": "Manifestação recebida na central TRANSURBAN. O protocolo é da plataforma. O encaminhamento institucional depende de adesão do órgão responsável."}


@router.get("/minhas-manifestacoes")
def minhas_manifestacoes(usuario=Depends(usuario_atual)):
    return executar(lambda db: db.table("tu_manifestacao").select("id,numero,linha_id,tipo,categoria,relato,status,resposta,criada_em")
                    .eq("usuario_id", usuario["id"]).order("criada_em", desc=True).limit(100))


def escopos_gestao(usuario):
    admins = {e.strip().lower() for e in os.getenv("ADMIN_EMAILS", "").split(",") if e.strip()}
    if (usuario.get("email") or "").lower() in admins:
        return ["maringa", "sarandi", "metropolitano"]
    acessos = executar(lambda db: db.table("tu_acesso").select("escopo").eq("usuario_id", usuario["id"]).eq("papel", "gestor").eq("ativo", True))
    escopos = [r["escopo"] for r in acessos]
    return ["maringa", "sarandi", "metropolitano"] if "todos" in escopos else escopos


@router.get("/gestao/manifestacoes")
def fila_gestao(usuario=Depends(gestor_autorizado)):
    escopos = escopos_gestao(usuario)
    if not escopos:
        return []
    return executar(lambda db: db.table("tu_manifestacao").select("id,numero,linha_id,cidade,competencia,tipo,categoria,nota_onibus,nota_motorista,relato,status,resposta,criada_em")
                    .in_("competencia", escopos).order("criada_em", desc=True).limit(500))


class Atendimento(BaseModel):
    status: Literal["em_analise", "respondida", "encerrada"]
    resposta: str = Field(default="", max_length=2000)


@router.put("/gestao/manifestacoes/{manifestacao_id}")
def responder_manifestacao(manifestacao_id: UUID, dados: Atendimento, usuario=Depends(gestor_autorizado)):
    registros = executar(lambda db: db.table("tu_manifestacao").select("competencia").eq("id", str(manifestacao_id)).limit(1))
    if not registros or registros[0]["competencia"] not in escopos_gestao(usuario):
        raise HTTPException(404, "Manifestação não disponível no seu escopo de gestão.")
    return executar(lambda db: db.rpc("tu_responder_manifestacao", {"p_id": str(manifestacao_id), "p_autor": usuario["id"],
                    "p_status": dados.status, "p_resposta": dados.resposta.strip()}))
