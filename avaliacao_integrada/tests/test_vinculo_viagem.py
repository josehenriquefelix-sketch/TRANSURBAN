import unittest
from types import SimpleNamespace
from unittest.mock import patch
from pydantic import ValidationError
from fastapi import HTTPException
from backend.controller.mobilidade import InicioViagem, Posicao, PerfilMotorista, iniciar_viagem, atualizar_perfil


class VinculoViagemTests(unittest.TestCase):
    def test_cliente_nao_escolhe_outro_motorista_ou_veiculo_no_inicio(self):
        for campo in ['motorista_id', 'modelo', 'prefixo']:
            with self.subTest(campo=campo), self.assertRaises(ValidationError):
                InicioViagem(linha_id='maringa-460', sentido='Ida', **{campo: 'outro'})
        with self.assertRaises(ValidationError):
            Posicao(latitude=-23, longitude=-51, precisao_m=10, motorista_id='outro')

    def test_viagem_usa_veiculo_do_perfil_e_usuario_da_sessao(self):
        payloads = []
        class Query:
            def __init__(self, tabela): self.tabela = tabela
            def select(self, *args): return self
            def eq(self, *args): return self
            def limit(self, *args): return self
            def insert(self, valores): payloads.append(valores); return self
            def execute(self):
                return SimpleNamespace(data=[{'prefixo':'TESTE-1','modelo':'Veículo de teste'}] if self.tabela == 'tu_motorista' else [{'id':'viagem'}])
        db = SimpleNamespace(table=lambda tabela: Query(tabela))
        with patch('backend.controller.mobilidade.executar', side_effect=lambda consulta: consulta(db).execute().data):
            iniciar_viagem(InicioViagem(linha_id='maringa-460', sentido='Ida'), usuario={'id':'motorista-autenticado'})
        self.assertEqual(payloads, [{'motorista_id':'motorista-autenticado','linha_id':'maringa-460','sentido':'Ida','prefixo':'TESTE-1','modelo':'Veículo de teste'}])

    def test_perfil_e_veiculo_nao_mudam_com_viagem_ativa(self):
        with patch('backend.controller.mobilidade.executar', return_value=[{'id':'ativa'}]) as banco:
            with self.assertRaises(HTTPException) as erro:
                atualizar_perfil(PerfilMotorista(nome_publico='Teste',modelo='Modelo',prefixo='1'), usuario={'id':'motorista'})
        self.assertEqual(erro.exception.status_code,409)
        banco.assert_called_once()
