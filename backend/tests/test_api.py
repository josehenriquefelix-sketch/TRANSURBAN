import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, OperationalError

from database import get_db
from main import app


def cadastrar(cliente, nome="Maringá"):
    resposta = cliente.post("/cidades", json={"nome": nome})
    assert resposta.status_code == 201
    return resposta.json()["id_cidade"]


def test_fluxo_completo_e_persistencia(cliente, banco):
    assert cliente.get("/").status_code == 200
    assert cliente.get("/docs").status_code == 200
    assert cliente.get("/cidades").json() == []
    assert cliente.get("/linhas").json() == []
    cidade = cadastrar(cliente)
    assert cidade > 0
    dados = {"codigo": "TESTE-001", "nome": "Linha acadêmica", "id_cidade": cidade}
    resposta = cliente.post("/linhas", json=dados)
    assert resposta.status_code == 201
    linha = resposta.json()
    assert linha == {"id_linha": linha["id_linha"], "codigo": "TESTE-001", "nome": "Linha acadêmica", "cidade": "Maringá"}
    assert cliente.get("/linhas").json() == [linha]
    # Nova conexão comprova commit; o vínculo armazenado é o ID.
    with banco.connect() as connection:
        assert connection.execute(text("SELECT id_cidade FROM linha_onibus")).scalar_one() == cidade
    # Outro cliente e outra sessão veem os dados já gravados.
    with TestClient(app) as outro:
        assert outro.get("/linhas").json() == [linha]


def test_fk_inexistente(cliente):
    resposta = cliente.post("/linhas", json={"codigo": "X", "nome": "Teste", "id_cidade": 999999})
    assert resposta.status_code == 404
    assert resposta.json() == {"detail": "Cidade não encontrada"}
    assert cliente.get("/linhas").json() == []


@pytest.mark.parametrize("dados", [{}, {"nome": "   "}, {"nome": "x" * 101}, {"nome": None}, {"nome": "Maringá", "id_cidade": 1}])
def test_cidade_invalida(cliente, dados):
    assert cliente.post("/cidades", json=dados).status_code == 422
    assert cliente.get("/cidades").json() == []


@pytest.mark.parametrize("alteracao", [{"codigo": " "}, {"codigo": "x" * 21}, {"nome": "x" * 121}, {"nome": " "}, {"id_cidade": 0}, {"id_cidade": "1"}, {"id_cidade": True}])
def test_linha_invalida(cliente, alteracao):
    dados = {"codigo": "X", "nome": "Teste", "id_cidade": cadastrar(cliente)}
    dados.update(alteracao)
    assert cliente.post("/linhas", json=dados).status_code == 422
    assert cliente.get("/linhas").json() == []


def test_unicidade_e_recuperacao(cliente):
    primeira = cadastrar(cliente, "  Maringá  ")
    assert cliente.post("/cidades", json={"nome": "Maringá"}).status_code == 409
    segunda = cadastrar(cliente, "Sarandi")
    dados = {"codigo": "001", "nome": "Teste", "id_cidade": primeira}
    assert cliente.post("/linhas", json=dados).status_code == 201
    assert cliente.post("/linhas", json=dados).status_code == 409
    dados["id_cidade"] = segunda
    assert cliente.post("/linhas", json=dados).status_code == 201
    assert len(cliente.get("/linhas").json()) == 2


def test_fk_garantida_no_postgresql(banco):
    with pytest.raises(IntegrityError):
        with banco.begin() as connection:
            connection.execute(text("INSERT INTO linha_onibus (id_cidade, codigo, nome) VALUES (999999, 'X', 'Teste')"))


def test_banco_indisponivel_sem_expor_segredo():
    def falhar():
        raise OperationalError("SELECT segredo", {}, Exception("senha_secreta"))
        yield
    app.dependency_overrides[get_db] = falhar
    try:
        with TestClient(app) as client:
            resposta = client.get("/cidades")
            assert resposta.status_code == 503
            assert "senha_secreta" not in resposta.text
    finally:
        app.dependency_overrides.clear()


def test_openapi():
    with TestClient(app) as client:
        spec = client.get("/openapi.json").json()
        docs = client.get("/docs").text
        assert "/documentacao/swagger-ui-bundle.js" in docs
        assert "/documentacao/swagger-ui.css" in docs
        assert "cdn.jsdelivr.net" not in docs
        assert client.get("/documentacao/swagger-ui-bundle.js").status_code == 200
        assert client.get("/documentacao/swagger-ui.css").status_code == 200
    assert set(spec["paths"]) == {"/", "/cidades", "/linhas"}
    for caminho in ("/cidades", "/linhas"):
        assert set(spec["paths"][caminho]) == {"get", "post"}
        assert {"201", "409", "422", "503"} <= set(spec["paths"][caminho]["post"]["responses"])
    assert "404" in spec["paths"]["/linhas"]["post"]["responses"]
    assert "id_cidade" not in spec["components"]["schemas"]["CidadeCreate"]["properties"]
