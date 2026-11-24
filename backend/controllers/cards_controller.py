"""View do criador de cards."""
from pathlib import Path
from flask import Blueprint, current_app, render_template, send_from_directory, abort
from backend.models.card import MODELO, MODELOS, ATRIBUTOS

cards = Blueprint("cards", __name__)

@cards.get("/Telas/fotos.html")
@cards.get("/cards")
def editor():
    return render_template(
        "paginas/fotos.html",
        paginas=current_app.config["PAGINAS"],
        pagina="Telas/fotos.html",
        modelo=MODELO.dados(),
        modelos=MODELOS,
        atributos=ATRIBUTOS,
    )


@cards.get("/assets/cards/modelos/<modelo_id>.png")
def imagem_modelo(modelo_id):
    if modelo_id not in {modelo["id"] for modelo in MODELOS}:
        abort(404)
    return send_from_directory(Path(__file__).resolve().parents[2] / "cards", f"card-{modelo_id}.png")

