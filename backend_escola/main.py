from contextlib import asynccontextmanager
import os
from pathlib import Path
from fastapi import Body, Depends, FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, joinedload
import models
import schemas
from database import Base, SessionLocal, engine, is_sqlite
from ia_routes import router as ia_router
from dados_publicos import router as dados_publicos_router
from web_api import router as web_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Bancos remotos são auditados antes de uso; inicialização não faz migrações.
    if is_sqlite:
        Base.metadata.create_all(bind=engine)
    try:
        yield
    finally:
        engine.dispose()

APRESENTACAO = os.getenv("TRANSURBAN_APRESENTACAO") == "1"
app = FastAPI(title="API TRANSURBAN", version="1.4.0", lifespan=lifespan,
              docs_url=None, redoc_url=None,
              openapi_tags=[
                  {"name":"Apresentação", "description":"Comece pelo roteiro dos testes. Cadastros DS são exemplos; IA usa programação pública histórica de Curitiba."},
                  {"name":"Sistema", "description":"Verifique o banco em /health antes dos testes."},
                  {"name":"DS — Cidades", "description":"Primeiro cadastre uma cidade e anote o ID devolvido."},
                  {"name":"DS — Linhas", "description":"Use o ID real da cidade. A linha DEMO-20 é um exemplo de cadastro, não uma linha operacional verificada."},
                  {"name":"IA — Dados públicos: Curitiba (histórico)", "description":"Snapshot comunitário, não oficial, de 28/09–05/10/2026. Não é dado de Maringá/Sarandi, atraso medido ou viagem realizada."},
              ],
              description="DS: cadastro e consulta em banco SQL. IA: programação publicada de Curitiba, com fonte, período e limitações. Para apresentar, abra GET /apresentacao. O estudo IA não inclui GPS, atraso medido ou previsão de chegada. O site em /app oferece viagens autodeclaradas e GPS voluntário, sem integração à frota oficial.")
@app.middleware("http")
async def cabecalhos_site(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith(("/app", "/web-api/")):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["Permissions-Policy"] = "geolocation=(self), camera=(), microphone=()"
        if request.url.path.startswith("/web-api/"):
            response.headers["Cache-Control"] = "no-store"
        else:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https://tile.openstreetmap.org; connect-src 'self'; "
                "object-src 'none'; base-uri 'self'; frame-ancestors 'self'; form-action 'self'"
            )
    return response

app.include_router(dados_publicos_router)
app.include_router(ia_router, include_in_schema=not APRESENTACAO)
app.include_router(web_router, include_in_schema=not APRESENTACAO)

app.mount("/documentacao-static", StaticFiles(directory=Path(__file__).resolve().parent / "swagger_static"), name="swagger-static")

@app.get("/docs", include_in_schema=False)
def documentacao():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="API TRANSURBAN — documentação",
        swagger_js_url="/documentacao-static/swagger-ui-bundle.js",
        swagger_css_url="/documentacao-static/swagger-ui.css",
        swagger_favicon_url="/documentacao-static/favicon-32x32.png",
        swagger_ui_parameters={"validatorUrl": None, "displayRequestDuration": True,
                               "docExpansion": "list", "defaultModelsExpandDepth": -1,
                               "filter": True},
    )

@app.exception_handler(SQLAlchemyError)
async def erro_banco(_request, _error):
    return JSONResponse(status_code=503, content={"detail": "Banco indisponível ou esquema incompatível. Verifique a configuração privada e execute a auditoria do banco."})

@app.exception_handler(RequestValidationError)
async def erro_validacao(request, error):
    if request.url.path.startswith('/web-api/'):
        # Não devolve senha ou outros valores enviados em respostas de validação.
        return JSONResponse(status_code=422,content={'detail':[
            {'loc':item['loc'],'type':item['type'],'msg':item['msg']}
            for item in error.errors()
        ]})
    return await request_validation_exception_handler(request,error)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def salvar(db, registro):
    try:
        db.add(registro)
        db.commit()
        db.refresh(registro)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Cadastro viola uma restrição do banco.")

def resposta_linha(linha):
    return {"id_linha": linha.id_linha, "codigo": linha.codigo, "nome": linha.nome,
            "id_cidade": linha.id_cidade, "cidade": linha.cidade.nome}

@app.get("/", tags=["Sistema"])
def inicio():
    return {"mensagem": "API TRANSURBAN funcionando", "documentacao": "/docs",
            "roteiro": "/apresentacao", "dados_publicos": "/ia/dados-publicos/resumo",
            "modo_apresentacao": APRESENTACAO, "site": "/app/"}

