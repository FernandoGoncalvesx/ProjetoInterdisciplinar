"""Validação e gravação do upload legado, com limpeza em caso de falha."""
from pathlib import Path
from uuid import uuid4
from backend.models.foto import MAX_ARQUIVOS, MAX_BYTES, FotoInvalida

PASTA_UPLOADS = Path(__file__).resolve().parents[1] / "uploads"


def salvar_uploads(arquivos):
    if not arquivos or len(arquivos) > MAX_ARQUIVOS:
        raise FotoInvalida("Selecione de 1 a 10 fotos.")

    fotos = []
    for arquivo in arquivos:
        dados = arquivo.read(MAX_BYTES + 1)
        if not dados or len(dados) > MAX_BYTES:
            raise FotoInvalida("Cada foto deve ter conteúdo e no máximo 5 MB.")
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
            raise FotoInvalida("Use imagens PNG, JPEG, GIF ou WebP.")
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
        raise

    return [p.name for p in salvos]
