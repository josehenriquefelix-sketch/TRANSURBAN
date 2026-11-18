"""O iniciador não confunde um servidor local com acesso disponível na rede."""
import unittest
from unittest.mock import patch
from backend import abrir_app


class RedeTests(unittest.TestCase):
    def test_rede_nao_considera_loopback_como_celular(self):
        with patch.object(abrir_app.socket, 'gethostbyname_ex', return_value=('pc', [], ['127.0.0.1'])), \
                patch.object(abrir_app.socket, 'create_connection') as conectar:
            self.assertFalse(abrir_app.servidor_disponivel_na_rede())
            conectar.assert_not_called()

    def test_rede_bloqueada_nao_e_anunciada_como_disponivel(self):
        with patch.object(abrir_app.socket, 'gethostbyname_ex', return_value=('pc', [], ['192.168.1.10'])), \
                patch.object(abrir_app.socket, 'create_connection', side_effect=OSError):
            self.assertFalse(abrir_app.servidor_disponivel_na_rede())

    def test_nao_reutiliza_servidor_restrito_ao_pc_no_modo_celular(self):
        with patch.object(abrir_app, 'REDE', True), patch.object(abrir_app.sys, 'argv', ['abrir_app.py', '--rede']), \
                patch.object(abrir_app, 'mostrar_rede'), patch.object(abrir_app, 'porta_aberta', return_value=True), \
                patch.object(abrir_app, 'servico_transurban_ativo', return_value=True), \
                patch.object(abrir_app, 'servidor_disponivel_na_rede', return_value=False), \
                patch.object(abrir_app.webbrowser, 'open') as abrir:
            self.assertEqual(abrir_app.main(), 1)
            abrir.assert_not_called()
