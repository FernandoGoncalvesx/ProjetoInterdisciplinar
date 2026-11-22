"""Remoção local do fundo com sessão reutilizada e concorrência limitada."""
import os
from io import BytesIO
from pathlib import Path
from threading import Lock
from backend.models.foto import FotoInvalida, RecorteIndisponivel

_trava = Lock()
_sessao = None

def recortar_pessoa(imagem):
    global _sessao
    if not _trava.acquire(blocking=False):
        raise RecorteIndisponivel("Outra foto está sendo processada. Tente novamente em instantes.")
    try:
        try:
            cache = Path(__file__).resolve().parents[1] / "cache_modelos"
            os.environ.setdefault("U2NET_HOME", str(cache))
            from rembg import new_session, remove
            if _sessao is None:
                _sessao = new_session("u2net_human_seg", providers=["CPUExecutionProvider"])
            resultado = remove(imagem, session=_sessao).convert("RGBA")
        except Exception as erro:
            raise RecorteIndisponivel(
                "O recorte está indisponível. Verifique as dependências e o download do modelo no servidor."
            ) from erro
        alfa = resultado.getchannel("A")
        limites = alfa.point(lambda valor: 255 if valor > 30 else 0).getbbox()
        if limites is None:
            raise FotoInvalida("Não foi possível obter um recorte. Tente outra foto com a pessoa bem visível.")
        resultado = resultado.crop(limites)
        saida = BytesIO()
        resultado.save(saida, format="PNG")
        return saida.getvalue()
    finally:
        _trava.release()

