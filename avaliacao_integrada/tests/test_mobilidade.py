"""Proteções das áreas profissionais, senha e contrato do catálogo público."""
import unittest
import os
from unittest.mock import patch

import httpx
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError

from backend.auth import NovaSenha, auth_request, usuario_atual, endereco_aplicacao
from backend.main import app


class MobilidadeTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.addCleanup(app.dependency_overrides.clear)

    def test_hospedagem_usa_url_publica_e_permite_dominio_proprio(self):
        with patch.dict(os.environ, {"APP_URL": "", "RENDER_EXTERNAL_URL": "https://exemplo.onrender.com/"}):
            self.assertEqual(endereco_aplicacao(), "https://exemplo.onrender.com")
        with patch.dict(os.environ, {"APP_URL": "https://mobilidade.example.com/", "RENDER_EXTERNAL_URL": "https://exemplo.onrender.com"}):
            self.assertEqual(endereco_aplicacao(), "https://mobilidade.example.com")

    def test_senha_exige_comprimento_e_quatro_classes(self):
        for senha in ("Ab1!", "abcdefgh1!", "ABCDEFGH1!", "Abcdefgh!!", "Abcdefgh12"):
            with self.subTest(senha=senha), self.assertRaises(ValidationError):
                NovaSenha(senha=senha)
        self.assertEqual(NovaSenha(senha="Exemplo1!").senha, "Exemplo1!")

    def test_senha_anterior_tem_mensagem_especifica(self):
        resposta = httpx.Response(422, json={"error_code": "same_password"})
        with patch("backend.auth.httpx.request", return_value=resposta):
            with self.assertRaises(HTTPException) as erro:
                auth_request("PUT", "user", {"password": "Exemplo1!"}, token="ficticio")
        self.assertEqual(erro.exception.status_code, 422)
        self.assertIn("diferente da anterior", erro.exception.detail)

    def test_passageiro_nao_acessa_area_profissional_nem_mesmo_por_url(self):
        app.dependency_overrides[usuario_atual] = lambda: {"id": "ficticio", "email": "passageiro@example.com"}
        with patch("backend.auth.papeis", return_value=["passageiro"]):
            for path in ("/mobilidade/motorista", "/mobilidade/gestao/manifestacoes"):
                self.assertEqual(self.client.get(path).status_code, 403)
            self.assertEqual(self.client.put("/mobilidade/motorista/perfil", json={
                "nome_publico": "Teste", "modelo": "Modelo", "prefixo": "001"
            }).status_code, 403)

    def test_catalogo_nao_promete_previsao_ou_cobertura_completa(self):
        catalogo = self.client.get("/mobilidade/catalogo").json()
        self.assertFalse(catalogo["cobertura_completa"])
        self.assertEqual(len({linha["id"] for linha in catalogo["linhas"]}), len(catalogo["linhas"]))
        for linha in catalogo["linhas"]:
            self.assertFalse(linha["previsao_tempo_real"])
            if linha["tipo_servico"] == "municipal":
                self.assertEqual(linha["cidades"], ["Maringá"])
                self.assertTrue(linha["consulta_oficial_url"].startswith("https://bus2.info/reports/2you/43wpt?route="))
            else:
                self.assertTrue(linha["fonte_url"].startswith("https://www.der.pr.gov.br/"))
        self.assertEqual(sum(linha["ambito"] == "maringa" for linha in catalogo["linhas"]), 66)
        self.assertEqual(sum(linha["ambito"] == "metropolitano" for linha in catalogo["linhas"]), 22)

    def test_variante_de_bairro_nao_mistura_partidas_de_outro_destino(self):
        resposta = self.client.get("/mobilidade/horarios/der-0010254410-sp?tipo_dia=dias_uteis").json()
        self.assertEqual(len(resposta["horarios"]), 8)
        self.assertTrue(all(horario["variante"] == "SP" for horario in resposta["horarios"]))
        self.assertEqual(resposta["linha"]["bairros_atendidos"], ["Jardim São Paulo"])

    def test_municipal_maringa_tem_consulta_oficial_e_sentido_proprio(self):
        resposta = self.client.get("/mobilidade/horarios/maringa-460").json()
        self.assertEqual(resposta["linha"]["sentidos"], ["Ida", "Volta"])
        self.assertIn("route=velu", resposta["linha"]["consulta_oficial_url"])
        self.assertEqual(resposta["horarios"], [])
        self.assertIsNone(resposta["previsao_ao_vivo"])

    def test_domingo_sem_servico_nao_inventa_partidas(self):
        catalogo = self.client.get("/mobilidade/catalogo").json()
        linha = next(linha for linha in catalogo["linhas"] if linha["id"] == "der-0030254430")
        resultado = self.client.get(f"/mobilidade/horarios/{linha['id']}?tipo_dia=domingo_feriado").json()
        self.assertEqual(resultado["horarios"], [])
        self.assertIsNone(resultado["previsao_ao_vivo"])

    def test_callback_google_invalido_limpa_cookies_sem_abrir_sessao(self):
        resposta = self.client.get("/auth/google/callback?code=ficticio&flow=falso", follow_redirects=False)
        self.assertEqual(resposta.status_code, 307)
        self.assertIn("google_sessao_invalida", resposta.headers["location"])
        self.assertIn("tu_pkce=", resposta.headers["set-cookie"])
        self.assertNotIn("transurban_access=", resposta.headers["set-cookie"])

    def test_motorista_nao_avalia_propria_viagem(self):
        app.dependency_overrides[usuario_atual] = lambda: {"id": "proprio", "email": "teste@example.com"}
        linha = self.client.get("/mobilidade/catalogo").json()["linhas"][0]["id"]
        with patch("backend.controller.mobilidade.executar", return_value=[{"motorista_id": "proprio", "linha_id": linha}]) as banco:
            resposta = self.client.post("/mobilidade/manifestacoes", json={
                "linha_id": linha, "viagem_id": "00000000-0000-0000-0000-000000000001",
                "cidade": "Maringá", "tipo": "elogio", "categoria": "Atendimento",
                "nota_motorista": 5, "relato": "Tentativa de avaliar a propria viagem."
            })
        self.assertEqual(resposta.status_code, 422)
        banco.assert_called_once()

    def test_manifestacao_rejeita_cidade_que_nao_e_atendida_pela_linha(self):
        app.dependency_overrides[usuario_atual] = lambda: {"id": "passageiro", "email": "teste@example.com"}
        with patch("backend.controller.mobilidade.executar") as banco:
            resposta = self.client.post("/mobilidade/manifestacoes", json={
                "linha_id": "maringa-460", "cidade": "Sarandi", "tipo": "sugestao",
                "categoria": "Atendimento", "relato": "Mensagem de teste para uma cidade incompativel."
            })
        self.assertEqual(resposta.status_code, 422)
        banco.assert_not_called()

    def test_horarios_ordenados_preservam_todas_as_partidas(self):
        resultado = self.client.get("/mobilidade/horarios/der-0010254470?tipo_dia=sabado").json()
        partidas = [horario["partida"] for horario in resultado["horarios"]]
        self.assertTrue(partidas)
        self.assertEqual(partidas, sorted(partidas))


if __name__ == "__main__":
    unittest.main()