@app.get("/apresentacao", tags=["Apresentação"], summary="Comece aqui: sequência e resultados esperados")
def roteiro() -> dict:
    return {
        "projeto":"TRANSURBAN", "modo_apresentacao": APRESENTACAO,
        "contexto":"Projeto para Maringá/Sarandi; estudo externo com programação pública de Curitiba.",
        "fonte":"GTFS comunitário histórico; não oficial da URBS. Consulte /ia/dados-publicos/fonte.",
        "periodo_fonte":"28/09 a 05/10/2026",
        "nao_disponivel":["atrasos medidos", "viagens realizadas", "passageiros", "GPS", "previsão de chegada"],
        "orientacao":"Abra cada operação, clique Try it out e Execute. Confira Server response, não Example Value.",
        "sequencia":[
            {"passo":1,"rota":"GET /health","esperado":"200; status ok; banco sqlite_local no inicializador de apresentação."},
            {"passo":2,"rota":"POST /cidades","entrada":{"nome":"Sarandi"},"esperado":"201; anote id_cidade realmente devolvido."},
            {"passo":3,"rota":"POST /linhas","esperado":"Use o exemplo válido e substitua id_cidade pelo ID devolvido; 201 com cidade Sarandi."},
            {"passo":4,"rota":"GET /linhas","esperado":"200; o cadastro DEMO-20 aparece na lista."},
            {"passo":5,"rota":"POST /linhas","esperado":"Exemplo cidade inexistente: confirme antes que 999999 não existe; 404. GET seguinte não contém a tentativa."},
            {"passo":6,"rota":"POST /cidades","entrada":{"nome":"   "},"esperado":"422 por nome vazio; erro intencional do teste."},
            {"passo":7,"rota":"GET /ia/dados-publicos/fonte","esperado":"200; fonte, período, hashes e limites."},
            {"passo":8,"rota":"GET /ia/dados-publicos/qualidade","esperado":"200; integridade e consistência do snapshot verificadas."},
            {"passo":9,"rota":"GET /ia/dados-publicos/resumo","esperado":"200; 71086 registros; 309 códigos; média de contagens 230,0518; mediana 162; não são minutos."},
            {"passo":10,"rota":"GET /ia/dados-publicos/agrupamentos/linha?limite=5","esperado":"200; cinco grupos para leitura; total completo identificado separadamente."},
            {"passo":11,"rota":"GET /ia/dados-publicos/agrupamentos/servico","esperado":"200; categorias somam 71086 registros, não viagens realizadas por dia."},
        ],
    }

@app.get("/health", tags=["Sistema"])
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "banco": "sqlite_local" if is_sqlite else "postgresql"}

@app.post("/cidades", response_model=schemas.CidadeResponse, status_code=201, tags=["DS — Cidades"],
          summary="Cadastrar cidade — 201; nome vazio — 422",
          responses={409: {"description": "Restrição de integridade no banco"}, 503: {"description": "Banco indisponível"}})
def criar_cidade(cidade: schemas.CidadeCreate = Body(openapi_examples={
    "cadastro_valido":{"summary":"Cadastro válido (201)","value":{"nome":"Sarandi"}},
    "nome_vazio":{"summary":"Teste: somente espaços (422)","value":{"nome":"   "}},
}), db: Session = Depends(get_db)):
    nova = models.Cidade(nome=cidade.nome)
    salvar(db, nova)
    return nova

@app.get("/cidades", response_model=list[schemas.CidadeResponse], tags=["DS — Cidades"])
def listar_cidades(db: Session = Depends(get_db)):
    return db.scalars(select(models.Cidade).order_by(models.Cidade.id_cidade)).all()

@app.post("/linhas", response_model=schemas.LinhaResponse, status_code=201, tags=["DS — Linhas"],
          summary="Cadastrar linha vinculada a uma cidade",
          description="Use o id_cidade devolvido pelo POST da cidade. O número 1 no exemplo não é garantido. Para testar 404, confira primeiro que o ID 999999 não existe.",
          responses={404: {"description": "Cidade não encontrada"}, 409: {"description": "Restrição de integridade no banco"}, 503: {"description": "Banco indisponível"}})
def criar_linha(linha: schemas.LinhaCreate = Body(openapi_examples={
    "cadastro_valido":{"summary":"Cadastro de demonstração (201): ajuste o ID", "value":{"codigo":"DEMO-20","nome":"Linha da apresentação","id_cidade":1}},
    "cidade_inexistente":{"summary":"Teste: cidade inexistente (404)", "value":{"codigo":"TESTE-ERRO","nome":"Tentativa inválida","id_cidade":999999}},
}), db: Session = Depends(get_db)):
    cidade = db.get(models.Cidade, linha.id_cidade)
    if cidade is None:
        raise HTTPException(status_code=404, detail="Cidade não encontrada")
    nova = models.LinhaOnibus(codigo=linha.codigo, nome=linha.nome, id_cidade=cidade.id_cidade)
    salvar(db, nova)
    return resposta_linha(nova)

@app.get("/linhas", response_model=list[schemas.LinhaResponse], tags=["DS — Linhas"])
def listar_linhas(db: Session = Depends(get_db)):
    consulta = select(models.LinhaOnibus).options(joinedload(models.LinhaOnibus.cidade)).order_by(models.LinhaOnibus.id_linha)
    return [resposta_linha(linha) for linha in db.scalars(consulta).all()]

app.mount("/painel", StaticFiles(directory=Path(__file__).resolve().parent / "frontend", html=True), name="painel")
app.mount("/app", StaticFiles(directory=Path(__file__).resolve().parent / "web", html=True), name="site")
