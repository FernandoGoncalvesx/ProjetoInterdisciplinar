"""Comando de preparação da tabela de jogos."""
import argparse
import mysql.connector
from database.migracoes.jogos import preparar_banco


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
