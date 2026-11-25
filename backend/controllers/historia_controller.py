from flask import Blueprint, render_template
from backend.models.historia import carregar_historia

historia = Blueprint("historia", __name__)


@historia.get("/Telas/historia.html")
def pagina():
    return render_template("paginas/historia.html", pagina="Telas/historia.html", historia=carregar_historia())
