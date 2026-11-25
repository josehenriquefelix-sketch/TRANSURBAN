"""Cliente do Supabase pela Data API HTTPS. O segredo fica somente no backend."""
import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
import httpx
from supabase import Client, ClientOptions, create_client

load_dotenv(Path(__file__).with_name(".env"), override=False)


def supabase_configurado() -> bool:
    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_KEY", "").strip()
    return bool(
        url.startswith("https://")
        and ".supabase.co" in url
        and "SEU_PROJETO" not in url
        and key
        and "EXEMPLO_FICTICIO" not in key
    )


@lru_cache(maxsize=1)
def get_supabase() -> Client:
    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_KEY", "").strip()
    if not url or not key:
        raise RuntimeError("Configure SUPABASE_URL e SUPABASE_KEY em backend/.env.")
    if not url.startswith("https://") or ".supabase.co" not in url or "SEU_PROJETO" in url:
        raise RuntimeError("SUPABASE_URL deve ser a URL HTTPS real do projeto Supabase.")
    if "EXEMPLO_FICTICIO" in key:
        raise RuntimeError("Substitua SUPABASE_KEY de exemplo pela chave privada do projeto.")
    # Mantém HTTPS e a verificação de certificados. HTTP/1.1 evita compartilhar
    # streams HTTP/2 que falharam nas consultas simultâneas dos painéis.
    conexao = httpx.Client(http2=False, timeout=20)
    return create_client(url, key, options=ClientOptions(httpx_client=conexao))

