"""Captura respostas reais sem cadastrar novos registros. Execute com API ativa."""
import json
from argparse import ArgumentParser
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


BASE_URL = "http://127.0.0.1:8000"


def chamada(path, payload=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = Request(BASE_URL + path, data=data,
                  headers={"Content-Type": "application/json"})
    try:
        response = urlopen(req, timeout=10)
    except HTTPError as exc:
        response = exc
    with response:
        body = response.read().decode("utf-8")
        if "application/json" in response.headers.get("Content-Type", ""):
            body = json.loads(body)
        else:
            body = {"tipo": response.headers.get("Content-Type"), "tamanho": len(body)}
        return {"rota": path, "metodo": "GET" if payload is None else "POST",
                "status": response.status, "resposta": body}


def main():
    global BASE_URL
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=BASE_URL)
    parser.add_argument("--saida", type=Path)
    args = parser.parse_args()
    parsed = urlparse(args.base_url)
    if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost"} or parsed.username or parsed.password or parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
        raise SystemExit("Use somente a URL local da API, por exemplo http://127.0.0.1:8001.")
    BASE_URL = args.base_url.rstrip("/")
    resultados = [chamada(p) for p in ("/", "/docs", "/openapi.json", "/documentacao/swagger-ui-bundle.js", "/documentacao/swagger-ui.css", "/site/", "/site/script.js", "/site/app.css", "/site/favicon.svg", "/cidades", "/linhas")]
    for item in resultados:
        assert item["status"] == 200, item
    cidades = next(item["resposta"] for item in resultados if item["rota"] == "/cidades")
    ids = {city["id_cidade"] for city in cidades}
    inexistente = 2147483647
    while inexistente in ids:
        inexistente -= 1
    erro = chamada("/linhas", {"codigo": "ERRO", "nome": "Teste inválido", "id_cidade": inexistente})
    assert erro["status"] == 404, erro
    resultados.append(erro)
    erro = chamada("/cidades", {"nome": "   "})
    assert erro["status"] == 422, erro
    resultados.append(erro)
    # A especificação inteira é acessível, mas não precisa inflar a evidência.
    for item in resultados:
        if item["rota"] == "/openapi.json":
            item["resposta"] = {"rotas": sorted(item["resposta"]["paths"])}
    target = args.saida or Path(__file__).resolve().parents[1] / "docs/avaliacao_backend/evidencias/http.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(resultados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(resultados)} verificações HTTP aprovadas. Respostas salvas em {target.name}.")


if __name__ == "__main__":
    main()
