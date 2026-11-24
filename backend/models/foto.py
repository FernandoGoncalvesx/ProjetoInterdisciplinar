"""Dados e erros do processamento de fotos."""
from dataclasses import dataclass, field
from typing import Any

MAX_ARQUIVOS = 10
MAX_BYTES = 5 * 1024 * 1024
MAX_PIXELS = 20_000_000

class FotoInvalida(ValueError):
    """Imagem não pode ser usada no editor."""

class RecorteIndisponivel(RuntimeError):
    """Dependência ou modelo de segmentação indisponível."""

@dataclass
class Foto:
    imagem: Any
    avisos: list[str] = field(default_factory=list)

