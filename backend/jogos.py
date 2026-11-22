"""Consulta a agenda e prepara os campos da tabela de jogos."""

import argparse
from datetime import datetime, timedelta, timezone

import mysql.connector

from backend.models.banco import conectar_banco

FUSO = timezone(timedelta(hours=-3))
COLUNAS = {
    "mandante": "VARCHAR(100) NULL",
    "visitante": "VARCHAR(100) NULL",
    "competicao": "VARCHAR(150) NULL",
    "placar_mandante": "SMALLINT UNSIGNED NULL",
    "placar_visitante": "SMALLINT UNSIGNED NULL",
    "situacao": "VARCHAR(8) NULL",
    "minuto": "SMALLINT UNSIGNED NULL",
    "atualizado_em": "DATETIME NULL",
}


def preparar_banco():
    """Adiciona apenas campos ausentes; mantém IDs, registros e relacionamentos."""
    with conectar_banco() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("SHOW COLUMNS FROM proximos_jogos")
            existentes = {linha[0] for linha in cursor.fetchall()}
            for coluna, definicao in COLUNAS.items():
                if coluna not in existentes:
                    cursor.execute(f"ALTER TABLE proximos_jogos ADD COLUMN {coluna} {definicao}")
        conexao.commit()


def listar_jogos():
    """Lê somente o banco; nenhuma chamada externa ocorre ao abrir a página."""
    with conectar_banco() as conexao:
        with conexao.cursor(dictionary=True) as cursor:
            agora = datetime.now(FUSO).replace(tzinfo=None)
            cursor.execute("""SELECT * FROM proximos_jogos
                WHERE data >= %s ORDER BY data LIMIT 50""",
                (agora,))
            futuros = cursor.fetchall()
            cursor.execute("""SELECT * FROM proximos_jogos
                WHERE data < %s ORDER BY data DESC LIMIT 50""", (agora,))
            return futuros + cursor.fetchall()


def agrupar_jogos(partidas):
    agora = datetime.now(FUSO).replace(tzinfo=None)
    hoje = agora.replace(hour=0, minute=0, second=0, microsecond=0)
    encerrados = {"FT", "AET", "PEN", "CANC", "ABD", "AWD", "WO"}
    ao_vivo = {"1H", "HT", "2H", "ET", "BT", "P", "LIVE", "INT", "SUSP"}
    grupos = {"proximos": [], "historico": []}
    for partida in partidas:
        situacao = partida.get("situacao")
        atual = partida["data"] >= agora or (situacao in ao_vivo and partida["data"] >= hoje)
        destino = "proximos" if atual and situacao not in encerrados else "historico"
        grupos[destino].append(partida)
    grupos["proximos"].sort(key=lambda jogo: jogo["data"])
    grupos["historico"].sort(key=lambda jogo: jogo["data"], reverse=True)
    return grupos


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("comando", choices=["preparar-banco"])
    parser.parse_args()
    try:
        preparar_banco()
    except mysql.connector.Error as erro:
        parser.exit(1, f"Erro MySQL ({erro.errno}). Confira a conexão e aplique o schema.\n")
    print("Banco preparado. Dados existentes preservados.")


if __name__ == "__main__":
    main()
