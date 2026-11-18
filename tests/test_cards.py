import base64
import importlib.util
import io
import unittest
from unittest.mock import patch
from werkzeug.datastructures import MultiDict
from backend.app import app
from backend.models.foto import Foto, FotoInvalida, RecorteIndisponivel
from backend.services.validacao_imagem import validar_imagem


class CardsHTTPTest(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def enviar(self, dados=b"foto"):
        return self.client.post("/api/cards/processar", data={"foto": (io.BytesIO(dados), "foto.jpg")})

    def test_editor_e_recursos(self):
        for url in ("/cards", "/Telas/fotos.html"):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"/api/cards/processar", response.data)
            self.assertNotIn(b'id="form-upload"', response.data)
        for url in ("/js/fotos.js", "/js/editor-card.js", "/css/editor-card.css"):
            with self.client.get(url) as response:
                self.assertEqual(response.status_code, 200)

    def test_exatamente_uma_foto(self):
        self.assertEqual(self.client.post("/api/cards/processar").status_code, 400)
        data = MultiDict([("foto", (io.BytesIO(b"a"), "a.jpg")), ("foto", (io.BytesIO(b"b"), "b.jpg"))])
        self.assertEqual(self.client.post("/api/cards/processar", data=data).status_code, 400)

    def test_limite_requisicao(self):
        self.assertEqual(self.enviar(b"x" * (6 * 1024 * 1024)).status_code, 413)

    def test_sucesso_sem_cache(self):
        with patch("backend.controllers.fotos_controller.validar_imagem", return_value=Foto("imagem", ["Aviso"])), patch("backend.controllers.fotos_controller.recortar_pessoa", return_value=b"png"):
            response = self.enviar()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["avisos"], ["Aviso"])
        self.assertEqual(base64.b64decode(response.json["recorte"].split(",")[1]), b"png")
        self.assertEqual(response.headers["Cache-Control"], "no-store")

    def test_erros_controlados(self):
        for erro, status in [(FotoInvalida("Foto inválida"), 400), (ImportError("Pillow"), 503), (RecorteIndisponivel("Modelo"), 503)]:
            with self.subTest(status=status), patch.object(app.logger, "exception"), patch("backend.controllers.fotos_controller.validar_imagem", side_effect=erro), patch("backend.controllers.fotos_controller.recortar_pessoa") as recorte:
                self.assertEqual(self.enviar().status_code, status)
                recorte.assert_not_called()


@unittest.skipUnless(importlib.util.find_spec("PIL"), "Pillow não instalado")
class ValidacaoTest(unittest.TestCase):
    def foto(self, tamanho=(400, 600), cor="black"):
        from PIL import Image
        arquivo = io.BytesIO()
        Image.new("RGB", tamanho, cor).save(arquivo, format="PNG")
        return arquivo.getvalue()

    def test_arquivo_falso_e_pequeno(self):
        for dados in (b"arquivo falso", self.foto((100, 100))):
            with self.assertRaises(FotoInvalida):
                validar_imagem(dados)

    def test_avisos_e_redimensionamento(self):
        foto = validar_imagem(self.foto((2000, 3000)))
        self.assertEqual(foto.imagem.size, (1067, 1600))
        self.assertTrue(any("escura" in aviso for aviso in foto.avisos))

    def test_orientacao_exif(self):
        from PIL import Image
        arquivo = io.BytesIO()
        imagem = Image.new("RGB", (400, 600))
        exif = imagem.getexif()
        exif[274] = 6
        imagem.save(arquivo, format="JPEG", exif=exif)
        self.assertEqual(validar_imagem(arquivo.getvalue()).imagem.size, (600, 400))

    def test_recorte_png_e_vazio(self):
        from PIL import Image
        from types import SimpleNamespace
        from backend.services import recorte_pessoa as servico
        imagem = Image.new("RGBA", (400, 600), (0, 0, 0, 0))
        imagem.paste((255, 0, 0, 255), (100, 50, 300, 550))
        modulo = SimpleNamespace(new_session=lambda *a, **k: object(), remove=lambda *a, **k: imagem)
        with patch.dict("sys.modules", {"rembg": modulo}), patch.object(servico, "_sessao", None):
            png = servico.recortar_pessoa(imagem)
            resultado = Image.open(io.BytesIO(png))
            self.assertEqual(resultado.size, (200, 500))
            self.assertEqual(resultado.mode, "RGBA")
            imagem.paste((0, 0, 0, 0), (0, 0, 400, 600))
            with self.assertRaises(FotoInvalida):
                servico.recortar_pessoa(imagem)


if __name__ == "__main__":
    unittest.main()

