import unittest
from datetime import datetime, timezone
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.main import app
from backend.auth import usuario_atual, gestor_autorizado


class GestaoOperacaoTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_operacao_exige_gestao_autorizada(self):
        self.assertEqual(self.client.get('/mobilidade/gestao/viagens').status_code, 401)
        app.dependency_overrides[usuario_atual] = lambda: {'id':'passageiro','email':'passageiro@example.com'}
        with patch('backend.auth.papeis', return_value=['passageiro']):
            self.assertEqual(self.client.get('/mobilidade/gestao/viagens').status_code, 403)

    def test_gestao_ve_motorista_sem_expor_identificador_da_conta(self):
        app.dependency_overrides[gestor_autorizado] = lambda: {'id':'gestor','email':'gestor@example.com'}
        rows = [
            [{'id':'viagem','motorista_id':'id-privado','linha_id':'maringa-460','prefixo':'TESTE-1','modelo':'Modelo de teste','sentido':'Ida'}],
            [{'usuario_id':'id-privado','nome_publico':'Motorista de teste'}],
            [{'viagem_id':'viagem','latitude':-23.4,'longitude':-51.9,'registrada_em':datetime.now(timezone.utc).isoformat()}],
        ]
        with patch('backend.controller.mobilidade.escopos_gestao', return_value=['maringa']), \
                patch('backend.controller.mobilidade.executar', side_effect=rows):
            r = self.client.get('/mobilidade/gestao/viagens')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()[0]['motorista']['nome'], 'Motorista de teste')
        self.assertTrue(r.json()[0]['posicao']['recente'])
        self.assertNotIn('motorista_id', r.json()[0])
        self.assertNotIn('email', r.text)

    def test_sem_escopo_nao_consulta_viagens(self):
        app.dependency_overrides[gestor_autorizado] = lambda: {'id':'gestor','email':'gestor@example.com'}
        with patch('backend.controller.mobilidade.escopos_gestao', return_value=[]), \
                patch('backend.controller.mobilidade.executar') as banco:
            self.assertEqual(self.client.get('/mobilidade/gestao/viagens').json(), [])
            banco.assert_not_called()

    def test_ferramentas_tecnicas_nao_fazem_parte_da_gestao(self):
        page = self.client.get('/gestao/').text
        for path in ['/gestao/materiais.html','/gestao/banco.html']:
            self.assertNotIn(path, page)
            self.assertEqual(self.client.get(path).status_code, 404)
        self.assertIn('Ocorrências recebidas', page)
        self.assertEqual(self.client.get('/estudo/materiais.html').status_code, 404)
