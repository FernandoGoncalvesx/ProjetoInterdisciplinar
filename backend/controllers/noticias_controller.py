import re
from threading import Lock
from flask import Blueprint, current_app, jsonify, render_template
from mysql.connector import Error as ErroBanco
from backend.models.noticia import listar_noticias

noticias = Blueprint("noticias", __name__)
coleta_noticias = Lock()


@noticias.get("/Telas/noticias.html")
def pagina():
    try:
        contexto = {"noticias": listar_noticias()}
    except (ErroBanco, ValueError):
        current_app.logger.warning("Conteúdo indisponível. Confira o banco e as migrações.")
        contexto = {"noticias": [], "banco_indisponivel": True}
    return render_template("paginas/noticias.html", pagina="Telas/noticias.html", **contexto)


@noticias.get("/api/crawler")
def api_crawler():
    if not coleta_noticias.acquire(blocking=False):
        return jsonify(erro="Já existe uma coleta em andamento. Tente novamente em instantes."), 409
    try:
        from backend.services.coleta_noticias import crawler_noticias
        return jsonify(crawler_noticias())
    except Exception:
        current_app.logger.exception("Erro ao coletar notícias da CBF")
        return jsonify(erro="Não foi possível atualizar as notícias da CBF"), 503
    finally:
        coleta_noticias.release()


@noticias.app_template_filter("texto_noticia")
def texto_noticia(texto):
    # Notícias antigas armazenam quebras como HTML; todo o restante continua escapado.
    return re.sub(r"<br\s*/?>", "\n", texto or "", flags=re.IGNORECASE)


@noticias.get("/api/noticias")
def api_noticias():
    try:
        return jsonify(listar_noticias())
    except (ErroBanco, ValueError):
        current_app.logger.exception("Erro ao consultar notícias")
        return jsonify(erro="Não foi possível consultar as notícias"), 503
