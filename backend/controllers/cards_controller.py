from pathlib import Path
from flask import Blueprint, render_template, send_from_directory, abort, session
from backend.models.card import MODELO, MODELOS, ATRIBUTOS

cards = Blueprint("cards", __name__)

@cards.get("/Telas/fotos.html")
@cards.get("/cards")
def editor():
    if not session.get("usuario_id"):
        session["retornar_cards"] = True
    return render_template(
        "paginas/editor_card.html",
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

