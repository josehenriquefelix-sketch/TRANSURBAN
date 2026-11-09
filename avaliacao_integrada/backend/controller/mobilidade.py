"""GPS opt-in do motorista e avaliações da viagem."""
import os
import secrets
import sqlite3
import time
import json
from contextlib import closing, contextmanager
from pathlib import Path
from typing import Annotated, Literal
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field, StringConstraints, ConfigDict

from backend.database import get_supabase, modo_demo

def remoto():
    try:
        return get_supabase()
    except RuntimeError as erro:
        raise HTTPException(503, str(erro)) from erro

router = APIRouter(prefix="/mobilidade", tags=["Mobilidade"])
Codigo = Annotated[str, StringConstraints(pattern=r"^[A-Z0-9-]{1,20}$")]
Expira = 35
credencial = HTTPBearer(auto_error=False, scheme_name="Motorista")

class Viagem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    veiculo: Codigo
    linha: Codigo

class Posicao(Viagem):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    precisao: float = Field(ge=0, le=10000)
    gps_em: float

class Avaliacao(Viagem):
    nota: int = Field(ge=1, le=5, strict=True)
    lotacao: Literal["Vazio", "Normal", "Cheio"]
    descricao: Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=400)]

@contextmanager
def banco():
    pasta = Path(__file__).resolve().parents[2] / "data"
    caminho = os.getenv("TRANSURBAN_MOB_DB", str(pasta / "mobilidade.sqlite3"))
    with closing(sqlite3.connect(caminho)) as con, con:
        con.row_factory = sqlite3.Row
        con.executescript("""
        CREATE TABLE IF NOT EXISTS gps (
          veiculo TEXT PRIMARY KEY, linha TEXT NOT NULL, latitude REAL NOT NULL,
          longitude REAL NOT NULL, precisao REAL NOT NULL, gps_em REAL NOT NULL,
          recebido REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS avaliacoes (
          id INTEGER PRIMARY KEY, veiculo TEXT NOT NULL, linha TEXT NOT NULL,
          nota INTEGER NOT NULL, lotacao TEXT NOT NULL, descricao TEXT NOT NULL,
          criado REAL NOT NULL
        );
        """)
        yield con

def motorista(auth: Annotated[HTTPAuthorizationCredentials | None, Depends(credencial)]):
    authorization = auth.credentials if auth else None
    chave = os.getenv("TRANSURBAN_MOTORISTA_TOKEN", "")
    if len(chave) < 24:
        raise HTTPException(503, "O acesso de motorista ainda não foi configurado.")
    if not authorization or not secrets.compare_digest(authorization.encode(), chave.encode()):
        raise HTTPException(401, "Código de motorista inválido.")

@router.put("/gps", summary="Publicar localização do ônibus", responses={401: {"description": "Código inválido"}, 503: {"description": "Acesso de motorista não configurado"}})
def gps(p: Posicao, _motorista: Annotated[None, Depends(motorista)]):
    agora = time.time()
    if not agora - Expira <= p.gps_em <= agora + 15:
        raise HTTPException(422, "Leitura de GPS fora da janela de atualização.")
    if not modo_demo():
        remoto().rpc("transurban_publicar_gps", {"leitura": {**p.model_dump(), "recebido": agora}}).execute()
        return {"recebido": True}
    with banco() as con:
        con.execute("INSERT INTO gps VALUES(?,?,?,?,?,?,?) ON CONFLICT(veiculo) DO UPDATE SET linha=excluded.linha,latitude=excluded.latitude,longitude=excluded.longitude,precisao=excluded.precisao,gps_em=excluded.gps_em,recebido=excluded.recebido WHERE excluded.gps_em >= gps.gps_em", (p.veiculo,p.linha,p.latitude,p.longitude,p.precisao,p.gps_em,agora))
    return {"recebido": True}

@router.delete("/gps/{veiculo}", status_code=204, summary="Encerrar compartilhamento do ônibus")
def parar(veiculo: Codigo, _motorista: Annotated[None, Depends(motorista)]):
    if not modo_demo():
        remoto().table("transurban_gps").delete().eq("veiculo", veiculo).execute()
        return
    with banco() as con:
        con.execute("DELETE FROM gps WHERE veiculo=?", (veiculo,))

@router.get("/onibus", summary="Listar ônibus com posição recente na linha")
def onibus(linha: Codigo):
    if not modo_demo():
        return remoto().table("transurban_gps").select("*").eq("linha", linha).gte("gps_em", time.time()-Expira).order("veiculo").limit(100).execute().data
    with banco() as con:
        agora = time.time()
        con.execute("DELETE FROM gps WHERE gps_em < ?", (agora-Expira,))
        return [dict(r) for r in con.execute("SELECT * FROM gps WHERE linha=? ORDER BY veiculo LIMIT 100", (linha,))]

@router.get("/trajeto", summary="Consultar coordenadas do trajeto cadastrado")
def trajeto(linha: Codigo):
    arquivo = os.getenv("TRANSURBAN_TRAJETOS_JSON")
    if not arquivo:
        return {"pontos": []}
    try:
        pontos = json.loads(Path(arquivo).read_text(encoding="utf-8")).get(linha, [])
        if not isinstance(pontos, list) or any(not isinstance(p,list) or len(p)!=2 or not all(isinstance(n,(int,float)) for n in p) or not (-90<=p[0]<=90 and -180<=p[1]<=180) for p in pontos):
            raise ValueError()
        return {"pontos": pontos}
    except (OSError, ValueError, AttributeError):
        raise HTTPException(503, "Não foi possível carregar o trajeto configurado.")

@router.post("/avaliacoes", status_code=201, summary="Registrar nota, lotação e relato da viagem")
def avaliar(a: Avaliacao):
    if not modo_demo():
        dados = remoto().table("transurban_avaliacoes").insert({**a.model_dump(), "criado": time.time()}).execute().data
        if not dados:
            raise HTTPException(502, "O Supabase não confirmou a avaliação.")
        return {"id": dados[0]["id"]}
    with banco() as con:
        cur = con.execute("INSERT INTO avaliacoes(veiculo,linha,nota,lotacao,descricao,criado) VALUES(?,?,?,?,?,?)", (a.veiculo,a.linha,a.nota,a.lotacao,a.descricao,time.time()))
        return {"id": cur.lastrowid}

@router.get("/avaliacoes", summary="Listar avaliações recentes da linha")
def avaliacoes(linha: Codigo):
    if not modo_demo():
        return remoto().table("transurban_avaliacoes").select("veiculo,nota,lotacao,descricao").eq("linha", linha).order("id", desc=True).limit(10).execute().data
    with banco() as con:
        return [dict(r) for r in con.execute("SELECT veiculo, nota, lotacao, descricao FROM avaliacoes WHERE linha=? ORDER BY id DESC LIMIT 10", (linha,))]
