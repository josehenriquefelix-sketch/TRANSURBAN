"""Integra API original, análise do CSV e site offline no mesmo servidor."""
from pathlib import Path
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi import HTTPException
from main import app
from dados_academicos import router

BASE = Path(__file__).resolve().parents[1]
app.include_router(router)
app.mount('/app', StaticFiles(directory=BASE / 'site', html=True), name='site')

@app.get('/apresentacao', include_in_schema=False)
def painel():
    return FileResponse(BASE / 'painel.html')

@app.get('/health', tags=['Diagnóstico'])
def health():
    from sqlalchemy import text
    from database import engine
    with engine.connect() as conexao:
        conexao.execute(text('SELECT 1'))
    return {'status': 'ok', 'banco': 'SQLite local', 'site': '/app/', 'api': '/docs', 'painel': '/apresentacao'}

@app.get('/console', include_in_schema=False)
def console():
    return FileResponse(BASE / 'console.html')

@app.get('/material/{arquivo}', include_in_schema=False)
def material(arquivo: str):
    permitidos = {'assistir-videoaula.html', 'videoaula.mp4', 'videoaula.vtt', 'GUIA-DA-EQUIPE.md'}
    if arquivo not in permitidos:
        raise HTTPException(404, 'Material não encontrado')
    return FileResponse(BASE / arquivo)
