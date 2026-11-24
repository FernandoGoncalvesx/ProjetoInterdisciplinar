"""Modelos disponíveis e configuração do editor de cards."""
from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class Card:
    nome: str = "Azul"
    largura: int = 740
    altura: int = 1240
    foto_x: int = 112
    foto_y: int = 75
    foto_largura: int = 210
    foto_altura: int = 255

    def dados(self):
        return asdict(self)

MODELO = Card()
MODELOS = [
    {"id": "azul", "nome": "Azul", "fundo": "#06162e", "texto": "#ffe4a1"},
    {"id": "branco", "nome": "Branco", "fundo": "#f5f1e8", "texto": "#29170f"},
    {"id": "dourado", "nome": "Dourado", "fundo": "#ffd34d", "texto": "#251700"},
    {"id": "preto", "nome": "Preto", "fundo": "#121212", "texto": "#ffe4a1"},
    {"id": "roxo", "nome": "Roxo", "fundo": "#320061", "texto": "#ffffff"},
    {"id": "verde", "nome": "Verde", "fundo": "#003f2f", "texto": "#fff5cd"},
]
ATRIBUTOS = {"RIT": "Ritmo", "FIN": "Finalização", "PAS": "Passe",
             "DRI": "Drible", "DEF": "Defesa", "FIS": "Físico"}

