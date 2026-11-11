"""Autenticação Supabase Auth, com sessão em cookies HttpOnly."""
import hashlib
import os
import re
import time
from collections import defaultdict, deque
from threading import Lock
from urllib.parse import quote

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.database import get_supabase

router = APIRouter(prefix="/auth", tags=["Conta e sessão"])
_tentativas = defaultdict(deque)
_lock = Lock()
ACCESS = "transurban_access"
REFRESH = "transurban_refresh"


def limitar(request: Request):
    chave = request.client.host if request.client else "local"
    agora = time.monotonic()
    with _lock:
        # Descarta endereços expirados para manter a memória limitada.
        for endereco in list(_tentativas):
            if not _tentativas[endereco] or _tentativas[endereco][-1] < agora - 900:
                del _tentativas[endereco]
        fila = _tentativas[chave]
        while fila and fila[0] < agora - 900:
            fila.popleft()
        if len(fila) >= 30:
            raise HTTPException(429, "Muitas tentativas. Aguarde 15 minutos e tente novamente.")
        fila.append(agora)


def cpf_hash(valor: str):
    return hashlib.sha256(valor.encode()).hexdigest()


def validar_cpf(valor: str):
    valor = re.sub(r"[.\-\s]", "", valor)
    if not re.fullmatch(r"\d{11}", valor) or len(set(valor)) == 1:
        raise ValueError("Informe um CPF válido.")
    for tamanho in (9, 10):
        soma = sum(int(valor[i]) * (tamanho + 1 - i) for i in range(tamanho))
        digito = (soma * 10) % 11
        if int(valor[tamanho]) != (0 if digito == 10 else digito):
            raise ValueError("Informe um CPF válido.")
    return valor


