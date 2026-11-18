"""Regras importantes do material: mesma fonte, fallback e chave composta."""
import os
import unittest
from unittest.mock import patch
from unittest.mock import MagicMock
from fastapi import Response
from backend.auth import cadastrar, reenviar_confirmacao, Cadastro, Email
from datetime import date
from fastapi.testclient import TestClient
from pydantic import ValidationError
from backend.main import app
from backend.auth import limitar
from backend import chat_dados, analise_dashboard
from backend.controller.materiais import Ordem, Material
from backend.notificacoes import mensagem_acesso, processar_um


class MaterialEscolarTests(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides[limitar]=lambda:None
        self.addCleanup(app.dependency_overrides.clear)
        self.client=TestClient(app)

    def test_chat_sem_ollama_preserva_conta_real_do_csv(self):
        with patch.dict(os.environ,{'OLLAMA_API_KEY':'','OLLAMA_MODELO':''}):
            pergunta=list(chat_dados.CONSULTAS)[0]
            resposta=self.client.post('/chat',json={'pergunta':' '+pergunta.upper()+' '})
        self.assertEqual(resposta.status_code,200)
        self.assertEqual(resposta.json()['resultado'],chat_dados.total_observacoes())
        self.assertIsNone(resposta.json()['explicacao'])
        self.assertTrue(resposta.json()['aviso'])

    def test_chat_nao_inventa_resposta_nem_envia_pergunta_arbitraria(self):
        with patch('backend.controller.chat.explicar') as modelo:
            r=self.client.post('/chat',json={'pergunta':'Qual ônibus está chegando agora?'}).json()
        self.assertIsNone(r['resultado']);modelo.assert_not_called()

    def test_falha_remota_nao_apaga_resultado(self):
        pergunta=list(chat_dados.CONSULTAS)[2]
        with patch('backend.controller.chat.explicar',side_effect=TimeoutError()):
            resposta=self.client.post('/chat',json={'pergunta':pergunta}).json()
        self.assertEqual(resposta['resultado'],chat_dados.total_atraso())
        self.assertIsNone(resposta['explicacao']);self.assertTrue(resposta['aviso'])

    def test_graficos_e_chat_reconciliam_com_resumo(self):
        self.assertEqual(sum(x['observacoes'] for x in analise_dashboard.observacoes_por_dia()),chat_dados.total_observacoes()['total_observacoes'])
        self.assertAlmostEqual(sum(x['atraso_total_min'] for x in analise_dashboard.atraso_por_dia()),chat_dados.total_atraso()['atraso_total_min'],places=4)

    def test_erro_de_csv_nao_e_escondido_por_fallback(self):
        with patch('backend.controller.chat.consultar',side_effect=ValueError('CSV inválido')):
            r=self.client.post('/chat',json={'pergunta':list(chat_dados.CONSULTAS)[0]})
        self.assertEqual(r.status_code,503)

    def test_estoque_exige_conta_administrativa(self):
        self.assertEqual(self.client.get('/gestao/estoque/materiais').status_code,401)

    def test_material_e_item_nao_aceitam_valores_invalidos(self):
        for preco in ['0','-1','1.123','NaN','Infinity']:
            with self.subTest(preco=preco),self.assertRaises(ValidationError):
                Material(nome='Peça de teste',categoria='pecas',valor_unitario=preco,estoque=1)
        with self.assertRaises(ValidationError):
            Ordem(unidade_id=1,data_ordem=date.today(),itens=[])
        with self.assertRaises(ValidationError):
            Ordem(unidade_id=1,data_ordem=date.today(),itens=[{'material_id':2,'quantidade':1},{'material_id':2,'quantidade':1}])

    def test_sem_smtp_nao_reserva_email_nem_finge_envio(self):
        with patch('backend.notificacoes.smtp_configurado',return_value=False),patch('backend.notificacoes.get_supabase') as banco:
            self.assertFalse(processar_um());banco.assert_not_called()

    def test_notificacao_diferencia_recebido_de_aprovado(self):
        registro={'papel':'motorista','evento':'recebido','pedido_id':'teste'}
        assunto,texto=mensagem_acesso(registro)
        self.assertIn('recebido',assunto);self.assertIn('não concede acesso',texto)
        registro['evento']='aprovado';assunto,texto=mensagem_acesso(registro)
        self.assertIn('aprovado',assunto);self.assertIn('/motorista/',texto)

    def test_chat_e_dados_separados_do_swagger_ds(self):
        ds=self.client.get('/openapi.json').json()['paths']
        ia=self.client.get('/dados/openapi.json').json()['paths']
        self.assertNotIn('/chat',ds);self.assertIn('/chat',ia)

    def test_cadastro_envia_redirecionamento_local_explicito(self):
        banco=MagicMock()
        banco.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value.data=[]
        with patch('backend.auth.get_supabase',return_value=banco),patch('backend.auth.auth_request',return_value={}) as chamada,patch.dict(os.environ,{'APP_URL':'http://127.0.0.1:8000'}):
            cadastrar(Cadastro(nome='Aluno de teste',email='aluno@example.com',cpf='52998224725',senha='Exemplo1!'),Response())
        self.assertEqual(chamada.call_args.args[1],'signup?redirect_to=http%3A%2F%2F127.0.0.1%3A8000%2F%23login')

    def test_reenvio_nao_utiliza_endereco_antigo_da_hospedagem(self):
        with patch('backend.auth.auth_request') as chamada,patch.dict(os.environ,{'APP_URL':'http://127.0.0.1:8000'}):
            reenviar_confirmacao(Email(email='aluno@example.com'))
        self.assertTrue(chamada.call_args.args[1].startswith('resend?redirect_to=http%3A%2F%2F127.0.0.1'))


if __name__=='__main__':unittest.main()
