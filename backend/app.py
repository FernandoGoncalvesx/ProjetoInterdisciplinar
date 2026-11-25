import os
import secrets
from pathlib import Path

if __name__ == "__main__" and __package__ is None:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
from flask import Flask, abort, jsonify, send_from_directory
from backend.controllers.autenticacao_controller import autenticacao
from backend.controllers.inicio_controller import inicio
from backend.controllers.noticias_controller import noticias
from backend.controllers.elenco_controller import elenco
from backend.controllers.jogos_controller import jogos
from backend.controllers.historia_controller import historia
from backend.controllers.fotos_controller import fotos
from backend.models.foto import MAX_ARQUIVOS, MAX_BYTES
from backend.controllers.cards_controller import cards

PASTA_ATUAL = Path(__file__).resolve().parent
PASTA_FRONTEND = PASTA_ATUAL.parent / "frontend"
PAGINAS = {
    "index.html": "Início",
    "Telas/noticias.html": "Notícias",
    "Telas/elenco.html": "Elenco",
    "Telas/proximos_jogos.html": "Próximos jogos",
    "Telas/historia.html": "História",
    "Telas/fotos.html": "Enviar fotos",
    "Telas/login_page.html": "Entrar",
}

app = Flask(__name__, template_folder=str(PASTA_FRONTEND / "templates"), static_folder=None)
load_dotenv(PASTA_ATUAL.parent / ".env")
app.config.update(
    SECRET_KEY=os.getenv("FLASK_SECRET_KEY") or secrets.token_hex(32),
    SESSION_COOKIE_SAMESITE="Lax",
    PAGINAS=PAGINAS,
    MAX_CONTENT_LENGTH=MAX_ARQUIVOS * MAX_BYTES + 1024 * 1024,
)
for controller in (inicio, autenticacao, noticias, elenco, jogos, historia, fotos, cards):
    app.register_blueprint(controller)


@app.context_processor
def navegacao():
    return {"paginas": app.config["PAGINAS"]}


@app.get("/<path:path>")
def arquivo_publico(path):
    pasta, _, arquivo = path.partition("/")
    if pasta in {"css", "js", "assets"} and arquivo:
        return send_from_directory(PASTA_FRONTEND / pasta, arquivo)
    abort(404)


@app.errorhandler(413)
def envio_grande(erro):
    return jsonify(mensagem="Envio muito grande. Envie até 10 fotos de 5 MB cada."), 413


if __name__ == "__main__":
    app.run(port=5000)
