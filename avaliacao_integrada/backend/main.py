"""FastAPI: CRUD Supabase por HTTPS e consultas pandas sobre CSV."""
import ctypes
import logging
import os
from pathlib import Path
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from httpx import RequestError
from postgrest.exceptions import APIError

from backend.controller.analise import router as analise_router
from backend.controller.cidades import router as cidades_router
from backend.controller.linhas import router as linhas_router
from backend.database import supabase_configurado
from backend.auth import router as auth_router
from backend.controller.portal import router as portal_router
from backend.controller.mobilidade import router as mobilidade_router
from backend.controller.suporte import router as suporte_router

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
    title="TRANSURBAN · API de Desenvolvimento de Sistemas",
    description=(
        "Contas, cidades, linhas, trajetos, avaliações e passe demonstrativo. "
        "Integração com Supabase por HTTPS."
    ),
    version="2.0.0",
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
    allow_headers=["Content-Type", "Authorization"],
)
app.include_router(auth_router)
app.include_router(portal_router)
app.include_router(mobilidade_router)
app.include_router(suporte_router)
app.include_router(cidades_router)
app.include_router(linhas_router)
app.include_router(analise_router)


def esquema_ds():
    if app.openapi_schema is None:
        app.openapi_schema = get_openapi(title=app.title, version=app.version,
                                         description=app.description, routes=app.routes)
        app.openapi_schema["paths"] = {path: value for path, value in app.openapi_schema["paths"].items()
                                        if not path.startswith("/ia/")}
    return app.openapi_schema


app.openapi = esquema_ds


@app.get("/dados/openapi.json", include_in_schema=False)
def esquema_dados():
    schema = get_openapi(title="TRANSURBAN · API de Ciência de Dados", version=app.version,
                        description="Resumo e quatro totalizações do CSV acadêmico, calculados com pandas.", routes=app.routes)
    schema["paths"] = {path: value for path, value in schema["paths"].items() if path.startswith("/ia/")}
    return schema


@app.get("/dados/docs", include_in_schema=False)
def documentacao_dados():
    return get_swagger_ui_html(openapi_url="/dados/openapi.json", title="TRANSURBAN · Ciência de Dados")


@app.middleware("http")
async def proteger_solicitacoes(request: Request, call_next):
    # Cookies só podem autorizar alterações da própria origem ou de origens configuradas.
    origin = request.headers.get("origin")
    mesma_origem = str(request.base_url).rstrip("/")
    if request.method in {"POST", "PUT", "DELETE", "PATCH"} and origin and origin not in [mesma_origem, *origens]:
        return JSONResponse(status_code=403, content={"detail": "Origem da solicitação não permitida."})
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-Frame-Options"] = "DENY"
    if request.url.path.startswith(("/auth", "/mobilidade", "/atendimento", "/gestao", "/motorista", "/portal/passe", "/portal/avaliacoes", "/portal/recargas")):
        response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/health", tags=["Sistema"])
def health():
    return {
        "projeto": "TRANSURBAN",
        "versao": "2026.11.14-gps",
        "supabase_configurado": supabase_configurado(),
        "interface": "/",
        "documentacao": "/docs",
    }


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
