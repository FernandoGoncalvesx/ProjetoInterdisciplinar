"""API de processamento de uma foto, sem armazenamento de imagens."""
import base64
from flask import Blueprint, current_app, jsonify, request
from backend.models.foto import MAX_BYTES, FotoInvalida, RecorteIndisponivel
from backend.services.validacao_imagem import validar_imagem
from backend.services.recorte_pessoa import recortar_pessoa

fotos = Blueprint("fotos", __name__)

@fotos.post("/api/cards/processar")
def processar():
    if request.content_length and request.content_length > MAX_BYTES + 1024 * 1024:
        return jsonify(mensagem="Envie uma foto de até 5 MB."), 413
    arquivos = list(request.files.items(multi=True))
    if len(arquivos) != 1 or arquivos[0][0] != "foto" or not arquivos[0][1].filename:
        return jsonify(mensagem="Selecione exatamente uma foto."), 400
    try:
        foto = validar_imagem(arquivos[0][1].read(MAX_BYTES + 1))
        png = recortar_pessoa(foto.imagem)
        resposta = jsonify(
            recorte="data:image/png;base64," + base64.b64encode(png).decode("ascii"),
            avisos=foto.avisos,
        )
        resposta.headers["Cache-Control"] = "no-store"
        return resposta
    except FotoInvalida as erro:
        return jsonify(mensagem=str(erro)), 400
    except (ImportError, RecorteIndisponivel):
        current_app.logger.exception("Serviço de recorte indisponível")
        return jsonify(mensagem="O serviço de recorte está indisponível. Tente novamente após verificar a instalação no servidor."), 503
    except Exception:
        current_app.logger.exception("Falha no processamento da foto")
        return jsonify(mensagem="Não foi possível processar a foto. Tente novamente."), 500

