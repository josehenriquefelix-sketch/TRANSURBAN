import unittest
from unittest.mock import patch
from urllib.parse import unquote
from fastapi.testclient import TestClient
from backend.main import app

class RecuperacaoTests(unittest.TestCase):
    def test_destino_sem_fragmento_e_com_area(self):
        for area in ['passageiro','motorista','gestor']:
            with patch('backend.auth.auth_request',return_value={}) as auth:
                r=TestClient(app).post('/auth/esqueci-senha',json={'email':'teste@example.invalid','area':area})
                self.assertEqual(r.status_code,200)
                redirect=unquote(auth.call_args.args[1])
                self.assertIn('/recuperar-senha?area='+area,redirect)
                self.assertNotIn('#',redirect)

    def test_area_desconhecida_nao_envia_link(self):
        with patch('backend.auth.auth_request') as auth:
            r=TestClient(app).post('/auth/esqueci-senha',json={'email':'teste@example.invalid','area':'https://example.invalid'})
            self.assertEqual(r.status_code,422);auth.assert_not_called()

    def test_rota_dedicada_existe(self):
        r=TestClient(app).get('/recuperar-senha?area=gestor')
        self.assertEqual(r.status_code,200);self.assertIn('/recuperacao.js',r.text)
