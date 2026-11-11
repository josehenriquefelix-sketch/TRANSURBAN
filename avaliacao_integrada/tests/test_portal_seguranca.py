"""Regressões de autenticação, permissão e separação dos Swaggers."""
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.auth import usuario_atual, validar_cpf
from backend.main import app


class PortalSegurancaTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.addCleanup(app.dependency_overrides.clear)

    def test_documentacao_ds_nao_inclui_totalizacoes(self):
        ds = self.client.get("/openapi.json").json()["paths"]
        dados = self.client.get("/dados/openapi.json").json()["paths"]
        self.assertIn("/cidades", ds)
        self.assertIn("/portal/recargas", ds)
        self.assertFalse(any(path.startswith("/ia/") for path in ds))
        self.assertEqual(len(dados), 5)
        self.assertTrue(all(path.startswith("/ia/") for path in dados))

    def test_visitante_nao_acessa_dados_privados(self):
        for path in ("/auth/me", "/portal/passe", "/portal/avaliacoes"):
            self.assertEqual(self.client.get(path).status_code, 401)
        self.assertEqual(self.client.post("/cidades", json={"nome": "Teste"}).status_code, 401)

    def test_passageiro_nao_altera_cidades_ou_linhas(self):
        app.dependency_overrides[usuario_atual] = lambda: {"id": "passageiro", "nome": "Passageiro", "email": "passageiro@example.com"}
        with patch.dict("os.environ", {"ADMIN_EMAILS": "equipe@example.com"}):
            self.assertEqual(self.client.post("/cidades", json={"nome": "Teste"}).status_code, 403)
            self.assertEqual(self.client.put("/cidades/1", json={"nome": "Teste"}).status_code, 403)
            self.assertEqual(self.client.delete("/linhas/1").status_code, 403)

    def test_cookie_de_sessao_nao_expoe_token_no_json(self):
        data = {"access_token": "token-ficticio", "refresh_token": "refresh-ficticio", "expires_in": 3600}
        with patch("backend.auth.auth_request", return_value=data):
            response = self.client.post("/auth/login", json={"identificador": "teste@example.com", "senha": "exemplo123"})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("access_token", response.json())
        self.assertIn("HttpOnly", response.headers["set-cookie"])
        self.assertIn("SameSite=lax", response.headers["set-cookie"])

    def test_rejeita_alteracao_de_outra_origem(self):
        response = self.client.post("/auth/login", headers={"Origin": "https://origem-externa.example"}, json={"identificador": "teste@example.com", "senha": "exemplo123"})
        self.assertEqual(response.status_code, 403)

    def test_validacao_de_cpf(self):
        self.assertEqual(validar_cpf("000.000.001-91"), "00000000191")
        for value in ("11111111111", "123", "00000000190", "abcdefghijk"):
            with self.assertRaises(ValueError):
                validar_cpf(value)


if __name__ == "__main__":
    unittest.main()
