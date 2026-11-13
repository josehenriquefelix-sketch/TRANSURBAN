"""Autenticação Supabase Auth, com sessão em cookies HttpOnly."""
import hashlib
import os
import re
import time
import secrets
import base64
from typing import Literal
from collections import defaultdict, deque
from threading import Lock
from urllib.parse import quote, urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field, field_validator
from fastapi.responses import RedirectResponse
from postgrest.exceptions import APIError

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


def validar_senha(valor: str):
    if not (any(c.isupper() for c in valor) and any(c.islower() for c in valor)
            and any(c.isdigit() for c in valor) and any(not c.isalnum() and not c.isspace() for c in valor)):
        raise ValueError("Use uma letra maiúscula, uma minúscula, um número e um símbolo.")
    return valor


class Cadastro(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nome: str = Field(min_length=2, max_length=100)
    email: str = Field(max_length=254)
    cpf: str
    senha: str = Field(min_length=8, max_length=72)

    _senha_segura = field_validator("senha")(validar_senha)

    @field_validator("email")
    @classmethod
    def email_valido(cls, valor):
        valor = valor.strip().lower()
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
    tipo_acesso: Literal["passageiro", "motorista", "gestor"] = "passageiro"


class Email(BaseModel):
    email: str = Field(min_length=5, max_length=254)

    @field_validator("email")
    @classmethod
    def normalizar(cls, valor):
        valor = valor.strip().lower()
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", valor):
            raise ValueError("Informe um e-mail válido.")
        return valor


class NovaSenha(BaseModel):
    senha: str = Field(min_length=8, max_length=72)
    _senha_segura = field_validator("senha")(validar_senha)


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
        codigo = data.get("error_code") or data.get("code")
        if codigo == "same_password":
            raise HTTPException(422, "Escolha uma senha diferente da anterior.")
        if codigo == "weak_password":
            raise HTTPException(422, "A senha não atende aos requisitos de segurança.")
        if codigo == "email_address_not_authorized":
            raise HTTPException(503, "O envio de e-mail precisa ser configurado no Supabase. Contate a equipe TRANSURBAN.")
        if codigo == "email_not_confirmed":
            raise HTTPException(403, "Confirme seu e-mail antes de entrar. Confira também a pasta de spam ou solicite o reenvio da confirmação.")
        if codigo == "invalid_credentials":
            raise HTTPException(401, "E-mail/CPF ou senha inválidos. Confira os dados ou use Esqueci minha senha.")
        if codigo in {"user_already_exists", "email_exists"}:
            raise HTTPException(409, "Não foi possível concluir o cadastro. Se já possui uma conta, entre ou recupere a senha.")
        if codigo in {"signup_disabled", "email_provider_disabled"}:
            raise HTTPException(503, "O cadastro por e-mail está temporariamente indisponível. Contate o suporte.")
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
            "nome": usuario.get("user_metadata", {}).get("nome") or usuario.get("user_metadata", {}).get("full_name") or "Passageiro"}


def papeis(usuario):
    permitidos = ["passageiro"]
    emails = {e.strip().lower() for e in os.getenv("ADMIN_EMAILS", "").split(",") if e.strip()}
    if (usuario.get("email") or "").lower() in emails:
        permitidos.append("gestor")
    try:
        acessos = get_supabase().table("tu_acesso").select("papel").eq("usuario_id", usuario["id"]).eq("ativo", True).execute().data
        permitidos.extend(acesso["papel"] for acesso in acessos if acesso["papel"] not in permitidos)
    except APIError as erro:
        if erro.code not in {"42P01", "PGRST205"}:
            raise
    return permitidos


def motorista_autorizado(usuario=Depends(usuario_atual)):
    if "motorista" not in papeis(usuario):
        raise HTTPException(403, "A área do motorista exige vínculo autorizado pela gestão.")
    return usuario


def gestor_autorizado(usuario=Depends(usuario_atual)):
    if "gestor" not in papeis(usuario):
        raise HTTPException(403, "Acesso restrito à gestão autorizada.")
    return usuario


def administrador(usuario=Depends(usuario_atual)):
    emails = {email.strip().lower() for email in os.getenv("ADMIN_EMAILS", "").split(",") if email.strip()}
    if usuario["email"].lower() not in emails:
        raise HTTPException(403, "Este cadastro é gerenciado pela equipe TRANSURBAN.")
    return usuario


