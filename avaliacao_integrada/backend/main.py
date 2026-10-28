"""FastAPI: CRUD Supabase por HTTPS e consultas pandas sobre CSV."""
import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from httpx import RequestError
from postgrest.exceptions import APIError

from backend.controller.analise import router as analise_router
from backend.controller.cidades import router as cidades_router
from backend.controller.linhas import router as linhas_router
from backend.database import supabase_configurado

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn.error")

app = FastAPI(
    title="TRANSURBAN · API integrada DS + IA",
    description=(
        "CRUD de cidades pela Data API HTTPS do Supabase e totalizações "
        "descritivas do CSV acadêmico com pandas."
    ),
    version="1.0.0",
)
origens = [
    origem.strip()
    for origem in os.getenv(
        "CORS_ORIGINS", "http://127.0.0.1:5500,http://localhost:5500"
    ).split(",")
    if origem.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origens,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"],
)
app.include_router(cidades_router)
app.include_router(linhas_router)
app.include_router(analise_router)


@app.get("/", tags=["Sistema"])
def inicio():
    return {
        "projeto": "TRANSURBAN",
        "supabase_configurado": supabase_configurado(),
        "documentacao": "/docs",
        "fonte_ia": "CSV sintético acadêmico; não é telemetria real",
    }


@app.exception_handler(APIError)
async def erro_supabase(_request: Request, erro: APIError):
    codigo = getattr(erro, "code", None)
    logger.error(
        "Falha Supabase (%s): %s",
        codigo or "sem código",
        getattr(erro, "message", "erro de API"),
    )
    status_code = 409 if codigo in {"23505", "23503", "23514"} else 502
    mensagem = (
        "Conflito com uma regra de integridade do banco."
        if status_code == 409
        else "O Supabase recusou a operação. Confira tabela, campos e permissões."
    )
    return JSONResponse(status_code=status_code, content={"detail": mensagem})


@app.exception_handler(RequestError)
async def erro_rede(_request: Request, erro: RequestError):
    logger.error("Falha de comunicação com o Supabase: %s", type(erro).__name__)
    return JSONResponse(
        status_code=503,
        content={
            "detail": "Não foi possível acessar o Supabase. Confira internet, URL e disponibilidade do projeto."
        },
    )


