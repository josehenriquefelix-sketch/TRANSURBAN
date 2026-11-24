"""Contexto público e tratamento compartilhado de consultas HTTPS."""
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

router = APIRouter(prefix="/portal", tags=["Contexto público"])


@router.get("/contexto")
def contexto_oficial():
    arquivo = Path(__file__).resolve().parents[2] / "data" / "contexto_oficial.json"
    return json.loads(arquivo.read_text(encoding="utf-8"))


def executar(consulta):
    try:
        return consulta(get_supabase()).execute().data
    except APIError as erro:
        if erro.code in {"42P01", "PGRST205", "PGRST202"}:
            raise HTTPException(503, "Este serviço está em atualização. Tente novamente em instantes.") from erro
        if erro.code == "23505":
            raise HTTPException(409, "Este registro já existe.") from erro
        if erro.code == "P0001":
            raise HTTPException(409, "Operação recusada. Confira se o registro está ativo e se os dados atendem às regras da operação.") from erro
        raise
