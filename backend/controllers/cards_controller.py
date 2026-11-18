"""View do criador de cards."""
from flask import Blueprint, current_app, render_template
from backend.models.card import MODELO

cards = Blueprint("cards", __name__)

@cards.get("/Telas/fotos.html")
@cards.get("/cards")
def editor():
    return render_template(
        "paginas/fotos.html",
        paginas=current_app.config["PAGINAS"],
        pagina="Telas/fotos.html",
        modelo=MODELO.dados(),
    )

