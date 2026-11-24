import re
import unittest
from unittest.mock import MagicMock, patch

from werkzeug.security import generate_password_hash, check_password_hash
from backend.app import app
from backend.contas import migrar


class TestAutenticacao(unittest.TestCase):
    def setUp(self):
        self.cliente = app.test_client()
        banco = patch("backend.models.usuario.conectar_banco")
        conexao = banco.start().return_value.__enter__.return_value
        self.addCleanup(banco.stop)
        self.conexao = conexao
        self.cursor = conexao.cursor.return_value.__enter__.return_value
        self.cursor.fetchone.return_value = {
            "id": 7, "nome_usuario": "ana.silva", "senha_hash": generate_password_hash("minha senha")
        }
        self.conta = "/Telas/login_page.html"

    def enviar(self, rota, **dados):
        html = self.cliente.get(self.conta).get_data(as_text=True)
        token = re.search(r'name="csrf" value="([^"]+)"', html).group(1)
        return self.cliente.post(rota, data=dict(csrf=token, **dados), follow_redirects=True)

    def test_entrar_e_sair(self):
        with patch("backend.controllers.jogos_controller.listar_jogos", return_value=[]):
            pagina = self.enviar("/api/login", nome_usuario=" ana.silva ", senha="minha senha")
        self.assertEqual(pagina.request.path, "/index.html")
        self.assertEqual(pagina.status_code, 200)
        self.assertEqual(self.cursor.execute.call_args.args[1], ("ana.silva",))
        with self.cliente.session_transaction() as sessao:
            self.assertEqual(sessao["usuario_id"], 7)
        self.enviar("/api/logout")
        with self.cliente.session_transaction() as sessao:
            self.assertNotIn("usuario_id", sessao)

    def test_credenciais_invalidas(self):
        for usuario in [self.cursor.fetchone.return_value, None]:
            with self.subTest(existe=bool(usuario)):
                self.cursor.fetchone.return_value = usuario
                pagina = self.enviar("/api/login", nome_usuario="ana.silva", senha="incorreta")
                self.assertIn("Usuário ou senha incorretos.", pagina.get_data(as_text=True))
                with self.cliente.session_transaction() as sessao:
                    self.assertNotIn("usuario_id", sessao)

    def test_sem_token(self):
        resposta = self.cliente.post("/api/login", follow_redirects=True)
        self.assertEqual(resposta.request.path, self.conta)
        self.assertIn("O formulário expirou", resposta.get_data(as_text=True))
        self.cursor.execute.assert_not_called()

    def test_cadastro_persiste_hash_e_confere_confirmacao(self):
        pagina = self.enviar("/api/cadastro", nome_usuario="nova", senha="segredo", confirmacao="outra")
        self.assertIn("confira a confirmação", pagina.get_data(as_text=True))
        self.cursor.execute.assert_not_called()
        pagina = self.enviar("/api/cadastro", nome_usuario="nova", senha="segredo", confirmacao="segredo")
        self.assertIn("Conta criada", pagina.get_data(as_text=True))
        parametros = self.cursor.execute.call_args.args[1]
        self.assertEqual(parametros[:2], ("", "nova"))
        self.assertTrue(check_password_hash(parametros[2], "segredo"))
        self.conexao.commit.assert_called_once()

    def test_alteracao_usuario_exige_senha_e_atualiza_sessao(self):
        with self.cliente.session_transaction() as sessao:
            sessao.update(usuario_id=7, nome="ana.silva")
        pagina = self.enviar("/api/conta/usuario", nome_usuario="ana.nova", senha="incorreta")
        self.assertIn("Confira sua senha atual", pagina.get_data(as_text=True))
        self.conexao.commit.assert_not_called()
        pagina = self.enviar("/api/conta/usuario", nome_usuario="ana.nova", senha="minha senha")
        self.assertIn("Nome de usuário atualizado", pagina.get_data(as_text=True))
        self.assertEqual(self.cursor.execute.call_args.args[1], ("ana.nova", 7))
        self.conexao.commit.assert_called_once()
        with self.cliente.session_transaction() as sessao:
            self.assertEqual(sessao["nome"], "ana.nova")

    def test_migracao_preserva_registros_e_pode_ser_repetida(self):
        cursor = MagicMock()
        cursor.fetchall.return_value = [("id",), ("email",), ("senha_hash",)]
        migrar(cursor)
        self.assertEqual(cursor.execute.call_args.args,
                         ("ALTER TABLE usuarios RENAME COLUMN email TO nome_usuario",))
        cursor.reset_mock()
        cursor.fetchall.return_value = [("id",), ("nome_usuario",), ("senha_hash",)]
        migrar(cursor)
        cursor.execute.assert_called_once_with("SHOW COLUMNS FROM usuarios")

    def test_migracao_recusa_colunas_ambiguas(self):
        cursor = MagicMock()
        cursor.fetchall.return_value = [("email",), ("nome_usuario",)]
        with self.assertRaises(ValueError):
            migrar(cursor)
        cursor.execute.assert_called_once_with("SHOW COLUMNS FROM usuarios")

class TestConteudo(unittest.TestCase):
    def test_elenco_e_noticias_renderizam_dados_escapados(self):
        cliente = app.test_client()
        with patch("backend.controllers.elenco_controller.listar_jogadoras", return_value=[
            {"nome": "Atleta teste", "posicao": "Atacante", "clube": "Clube teste", "imagem_url": None}
        ]):
            resposta = cliente.get("/Telas/elenco.html")
            self.assertEqual(resposta.status_code, 200)
            self.assertIn("Atleta teste", resposta.get_data(as_text=True))
        with patch("backend.controllers.noticias_controller.listar_noticias", return_value=[
            {"id": 1, "titulo": "Publicação teste", "autor": "Equipe", "imagem_url": None, "texto": "<script>alert(1)</script>"}
        ]):
            resposta = cliente.get("/Telas/noticias.html")
            self.assertEqual(resposta.status_code, 200)
            self.assertIn("&lt;script&gt;", resposta.get_data(as_text=True))
