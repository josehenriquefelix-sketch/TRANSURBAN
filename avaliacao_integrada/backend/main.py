"""FastAPI: CRUD de cidades e linhas via Supabase."""
import ctypes
import logging
import os
from pathlib import Path
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from httpx import RequestError
from postgrest.exceptions import APIError

from backend.controller.cidades import router as cidades_router
from backend.controller.linhas import router as linhas_router
from backend.database import supabase_configurado, get_supabase, modo_demo

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn.error")

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


@asynccontextmanager
async def manter_computador_ativo(_app):
    restaurar_estado = None
    if os.name == "nt":
        try:
            kernel = ctypes.WinDLL("kernel32", use_last_error=True)
            definir_estado = kernel.SetThreadExecutionState
            definir_estado.argtypes = [ctypes.c_uint]
            definir_estado.restype = ctypes.c_uint
            estado_continuo = 0x80000000
            estado_sistema_ativo = 0x00000001
            if definir_estado(estado_continuo | estado_sistema_ativo):
                restaurar_estado = definir_estado
            else:
                logger.warning("Nao foi possivel solicitar que o Windows mantenha o sistema ativo.")
        except (AttributeError, OSError) as erro:
            logger.warning("Solicitacao temporaria de sistema ativo indisponivel: %s", type(erro).__name__)
    try:
        yield
    finally:
        if restaurar_estado is not None:
            restaurar_estado(0x80000000)

app = FastAPI(
    title="TRANSURBAN · API de cadastros",
    description=(
        "CRUD de cidades e linhas pela Data API HTTPS do Supabase."
    ),
    version="1.0.0",
    lifespan=manter_computador_ativo,
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


@app.get("/health", tags=["Sistema"])
def health():
    return {
        "projeto": "TRANSURBAN",
        "supabase_configurado": supabase_configurado(),
        "interface": "/",
        "documentacao": "/docs",
    }


@app.get("/health/banco", tags=["Sistema"])
def health_banco():
    try:
        db = get_supabase()
        db.table("cidade").select("id_cidade").limit(1).execute()
        db.table("linha_onibus").select("id_linha,cidade(nome)").limit(1).execute()
    except RuntimeError as erro:
        raise HTTPException(503, str(erro)) from erro
    return {"conectado": True, "modo": "demo" if modo_demo() else "supabase"}


@app.get("/", tags=["Sistema"], include_in_schema=False)
def inicio():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.exception_handler(APIError)
async def erro_supabase(_request: Request, erro: APIError):
    codigo = getattr(erro, "code", None)
    logger.error(
        "Falha Supabase (%s): %s",
        codigo or "sem código",
        getattr(erro, "message", "erro de API"),
    )
    if codigo == "23503":
        return JSONResponse(
            status_code=409,
            content={
                "detail": (
                    "A operação foi bloqueada por uma chave estrangeira. "
                    "Confira os registros relacionados antes de tentar novamente."
                )
            },
        )
    status_code = 409 if codigo in {"23505", "23514"} else 502
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



# Serve interface and API from one origin, so the project starts with one local service.
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


