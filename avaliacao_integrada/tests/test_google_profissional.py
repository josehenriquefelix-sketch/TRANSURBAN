"""OAuth mantém autenticação separada da autorização profissional."""
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.main import app
from backend.auth import ACCESS


class GoogleProfissionalTests(unittest.TestCase):
    def callback(self, role, roles):
        client=TestClient(app)
        for key,value in {'tu_pkce':'verificador_ficticio','tu_oauth_state':'estado_ficticio','tu_oauth_role':role}.items():
            client.cookies.set(key,value,path='/auth')
        data={'access_token':'token_ficticio_para_teste','refresh_token':'refresh_ficticio','expires_in':3600}
        with patch('backend.auth.auth_request',side_effect=[data,{'id':'usuario_ficticio','email':'teste@example.invalid'}]),patch('backend.auth.papeis',return_value=roles):
            return client.get('/auth/google/callback?code=codigo_ficticio&flow=estado_ficticio',follow_redirects=False)

    def test_motorista_autorizado_retorna_ao_painel(self):
        r=self.callback('motorista',['passageiro','motorista'])
        self.assertEqual(r.headers['location'],'/motorista/')
        self.assertIn(ACCESS+'=',r.headers['set-cookie'])

    def test_gestor_autorizado_retorna_ao_painel(self):
        self.assertEqual(self.callback('gestor',['passageiro','gestor']).headers['location'],'/gestao/')

    def test_identidade_sem_vinculo_retorna_somente_ao_pedido(self):
        for role,path in [('motorista','/motorista/'),('gestor','/gestao/')]:
            with self.subTest(role=role):
                r=self.callback(role,['passageiro'])
                self.assertEqual(r.headers['location'],path+'?acesso=pendente')
                self.assertIn(ACCESS+'=',r.headers['set-cookie'])
                self.assertIn('tu_pkce=',r.headers['set-cookie'])

    def test_papel_adulterado_nao_cria_redirecionamento_externo(self):
        self.assertEqual(self.callback('https://example.invalid',['passageiro']).headers['location'],'/#inicio')

    def test_estado_invalido_preserva_area_sem_criar_sessao(self):
        c=TestClient(app);c.cookies.set('tu_oauth_role','motorista',path='/auth')
        r=c.get('/auth/google/callback?code=falso&flow=falso',follow_redirects=False)
        self.assertEqual(r.headers['location'],'/motorista/?erro=google_sessao_invalida#login')
        self.assertNotIn(ACCESS+'=',r.headers['set-cookie'])
