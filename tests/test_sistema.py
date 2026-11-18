import io
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch

from backend import app as servidor
from backend.models import banco


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        for nome, valor in attrs:
            if nome in {"href", "src"} and valor.startswith("/"):
                self.links.append(valor)


class SistemaTest(unittest.TestCase):
    def setUp(self):
        self.client = servidor.app.test_client()
        for funcao in ["listar_jogadoras", "listar_noticias"]:
            consulta_conteudo = patch.object(servidor, funcao, return_value=[])
            consulta_conteudo.start()
            self.addCleanup(consulta_conteudo.stop)
        consulta = patch.object(servidor, "listar_jogos", return_value=[])
        consulta.start()
        self.addCleanup(consulta.stop)
        self.pasta = tempfile.TemporaryDirectory()
        self.addCleanup(self.pasta.cleanup)
        self.patch = patch.object(servidor, "PASTA_UPLOADS", Path(self.pasta.name))
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def enviar(self, arquivos):
        return self.client.post("/api/upload", data={"fotos": arquivos})

    def test_paginas_links_e_menu(self):
        for pagina in servidor.PAGINAS:
            with self.subTest(pagina=pagina):
                response = self.client.get("/" + pagina)
                self.assertEqual(response.status_code, 200)
                html = response.get_data(as_text=True)
                self.assertNotIn("{%", html)
                self.assertEqual(html.count('<h1>'), 1)
                self.assertEqual(html.count('aria-current="page"'), 1)
                self.assertEqual(html.count('<header class="cabecalho">'), 1)
                links = Links()
                links.feed(html)
                for link in links.links:
                    with self.client.get(link) as recurso:
                        self.assertEqual(recurso.status_code, 200, link)

    def test_arquivos_privados_e_templates_nao_sao_publicados(self):
        for path in ["/.env", "/base.html", "/templates/layout.html", "/templates/paginas/fotos.html", "/uploads/teste.png", "/frontend/base.html", "/assets/../../.env"]:
            self.assertEqual(self.client.get(path).status_code, 404, path)

    def test_fotos_tem_pagina_propria(self):
        inicio = self.client.get('/').get_data(as_text=True)
        fotos = self.client.get('/Telas/fotos.html').get_data(as_text=True)
        self.assertNotIn('id="form-upload"', inicio)
        self.assertIn('href="/Telas/fotos.html"', inicio)
        self.assertIn('id="form-foto-card" action="/api/cards/processar"', fotos)
        self.assertIn('type="submit" disabled', fotos)

    def test_fotos_repetidas_recebem_nomes_unicos(self):
        nomes = []
        for _ in range(2):
            response = self.enviar((io.BytesIO(b"\x89PNG\r\n\x1a\nconteudo"), "../../foto.png"))
            self.assertEqual(response.status_code, 200)
            nome = response.json["arquivos"][0]
            self.assertRegex(nome, r"^[0-9a-f]{32}\.png$")
            self.assertTrue((Path(self.pasta.name) / nome).exists())
            nomes.append(nome)
        self.assertNotEqual(*nomes)

    def test_lote_invalido_nao_salva_nada(self):
        response = self.enviar([(io.BytesIO(b"\xff\xd8\xffimagem"), "boa.jpg"), (io.BytesIO(b"script"), "falsa.png")])
        self.assertEqual(response.status_code, 400)
        self.assertEqual(list(Path(self.pasta.name).iterdir()), [])

    def test_envio_vazio_quantidade_e_tamanho(self):
        self.assertEqual(self.enviar([]).status_code, 400)
        self.assertEqual(self.enviar((io.BytesIO(b""), "vazia.png")).status_code, 400)
        arquivos = [(io.BytesIO(b"GIF89aconteudo"), f"{n}.gif") for n in range(11)]
        self.assertEqual(self.enviar(arquivos).status_code, 400)
        with patch.object(servidor, "MAX_BYTES", 10):
            self.assertEqual(self.enviar((io.BytesIO(b"\x89PNG\r\n\x1a\nexcesso"), "grande.png")).status_code, 400)

    def test_falha_de_gravacao_limpa_lote(self):
        original = Path.open
        chamadas = []

        def abrir(caminho, *args, **kwargs):
            chamadas.append(caminho)
            if len(chamadas) == 2:
                raise OSError("Falha de teste")
            return original(caminho, *args, **kwargs)

        with patch.object(Path, "open", abrir), patch.object(servidor.app.logger, "exception"):
            response = self.enviar([(io.BytesIO(b"GIF89aok"), "a.gif"), (io.BytesIO(b"GIF89aok"), "b.gif")])
        self.assertEqual(response.status_code, 500)
        self.assertEqual(list(Path(self.pasta.name).iterdir()), [])

    def test_limite_global_retorna_json(self):
        with patch.dict(servidor.app.config, MAX_CONTENT_LENGTH=10):
            response = self.enviar((io.BytesIO(b"x" * 20), "foto.jpg"))
        self.assertEqual(response.status_code, 413)
        self.assertIn("mensagem", response.json)

    def test_diagnostico_de_banco_incompleto(self):
        from unittest.mock import MagicMock
        conexao = MagicMock()
        cursor = conexao.__enter__.return_value.cursor.return_value.__enter__.return_value
        cursor.fetchone.return_value = ("projeto_interdisciplinar",)
        cursor.fetchall.return_value = [("jogadoras",)]
        with patch.object(banco, "conectar_banco", return_value=conexao):
            with self.assertRaisesRegex(ValueError, "schema.sql"):
                banco.verificar_banco()
        self.assertNotIn("SHOW COLUMNS FROM usuarios", [call.args[0] for call in cursor.execute.call_args_list])


if __name__ == "__main__":
    unittest.main()

