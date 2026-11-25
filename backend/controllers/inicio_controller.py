from flask import Blueprint, render_template
from backend.controllers.jogos_controller import contexto_jogos

inicio = Blueprint("inicio", __name__)


@inicio.get("/")
@inicio.get("/index.html")
def pagina():
    return render_template("paginas/inicio.html", pagina="index.html", **contexto_jogos())
