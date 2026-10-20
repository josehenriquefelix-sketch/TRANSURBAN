"""Captura respostas reais sem cadastrar novos registros. Execute com API ativa."""
import json
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def chamada(path, payload=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = Request("http://127.0.0.1:8000" + path, data=data,
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
    resultados = [chamada(p) for p in ("/", "/docs", "/openapi.json", "/site/", "/site/script.js", "/site/style.css", "/site/modulo6.css", "/site/favicon.svg", "/cidades", "/linhas")]
    for item in resultados:
        assert item["status"] == 200, item
    erro = chamada("/linhas", {"codigo": "ERRO", "nome": "Teste inválido", "id_cidade": 2147483647})
    assert erro["status"] == 404, erro
    resultados.append(erro)
    erro = chamada("/cidades", {"nome": "   "})
    assert erro["status"] == 422, erro
    resultados.append(erro)
    # A especificação inteira é acessível, mas não precisa inflar a evidência.
    for item in resultados:
        if item["rota"] == "/openapi.json":
            item["resposta"] = {"rotas": sorted(item["resposta"]["paths"])}
    target = Path(__file__).resolve().parents[1] / "docs/avaliacao_backend/evidencias/http.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(resultados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("12 verificações HTTP aprovadas. Respostas salvas em docs/avaliacao_backend/evidencias/http.json.")


if __name__ == "__main__":
    main()
