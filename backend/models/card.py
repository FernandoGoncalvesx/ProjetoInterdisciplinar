"""Configuração do primeiro modelo editável."""
from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class Card:
    nome: str = "Azul"
    largura: int = 750
    altura: int = 1050
    foto_x: int = 125
    foto_y: int = 100
    foto_largura: int = 500
    foto_altura: int = 650

    def dados(self):
        return asdict(self)

MODELO = Card()

