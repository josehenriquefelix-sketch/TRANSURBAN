"""Na pasta backend: python -m uvicorn main:app --reload."""
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from sqlalchemy.exc import SQLAlchemyError
from routes import cidades_router, linhas_router

app = FastAPI(title="TRANSURBAN - API", version="2.0.0", docs_url=None, redoc_url=None,
              description="Cidade e linha de ônibus relacionadas conforme o DER do projeto.")
app.include_router(cidades_router)
app.include_router(linhas_router)
app.mount("/site", StaticFiles(directory=Path(__file__).resolve().parents[1] / "frontend", html=True), name="site")
app.mount("/documentacao", StaticFiles(directory=Path(__file__).resolve().parent / "static/swagger"), name="documentacao")


@app.get("/docs", include_in_schema=False)
def documentacao():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        swagger_js_url="/documentacao/swagger-ui-bundle.js",
        swagger_css_url="/documentacao/swagger-ui.css",
        swagger_favicon_url="/site/favicon.svg",
        swagger_ui_parameters={"validatorUrl": None},
    )

@app.exception_handler(SQLAlchemyError)
async def erro_banco(_request, _exception):
    return JSONResponse(status_code=503, content={
        "detail": "Banco indisponível ou estrutura incompatível. Confira a configuração e o roteiro de banco."
    })

@app.get("/", tags=["Sistema"])
def inicio():
    return {"mensagem": "API TRANSURBAN funcionando", "documentacao": "/docs"}
