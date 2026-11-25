from io import BytesIO
from backend.models.foto import Foto, FotoInvalida, MAX_BYTES, MAX_PIXELS

def validar_imagem(dados):
    from PIL import Image, ImageOps, ImageStat, ImageFilter, UnidentifiedImageError
    if not dados or len(dados) > MAX_BYTES:
        raise FotoInvalida("Envie uma foto de até 5 MB.")
    try:
        with Image.open(BytesIO(dados)) as original:
            if original.format not in {"JPEG", "PNG", "WEBP"}:
                raise FotoInvalida("Use PNG, JPEG ou WebP.")
            if original.width * original.height > MAX_PIXELS:
                raise FotoInvalida("Use uma imagem de até 20 megapixels.")
            if getattr(original, "n_frames", 1) != 1:
                raise FotoInvalida("Envie uma foto estática, sem animação.")
            original.verify()
        with Image.open(BytesIO(dados)) as original:
            imagem = ImageOps.exif_transpose(original).convert("RGB")
            imagem.load()
    except (UnidentifiedImageError, OSError, SyntaxError, Image.DecompressionBombError) as erro:
        raise FotoInvalida("O arquivo não é uma imagem válida ou está danificado.") from erro
    if min(imagem.size) < 300:
        raise FotoInvalida("A foto precisa ter pelo menos 300 pixels em cada dimensão.")
    imagem.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
    amostra = imagem.convert("L")
    amostra.thumbnail((512, 512))
    luz = ImageStat.Stat(amostra).mean[0]
    avisos = []
    if luz < 55:
        avisos.append("A foto parece escura. Confira se o rosto e a roupa estão visíveis.")
    elif luz > 215:
        avisos.append("A foto parece muito clara. Confira se os detalhes foram preservados.")
    bordas = amostra.filter(ImageFilter.FIND_EDGES).crop((2, 2, amostra.width-2, amostra.height-2))
    if ImageStat.Stat(bordas).var[0] < 100:
        avisos.append("A foto pode ter pouca nitidez ou poucos detalhes. Confira a prévia.")
    return Foto(imagem, avisos)

