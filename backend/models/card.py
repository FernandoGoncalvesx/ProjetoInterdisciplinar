from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class Card:
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
    {"id": "azul", "nome": "Azul", "texto": "#ffe4a1"},
    {"id": "branco", "nome": "Branco", "texto": "#29170f"},
    {"id": "dourado", "nome": "Dourado", "texto": "#251700"},
    {"id": "preto", "nome": "Preto", "texto": "#ffe4a1"},
    {"id": "roxo", "nome": "Roxo", "texto": "#ffffff"},
    {"id": "verde", "nome": "Verde", "texto": "#fff5cd"},
]
ATRIBUTOS = {"RIT": "Ritmo", "FIN": "Finalização", "PAS": "Passe",
             "DRI": "Drible", "DEF": "Defesa", "FIS": "Físico"}

