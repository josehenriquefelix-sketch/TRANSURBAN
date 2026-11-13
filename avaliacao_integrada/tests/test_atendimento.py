"""Contratos de autenticação, privacidade e acesso dos três portais."""
import unittest
from unittest.mock import patch
import httpx
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError
from backend.auth import Email, auth_request, usuario_atual
from backend.controller.suporte import Local
from backend.main import app


class AtendimentoTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.addCleanup(app.dependency_overrides.clear)

    def test_portais_separados(self):
        publico = self.client.get('/').text
        self.assertNotIn('id="gestao"', publico)
        self.assertNotIn('id="motorista"', publico)
        self.assertNotIn('href="/docs"', publico)
        self.assertNotIn('href="/gestao/', publico)
        for caminho, logo in [('/', 'passageiro'), ('/motorista/', 'motorista'), ('/gestao/', 'gestao')]:
            resposta = self.client.get(caminho)
            self.assertEqual(resposta.status_code, 200)
            self.assertIn(f'/logo-{logo}.svg', resposta.text)

    def test_erro_de_login_distingue_confirmacao_e_credenciais(self):
        for codigo, status, trecho in [('email_not_confirmed', 403, 'Confirme'), ('invalid_credentials', 401, 'senha inválidos')]:
            with self.subTest(codigo=codigo), patch('backend.auth.httpx.request', return_value=httpx.Response(400, json={'error_code': codigo})):
                with self.assertRaises(HTTPException) as erro:
                    auth_request('POST', 'token?grant_type=password', {})
                self.assertEqual(erro.exception.status_code, status)
                self.assertIn(trecho, erro.exception.detail)

    def test_email_normaliza_espacos_e_caixa(self):
        self.assertEqual(Email(email=' Pessoa@Example.com ').email, 'pessoa@example.com')

    def test_local_exige_coordenadas_pareadas_e_finitas(self):
        for coords in [{'latitude': 1}, {'latitude': float('nan'), 'longitude': 1}, {'latitude': 1, 'longitude': 181}]:
            with self.subTest(coords=coords), self.assertRaises(ValidationError):
                Local(cidade='Maringá', **coords)

    def test_visitante_nao_acessa_suporte_privado(self):
        for rota in ['/atendimento/meus-chamados', '/atendimento/meus-pedidos', '/atendimento/gestao/chamados', '/atendimento/gestao/pedidos-acesso']:
            self.assertEqual(self.client.get(rota).status_code, 401)

    def test_passageiro_nao_administra_nem_usa_fluxo_motorista(self):
        app.dependency_overrides[usuario_atual] = lambda: {'id': 'teste', 'email': 'teste@example.com'}
        with patch('backend.auth.papeis', return_value=['passageiro']):
            for rota in ['/atendimento/gestao/chamados', '/atendimento/gestao/pedidos-acesso']:
                self.assertEqual(self.client.get(rota).status_code, 403)
            self.assertEqual(self.client.post('/atendimento/motorista/chamados', json={}).status_code, 403)

    def test_pedido_profissional_nao_concede_papel(self):
        app.dependency_overrides[usuario_atual] = lambda: {'id': 'teste', 'email': 'teste@example.com'}
        with patch('backend.controller.suporte.executar', return_value=[{'id': 'pedido', 'status': 'pendente'}]) as banco:
            resultado = self.client.post('/atendimento/pedidos-acesso', json={'papel': 'motorista', 'justificativa': 'Vínculo a verificar pela equipe.'})
        self.assertEqual(resultado.status_code, 201)
        self.assertEqual(resultado.json()['status'], 'pendente')
        banco.assert_called_once()

    def test_cidade_incompativel_nao_grava_chamado(self):
        app.dependency_overrides[usuario_atual] = lambda: {'id': 'teste', 'email': 'teste@example.com'}
        with patch('backend.controller.suporte.executar') as banco:
            resultado = self.client.post('/atendimento/passageiro/chamados', json={'cidade': 'Sarandi', 'linha_id': 'maringa-460', 'categoria': 'Atendimento', 'assunto': 'Teste de cidade', 'mensagem': 'Relato com uma cidade incompatível.'})
        self.assertEqual(resultado.status_code, 422)
        banco.assert_not_called()
