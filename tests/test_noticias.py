import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from backend import app as servidor
from backend.services import coleta_noticias as coletor
from backend.controllers import noticias_controller
from backend.models import noticia


class NoticiasTest(unittest.TestCase):
    def setUp(self):
        self.client = servidor.app.test_client()

    def test_consulta_existencia_por_titulo(self):
        with patch.object(noticia, "conectar_banco") as conectar:
            cursor = conectar.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value
            for resultado, esperado in ((None, False), ((1,), True)):
                cursor.fetchone.return_value = resultado
                self.assertEqual(noticia.noticia_existe("Título"), esperado)
                self.assertEqual(cursor.execute.call_args.args[1], ("Título",))

    def test_coleta_pula_noticia_existente_e_salva_nova(self):
        with patch.object(coletor, "sync_playwright") as playwright, \
                patch.object(coletor, "noticia_existe", side_effect=[True, False]), \
                patch.object(coletor, "_baixar_imagem", return_value="/assets/noticias/nova.png") as baixar, \
                patch.object(coletor, "salvar_se_nova") as salvar:
            browser = playwright.return_value.__enter__.return_value.chromium.launch.return_value
            page = browser.new_page.return_value
            page.locator.return_value.evaluate_all.side_effect = [
                ["/antiga", "/nova"], ["Antiga"], ["Nova"], ["Texto"], ["CBF"],
            ]
            page.locator.return_value.first.count.return_value = 1
            page.locator.return_value.first.evaluate.return_value = "https://exemplo.test/nova.png"
            coletor.crawler_noticias()
            baixar.assert_called_once_with(page, "https://exemplo.test/nova.png")
            salvar.assert_called_once_with("Nova", "CBF", "/assets/noticias/nova.png", "Texto")
            browser.close.assert_called_once()

    def test_model_salva_noticia_sem_duplicar_titulo(self):
        with patch.object(noticia, "conectar_banco") as conectar:
            banco = conectar.return_value.__enter__.return_value
            cursor = banco.cursor.return_value.__enter__.return_value
            cursor.fetchone.return_value = None
            self.assertTrue(noticia.salvar_se_nova("Título", "CBF", None, "Texto"))
            self.assertEqual(cursor.execute.call_args.args[1], ("Título", "CBF", None, "Texto"))
            banco.commit.assert_called_once()
            cursor.reset_mock()
            banco.reset_mock()
            cursor.fetchone.return_value = (1,)
            self.assertFalse(noticia.salvar_se_nova("Título", "CBF", None, "Texto"))
            cursor.execute.assert_called_once()
            banco.commit.assert_not_called()

    def test_api_retorna_noticias_e_trata_banco_indisponivel(self):
        with patch.object(noticias_controller, "listar_noticias", return_value=[{"id": 7, "titulo": "CBF"}]):
            resposta = self.client.get("/api/noticias")
            self.assertEqual(resposta.status_code, 200)
            self.assertEqual(resposta.json[0]["titulo"], "CBF")
        with patch.object(noticias_controller, "listar_noticias", side_effect=ValueError("configuração privada")):
            resposta = self.client.get("/api/noticias")
            self.assertEqual(resposta.status_code, 503)
            self.assertNotIn("privada", resposta.get_data(as_text=True))

    def test_coleta_e_falha_liberam_trava(self):
        with patch.object(coletor, "crawler_noticias", return_value={"mensagem": "ok"}) as coleta:
            self.assertEqual(self.client.get("/api/crawler").json, {"mensagem": "ok"})
            coleta.assert_called_once()
        with patch.object(coletor, "crawler_noticias", side_effect=RuntimeError("falha")):
            self.assertEqual(self.client.get("/api/crawler").status_code, 503)
        self.assertFalse(noticias_controller.coleta_noticias.locked())

    def test_coleta_concorrente_nao_abre_outro_navegador(self):
        noticias_controller.coleta_noticias.acquire()
        try:
            with patch.object(coletor, "crawler_noticias") as coleta:
                self.assertEqual(self.client.get("/api/crawler").status_code, 409)
                coleta.assert_not_called()
        finally:
            noticias_controller.coleta_noticias.release()

    def test_pagina_preserva_texto_escapado_e_quebras_antigas(self):
        noticias = [{"id": 1, "titulo": "Título", "autor": "CBF", "imagem_url": None,
                     "texto": "Primeiro<br><BR/><script>teste</script>"}]
        with patch.object(noticias_controller, "listar_noticias", return_value=noticias):
            resposta = self.client.get("/Telas/noticias.html")
        html = resposta.get_data(as_text=True)
        self.assertIn("Primeiro\n\n&lt;script&gt;teste&lt;/script&gt;", html)
        for caminho in ("/js/noticias.js", "/css/noticias.css"):
            self.assertIn(caminho, html)
            with self.client.get(caminho) as recurso:
                self.assertEqual(recurso.status_code, 200)
        self.assertIn('id="lista-noticias"', html)
        self.assertIn('id="detalhes-noticia"', html)
        dados = html.split('<script id="noticias-iniciais" type="application/json">', 1)[1].split('</script>', 1)[0]
        self.assertEqual(json.loads(dados), noticias)
        self.assertNotIn('<script>', dados)

    def test_imagem_salva_na_pasta_servida_pelo_portal(self):
        page = MagicMock()
        resposta = page.context.request.get.return_value
        resposta.ok = True
        resposta.headers = {"content-type": "image/png"}
        resposta.body.return_value = b"imagem de teste"
        with tempfile.TemporaryDirectory() as pasta, patch.object(coletor, "PASTA_IMAGENS", Path(pasta)):
            url = coletor._baixar_imagem(page, "https://exemplo.test/foto.png")
            self.assertTrue(url.startswith("/assets/noticias/"))
            self.assertEqual((Path(pasta) / url.rsplit("/", 1)[1]).read_bytes(), b"imagem de teste")
            resposta.headers = {"content-type": "text/html"}
            self.assertIsNone(coletor._baixar_imagem(page, "https://exemplo.test/falsa.png"))


if __name__ == "__main__":
    unittest.main()
