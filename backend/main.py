"""Na pasta backend: python -m uvicorn main:app --reload."""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from sqlalchemy.exc import SQLAlchemyError
from routes import cidades_router, linhas_router

app = FastAPI(title="TRANSURBAN — Avaliação de backend", version="2.0.0",
              description="Cidade e linha de ônibus relacionadas conforme o DER do projeto.")
app.include_router(cidades_router)
app.include_router(linhas_router)
app.mount("/site", StaticFiles(directory=Path(__file__).resolve().parents[1] / "frontend", html=True), name="site")

@app.exception_handler(SQLAlchemyError)
async def erro_banco(_request, _exception):
    return JSONResponse(status_code=503, content={
        "detail": "Banco indisponível ou estrutura incompatível. Confira a configuração e o roteiro de banco."
    })

@app.get("/", tags=["Sistema"])
def inicio():
    return {"mensagem": "API TRANSURBAN funcionando", "documentacao": "/docs"}