class Cadastro(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nome: str = Field(min_length=2, max_length=100)
    email: str = Field(max_length=254)
    cpf: str
    senha: str = Field(min_length=8, max_length=72)

    @field_validator("email")
    @classmethod
    def email_valido(cls, valor):
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", valor):
            raise ValueError("Informe um e-mail válido.")
        return valor.strip().lower()

    @field_validator("cpf")
    @classmethod
    def cpf_valido(cls, valor):
        return validar_cpf(valor)


class Login(BaseModel):
    identificador: str = Field(min_length=3, max_length=254)
    senha: str = Field(min_length=1, max_length=72)


class Email(BaseModel):
    email: str = Field(min_length=5, max_length=254)


class NovaSenha(BaseModel):
    senha: str = Field(min_length=8, max_length=72)


class Recuperacao(NovaSenha):
    access_token: str = Field(min_length=20, max_length=8192)


def auth_request(method, path, payload=None, token=None):
    url = os.getenv("SUPABASE_URL", "").rstrip("/")
    key = os.getenv("SUPABASE_KEY", "")
    if not url or not key:
        raise HTTPException(503, "Configure o Supabase em backend/.env.")
    headers = {"apikey": key, "Authorization": f"Bearer {token or key}"}
    try:
        result = httpx.request(method, f"{url}/auth/v1/{path}", json=payload, headers=headers, timeout=20)
    except httpx.RequestError as erro:
        raise HTTPException(503, "Serviço de contas indisponível. Tente novamente.") from erro
    data = result.json() if result.content else {}
    if result.is_error:
        if result.status_code == 429:
            raise HTTPException(429, "Limite de envio atingido. Aguarde antes de tentar novamente.")
        raise HTTPException(401 if result.status_code in (400, 401, 403, 422) else 503,
                            "Não foi possível validar a conta ou a sessão. Confira os dados e a confirmação do e-mail.")
    return data


def cookies(response, data):
    seguro = os.getenv("COOKIE_SECURE", "false").lower() == "true"
    response.set_cookie(ACCESS, data["access_token"], httponly=True, secure=seguro,
                        samesite="lax", max_age=int(data.get("expires_in", 3600)), path="/")
    response.set_cookie(REFRESH, data["refresh_token"], httponly=True, secure=seguro,
                        samesite="lax", max_age=604800, path="/auth")
    response.headers["Cache-Control"] = "no-store"


def usuario_atual(request: Request):
    token = request.cookies.get(ACCESS)
    if not token:
        raise HTTPException(401, "Entre na sua conta para continuar.")
    usuario = auth_request("GET", "user", token=token)
    return {"id": usuario["id"], "email": usuario.get("email"),
            "nome": usuario.get("user_metadata", {}).get("nome", "Passageiro")}


def administrador(usuario=Depends(usuario_atual)):
    emails = {email.strip().lower() for email in os.getenv("ADMIN_EMAILS", "").split(",") if email.strip()}
    if usuario["email"].lower() not in emails:
        raise HTTPException(403, "Este cadastro é gerenciado pela equipe TRANSURBAN.")
    return usuario


@router.post("/cadastro", status_code=201, dependencies=[Depends(limitar)])
def cadastrar(dados: Cadastro, response: Response):
    data = auth_request("POST", "signup", {"email": dados.email, "password": dados.senha,
                        "data": {"nome": dados.nome, "cpf_hash": cpf_hash(dados.cpf)}})
    # O trigger SQL grava o vínculo CPF/conta sem expor o CPF original.
    if data.get("access_token"):
        cookies(response, data)
    return {"mensagem": "Cadastro recebido. Confira seu e-mail para confirmar a conta.",
            "autenticado": bool(data.get("access_token"))}


@router.post("/login", dependencies=[Depends(limitar)])
def entrar(dados: Login, response: Response):
    identificador = dados.identificador.strip().lower()
    if "@" not in identificador:
        try:
            cpf = validar_cpf(identificador)
        except ValueError as erro:
            raise HTTPException(401, "E-mail/CPF ou senha inválidos.") from erro
        registros = get_supabase().table("tu_perfil").select("email").eq("cpf_hash", cpf_hash(cpf)).limit(1).execute().data
        if not registros:
            raise HTTPException(401, "E-mail/CPF ou senha inválidos.")
        identificador = registros[0]["email"]
    data = auth_request("POST", "token?grant_type=password", {"email": identificador, "password": dados.senha})
    cookies(response, data)
    return {"mensagem": "Login realizado."}


@router.get("/me")
def minha_conta(response: Response, usuario=Depends(usuario_atual)):
    response.headers["Cache-Control"] = "no-store"
    emails = {e.strip().lower() for e in os.getenv("ADMIN_EMAILS", "").split(",") if e.strip()}
    return {**usuario, "administrador": usuario["email"].lower() in emails}


@router.post("/refresh")
def renovar(request: Request, response: Response):
    token = request.cookies.get(REFRESH)
    if not token:
        raise HTTPException(401, "Entre novamente na sua conta.")
    data = auth_request("POST", "token?grant_type=refresh_token", {"refresh_token": token})
    cookies(response, data)
    return {"mensagem": "Sessão renovada."}


@router.post("/logout")
def sair(request: Request, response: Response):
    token = request.cookies.get(ACCESS)
    if token:
        try:
            auth_request("POST", "logout?scope=local", token=token)
        except HTTPException:
            pass
    response.delete_cookie(ACCESS, path="/")
    response.delete_cookie(REFRESH, path="/auth")
    return {"mensagem": "Você saiu da conta."}


@router.post("/esqueci-senha", dependencies=[Depends(limitar)])
def esqueci_senha(dados: Email):
    redirect = os.getenv("APP_URL", "http://127.0.0.1:8000").rstrip("/") + "/#nova-senha"
    auth_request("POST", "recover?redirect_to=" + quote(redirect, safe=""), {"email": dados.email.strip().lower()})
    return {"mensagem": "Se o e-mail estiver cadastrado, você receberá um link para criar uma nova senha."}


@router.post("/redefinir-senha", dependencies=[Depends(limitar)])
def redefinir(dados: Recuperacao):
    # O link do Supabase emite o token temporário usado para redefinir a senha.
    auth_request("PUT", "user", {"password": dados.senha}, token=dados.access_token)
    return {"mensagem": "Senha atualizada. Entre com a nova senha."}
