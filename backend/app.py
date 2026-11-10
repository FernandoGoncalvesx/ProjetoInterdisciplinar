from pathlib import Path
from uuid import uuid4

# Permite executar este arquivo diretamente ou com python -m backend.app.
if __name__ == "__main__" and __package__ is None:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flask import Flask, abort, jsonify, render_template, request, send_from_directory
from mysql.connector import Error as ErroBanco
from backend.jogos import agrupar_jogos, listar_jogos
from backend.feed_noticias import cache_noticias, identificar_noticia

PASTA_ATUAL = Path(__file__).resolve().parent
PASTA_FRONTEND = PASTA_ATUAL.parent / "frontend"
PASTA_UPLOADS = PASTA_ATUAL / "uploads"
MAX_ARQUIVOS = 10
MAX_BYTES = 5 * 1024 * 1024
PAGINAS = {
    "index.html": "Início",
    "Telas/noticias.html": "Notícias",
    "Telas/elenco.html": "Elenco",
    "Telas/proximos_jogos.html": "Próximos jogos",
    "Telas/historia.html": "História",
    "Telas/fotos.html": "Enviar fotos",
}

app = Flask(__name__, template_folder=str(PASTA_FRONTEND / "templates"), static_folder=None)
app.config["MAX_CONTENT_LENGTH"] = MAX_ARQUIVOS * MAX_BYTES + 1024 * 1024


@app.get("/")
@app.get("/<path:path>")
def pagina(path="index.html"):
    if path in PAGINAS:
        template = "inicio" if path == "index.html" else Path(path).stem
        contexto = {}
        if template in {"proximos_jogos", "inicio"}:
            try:
                contexto.update(agrupar_jogos(listar_jogos()))
            except (ErroBanco, ValueError):
                contexto.update(proximos=[], historico=[], banco_indisponivel=True)
                app.logger.warning("Consulta de jogos indisponível. Confira MySQL e a preparação do schema.")
        return render_template(f"paginas/{template}.html", paginas=PAGINAS, pagina=path, **contexto)
    pasta, _, arquivo = path.partition("/")
    if pasta in {"css", "js", "assets"} and arquivo:
        return send_from_directory(PASTA_FRONTEND / pasta, arquivo)
    abort(404)


@app.get("/api/noticias")
def noticias():
    dados = cache_noticias.consultar(forcar=request.args.get("atualizar") == "1")
    compacto = request.args.get("compacto") == "1"
    itens = dados["noticias"][:1] if compacto else dados["noticias"]
    itens = [identificar_noticia(n) for n in itens]
    html = render_template("componentes/noticias.html", noticias=itens, compacto=compacto)
    return jsonify(**dados, html=html)


@app.errorhandler(413)
def envio_grande(erro):
    return jsonify(mensagem="Envio muito grande. Envie até 10 fotos de 5 MB cada."), 413


@app.post("/api/upload")
def upload_fotos():
    arquivos = [arquivo for arquivo in request.files.getlist("fotos") if arquivo.filename]
    if not arquivos or len(arquivos) > MAX_ARQUIVOS:
        return jsonify(mensagem="Selecione de 1 a 10 fotos."), 400

    fotos = []
    for arquivo in arquivos:
        dados = arquivo.read(MAX_BYTES + 1)
        if not dados or len(dados) > MAX_BYTES:
            return jsonify(mensagem="Cada foto deve ter conteúdo e no máximo 5 MB."), 400
        # Confere a assinatura, sem confiar na extensão ou no MIME enviado pelo navegador.
        if dados.startswith(b"\x89PNG\r\n\x1a\n"):
            extensao = ".png"
        elif dados.startswith(b"\xff\xd8\xff"):
            extensao = ".jpg"
        elif dados[:6] in (b"GIF87a", b"GIF89a"):
            extensao = ".gif"
        elif dados[:4] == b"RIFF" and dados[8:12] == b"WEBP":
            extensao = ".webp"
        else:
            return jsonify(mensagem="Use imagens PNG, JPEG, GIF ou WebP."), 400
        fotos.append((uuid4().hex + extensao, dados))

    salvos = []
    try:
        PASTA_UPLOADS.mkdir(parents=True, exist_ok=True)
        for nome, dados in fotos:
            caminho = PASTA_UPLOADS / nome
            with caminho.open("xb") as destino:
                salvos.append(caminho)
                destino.write(dados)
    except OSError:
        for caminho in salvos:
            caminho.unlink(missing_ok=True)
        app.logger.exception("Falha ao salvar fotos")
        return jsonify(mensagem="Não foi possível salvar as fotos. Tente novamente."), 500

    return jsonify(mensagem="Fotos enviadas com sucesso!", arquivos=[p.name for p in salvos])


if __name__ == "__main__":
    app.run(port=5000)
