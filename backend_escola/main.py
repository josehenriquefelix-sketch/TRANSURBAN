from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import Depends, FastAPI, HTTPException
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Bancos remotos são auditados antes de uso; inicialização não faz migrações.
    if is_sqlite:
        Base.metadata.create_all(bind=engine)
    try:
        yield
    finally:
        engine.dispose()

app = FastAPI(title="API TRANSURBAN", version="1.1.1", lifespan=lifespan,
              docs_url=None, redoc_url=None,
              description="Cadastros de cidades e linhas, análise de CSV acadêmico e dashboard em /painel/.")
app.include_router(ia_router)

app.mount("/documentacao-static", StaticFiles(directory=Path(__file__).resolve().parent / "swagger_static"), name="swagger-static")

@app.get("/docs", include_in_schema=False)
def documentacao():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="API TRANSURBAN — documentação",
        swagger_js_url="/documentacao-static/swagger-ui-bundle.js",
        swagger_css_url="/documentacao-static/swagger-ui.css",
        swagger_favicon_url="/documentacao-static/favicon-32x32.png",
        swagger_ui_parameters={"validatorUrl": None},
    )

@app.exception_handler(SQLAlchemyError)
async def erro_banco(_request, _error):
    return JSONResponse(status_code=503, content={"detail": "Banco indisponível ou esquema incompatível. Verifique a configuração privada e execute a auditoria do banco."})

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
    return {"mensagem": "API TRANSURBAN funcionando", "painel": "/painel/", "documentacao": "/docs"}

@app.get("/health", tags=["Sistema"])
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "banco": "sqlite_local" if is_sqlite else "postgresql"}

@app.post("/cidades", response_model=schemas.CidadeResponse, status_code=201, tags=["DS — Cidades"],
          responses={409: {"description": "Restrição de integridade no banco"}, 503: {"description": "Banco indisponível"}})
def criar_cidade(cidade: schemas.CidadeCreate, db: Session = Depends(get_db)):
    nova = models.Cidade(nome=cidade.nome)
    salvar(db, nova)
    return nova

@app.get("/cidades", response_model=list[schemas.CidadeResponse], tags=["DS — Cidades"])
def listar_cidades(db: Session = Depends(get_db)):
    return db.scalars(select(models.Cidade).order_by(models.Cidade.id_cidade)).all()

@app.post("/linhas", response_model=schemas.LinhaResponse, status_code=201, tags=["DS — Linhas"],
          responses={404: {"description": "Cidade não encontrada"}, 409: {"description": "Restrição de integridade no banco"}, 503: {"description": "Banco indisponível"}})
def criar_linha(linha: schemas.LinhaCreate, db: Session = Depends(get_db)):
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
