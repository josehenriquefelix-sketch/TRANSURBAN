"""Atendimento por usuário e escopo, alertas confirmados e aprovação administrativa."""
from datetime import datetime, timedelta, timezone
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.auth import usuario_atual, motorista_autorizado, gestor_autorizado, administrador
from backend.controller.mobilidade import linha_validada, escopos_gestao
from backend.controller.portal import executar

router = APIRouter(prefix="/atendimento", tags=["Suporte e operação"])


class Local(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    cidade: Literal["Maringá", "Sarandi"]
    linha_id: str | None = Field(default=None, max_length=100)
    latitude: float | None = Field(default=None, ge=-90, le=90, allow_inf_nan=False)
    longitude: float | None = Field(default=None, ge=-180, le=180, allow_inf_nan=False)

    @model_validator(mode="after")
    def coordenadas_completas(self):
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("Informe as duas coordenadas ou deixe o local em branco.")
        return self


def competencia(dados):
    if dados.linha_id:
        linha = linha_validada(dados.linha_id)
        if dados.cidade not in linha["cidades"]:
            raise HTTPException(422, "A linha não atende à cidade informada.")
        return linha["ambito"]
    return "maringa" if dados.cidade == "Maringá" else "sarandi"


class Chamado(Local):
    categoria: Literal["Acessibilidade", "Atendimento", "Trânsito", "Obras", "Desvio", "Segurança", "Outros"]
    assunto: str = Field(min_length=5, max_length=120)
    mensagem: str = Field(min_length=10, max_length=2000)


def gravar_chamado(dados, usuario, perfil):
    escopo = competencia(dados)
    registro = executar(lambda db: db.table("tu_chamado").insert({**dados.model_dump(), "usuario_id": usuario["id"],
                      "perfil": perfil, "competencia": escopo}))[0]
    return {"id": registro["id"], "protocolo": f"SUP-{registro['numero']:06d}", "status": registro["status"]}


@router.post("/passageiro/chamados", status_code=201)
def chamado_passageiro(dados: Chamado, usuario=Depends(usuario_atual)):
    return gravar_chamado(dados, usuario, "passageiro")


@router.post("/motorista/chamados", status_code=201)
def chamado_motorista(dados: Chamado, usuario=Depends(motorista_autorizado)):
    return gravar_chamado(dados, usuario, "motorista")


@router.get("/meus-chamados")
def meus_chamados(usuario=Depends(usuario_atual)):
    return executar(lambda db: db.table("tu_chamado").select("id,numero,perfil,cidade,linha_id,categoria,assunto,mensagem,status,resposta,criado_em")
                    .eq("usuario_id", usuario["id"]).order("criado_em", desc=True).limit(100))


@router.get("/gestao/chamados")
def chamados_gestao(usuario=Depends(gestor_autorizado)):
    return executar(lambda db: db.table("tu_chamado").select("*").in_("competencia", escopos_gestao(usuario))
                    .order("criado_em", desc=True).limit(500))


class Resposta(BaseModel):
    status: Literal["em_analise", "respondido", "encerrado"]
    resposta: str = Field(min_length=10, max_length=2000)


@router.put("/gestao/chamados/{chamado_id}")
def responder(chamado_id: UUID, dados: Resposta, usuario=Depends(gestor_autorizado)):
    registros = executar(lambda db: db.table("tu_chamado").select("competencia").eq("id", str(chamado_id)).limit(1))
    if not registros or registros[0]["competencia"] not in escopos_gestao(usuario):
        raise HTTPException(404, "Chamado não disponível no seu escopo.")
    return executar(lambda db: db.rpc("tu_responder_chamado", {"p_chamado": str(chamado_id), "p_autor": usuario["id"],
                    "p_status": dados.status, "p_resposta": dados.resposta.strip()}))


class Alerta(Local):
    nivel: Literal["vermelho", "amarelo", "verde"]
    titulo: str = Field(min_length=5, max_length=120)
    orientacao: str = Field(min_length=10, max_length=1000)
    validade_horas: int = Field(default=2, ge=1, le=24)


@router.get("/alertas")
def alertas(cidade: Literal["Maringá", "Sarandi"] | None = None):
    def consulta(db):
        q = db.table("tu_alerta_operacional").select("id,cidade,linha_id,nivel,titulo,orientacao,latitude,longitude,criado_em,expira_em")
        q = q.eq("ativo", True).gt("expira_em", datetime.now(timezone.utc).isoformat())
        return q.eq("cidade", cidade).order("criado_em", desc=True).limit(300) if cidade else q.order("criado_em", desc=True).limit(300)
    return executar(consulta)


@router.post("/gestao/alertas", status_code=201)
def publicar_alerta(dados: Alerta, usuario=Depends(gestor_autorizado)):
    escopo = competencia(dados)
    if escopo not in escopos_gestao(usuario):
        raise HTTPException(403, "A ocorrência está fora do seu escopo de gestão.")
    if dados.latitude is None:
        raise HTTPException(422, "Marque no mapa o local da ocorrência.")
    valores = dados.model_dump(exclude={"validade_horas"})
    valores.update(autor_id=usuario["id"], competencia=escopo,
                   expira_em=(datetime.now(timezone.utc)+timedelta(hours=dados.validade_horas)).isoformat())
    registro = executar(lambda db: db.table("tu_alerta_operacional").insert(valores))[0]
    return {"id": registro["id"], "mensagem": "Ocorrência confirmada publicada. A orientação não altera automaticamente o itinerário oficial."}


@router.delete("/gestao/alertas/{alerta_id}")
def retirar_alerta(alerta_id: UUID, usuario=Depends(gestor_autorizado)):
    registros = executar(lambda db: db.table("tu_alerta_operacional").update({"ativo": False}).eq("id", str(alerta_id))
                        .in_("competencia", escopos_gestao(usuario)))
    if not registros:
        raise HTTPException(404, "Ocorrência não disponível no seu escopo.")
    return {"mensagem": "Ocorrência retirada do mapa."}


class Pedido(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    papel: Literal["motorista", "gestor"]
    justificativa: str = Field(min_length=10, max_length=1000)


@router.post("/pedidos-acesso", status_code=201)
def pedir_acesso(dados: Pedido, usuario=Depends(usuario_atual)):
    # Inserção simples: um novo pedido nunca concede ou modifica papéis.
    registro = executar(lambda db: db.table("tu_pedido_acesso").insert({**dados.model_dump(), "usuario_id": usuario["id"]}))[0]
    return {"id": registro["id"], "status": registro["status"], "mensagem": "Pedido recebido. O acesso profissional depende de análise e aprovação."}


@router.get("/meus-pedidos")
def meus_pedidos(usuario=Depends(usuario_atual)):
    return executar(lambda db: db.table("tu_pedido_acesso").select("id,papel,status,decisao,criado_em,decidido_em")
                    .eq("usuario_id", usuario["id"]))


@router.get("/gestao/pedidos-acesso")
def pedidos_administracao(usuario=Depends(administrador)):
    pedidos = executar(lambda db: db.table("tu_pedido_acesso").select("*").order("criado_em", desc=True).limit(200))
    ids = list({p["usuario_id"] for p in pedidos})
    perfis = executar(lambda db: db.table("tu_perfil").select("usuario_id,nome,email").in_("usuario_id", ids)) if ids else []
    por_id = {p["usuario_id"]: p for p in perfis}
    return [{**p, "solicitante": por_id.get(p["usuario_id"], {})} for p in pedidos]


class Decisao(BaseModel):
    aprovar: bool
    escopo: Literal["maringa", "sarandi", "metropolitano", "todos"]
    decisao: str = Field(min_length=10, max_length=1000)


@router.put("/gestao/pedidos-acesso/{pedido_id}")
def decidir_acesso(pedido_id: UUID, dados: Decisao, usuario=Depends(administrador)):
    return executar(lambda db: db.rpc("tu_decidir_acesso", {"p_pedido": str(pedido_id), "p_revisor": usuario["id"],
                    "p_aprovar": dados.aprovar, "p_escopo": dados.escopo, "p_decisao": dados.decisao.strip()}))
