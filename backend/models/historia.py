"""Leitura dos dados históricos do portal."""
import json
from pathlib import Path


def carregar_historia():
    with (Path(__file__).resolve().parents[1] / "dados" / "historia.json").open(encoding="utf-8") as arquivo:
        return json.load(arquivo)
