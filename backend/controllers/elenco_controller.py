from flask import Blueprint, current_app, render_template
from mysql.connector import Error as ErroBanco
from backend.models.jogadora import listar_jogadoras

elenco = Blueprint("elenco", __name__)


@elenco.get("/Telas/elenco.html")
def pagina():
    try:
        contexto = {"jogadoras": listar_jogadoras()}
    except (ErroBanco, ValueError):
        current_app.logger.warning("Conteúdo indisponível. Confira o banco e as migrações.")
        contexto = {"jogadoras": [], "banco_indisponivel": True}
    return render_template("paginas/elenco.html", pagina="Telas/elenco.html", **contexto)