@router.post("/cadastro", status_code=201, dependencies=[Depends(limitar)])
def cadastrar(dados: Cadastro, response: Response):
    existentes = get_supabase().table("tu_perfil").select("usuario_id").eq("cpf_hash", cpf_hash(dados.cpf)).limit(1).execute().data
    if existentes:
        raise HTTPException(409, "Não foi possível concluir o cadastro. Se já possui uma conta, entre ou recupere a senha.")
    data = auth_request("POST", "signup", {"email": dados.email, "password": dados.senha,
                        "data": {"nome": dados.nome, "cpf_hash": cpf_hash(dados.cpf)}})
    # O trigger SQL grava o vínculo CPF/conta sem expor o CPF original.
    if data.get("access_token"):
        cookies(response, data)
    mensagem = "Conta criada. Você já pode continuar." if data.get("access_token") else "Cadastro recebido. Confira seu e-mail e a pasta de spam para confirmar a conta antes de entrar."
    return {"mensagem": mensagem,
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
        identificador = registros[0]["email"].strip().lower()
    data = auth_request("POST", "token?grant_type=password", {"email": identificador, "password": dados.senha})
    if dados.tipo_acesso != "passageiro":
        user = auth_request("GET", "user", token=data["access_token"])
        if dados.tipo_acesso not in papeis({"id": user["id"], "email": user.get("email")}):
            raise HTTPException(403, "Sua conta ainda não foi autorizada para este tipo de acesso.")
    cookies(response, data)
    return {"mensagem": "Login realizado."}


@router.get("/me")
def minha_conta(response: Response, usuario=Depends(usuario_atual)):
    response.headers["Cache-Control"] = "no-store"
    emails = {e.strip().lower() for e in os.getenv("ADMIN_EMAILS", "").split(",") if e.strip()}
    return {**usuario, "administrador": usuario["email"].lower() in emails, "papeis": papeis(usuario)}


@router.get("/configuracao")
def configuracao_publica():
    settings = auth_request("GET", "settings")
    return {"google": bool(settings.get("external", {}).get("google"))}


def limpar_oauth(response):
    for key in ("tu_pkce", "tu_oauth_state", "tu_oauth_role"):
        response.delete_cookie(key, path="/auth")
    return response


@router.get("/google")
def entrar_google(tipo_acesso: Literal["passageiro", "motorista", "gestor"] = "passageiro"):
    settings = auth_request("GET", "settings")
    if not settings.get("external", {}).get("google"):
        raise HTTPException(503, "Login com Google aguardando configuração do provedor no Supabase.")
    verifier = secrets.token_urlsafe(48)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
    state = secrets.token_urlsafe(24)
    app_url = os.getenv("APP_URL", "http://127.0.0.1:8000").rstrip("/")
    callback = f"{app_url}/auth/google/callback?flow={state}"
    query = urlencode({"provider": "google", "redirect_to": callback, "code_challenge": challenge, "code_challenge_method": "s256"})
    response = RedirectResponse(os.getenv("SUPABASE_URL", "").rstrip("/") + "/auth/v1/authorize?" + query)
    secure = os.getenv("COOKIE_SECURE", "false").lower() == "true"
    for key, value in {"tu_pkce": verifier, "tu_oauth_state": state, "tu_oauth_role": tipo_acesso}.items():
        response.set_cookie(key, value, max_age=600, httponly=True, secure=secure, samesite="lax", path="/auth")
    return response


@router.get("/google/callback", include_in_schema=False)
def google_callback(request: Request, code: str = "", flow: str = ""):
    expected = request.cookies.get("tu_oauth_state", "")
    verifier = request.cookies.get("tu_pkce", "")
    if not code or not expected or not verifier or not secrets.compare_digest(flow, expected):
        return limpar_oauth(RedirectResponse("/?erro=google_sessao_invalida#login"))
    try:
        data = auth_request("POST", "token?grant_type=pkce", {"auth_code": code, "code_verifier": verifier})
        user = auth_request("GET", "user", token=data["access_token"])
        role = request.cookies.get("tu_oauth_role", "passageiro")
        if role not in papeis({"id": user["id"], "email": user.get("email")}):
            return limpar_oauth(RedirectResponse("/?erro=acesso_nao_autorizado#login"))
        destino = {"motorista": "/motorista/", "gestor": "/gestao/"}.get(role, "/#inicio")
        response = RedirectResponse(destino)
        cookies(response, data)
    except HTTPException:
        response = RedirectResponse("/?erro=google_indisponivel#login")
    return limpar_oauth(response)


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


@router.post("/reenviar-confirmacao", dependencies=[Depends(limitar)])
def reenviar_confirmacao(dados: Email):
    auth_request("POST", "resend", {"type": "signup", "email": dados.email})
    return {"mensagem": "Se a conta precisar de confirmação, você receberá uma nova mensagem. Confira também o spam."}


@router.post("/redefinir-senha", dependencies=[Depends(limitar)])
def redefinir(dados: Recuperacao):
    # O link do Supabase emite o token temporário usado para redefinir a senha.
    auth_request("PUT", "user", {"password": dados.senha}, token=dados.access_token)
    return {"mensagem": "Senha atualizada. Entre com a nova senha."}
