"""Página da agenda e contexto compartilhado com a página inicial."""
from flask import Blueprint, current_app, render_template
from mysql.connector import Error as ErroBanco
from backend.models.jogo import agrupar_jogos, listar_jogos

jogos = Blueprint("jogos", __name__)


def contexto_jogos():
    try:
        return agrupar_jogos(listar_jogos())
    except (ErroBanco, ValueError):
        current_app.logger.warning("Consulta de jogos indisponível. Confira MySQL e a preparação do schema.")
        return dict(proximos=[], historico=[], banco_indisponivel=True)


@jogos.get("/Telas/proximos_jogos.html")
def pagina():
    return render_template("paginas/proximos_jogos.html", pagina="Telas/proximos_jogos.html", **contexto_jogos())
