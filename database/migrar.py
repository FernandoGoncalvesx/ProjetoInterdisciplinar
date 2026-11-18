"""Atualiza a estrutura existente e importa o elenco da versão anterior."""
import json
from pathlib import Path
from mysql.connector import Error
from backend.models.banco import conectar_banco
from database.migracoes.contas import migrar


def executar():
    with conectar_banco() as banco, banco.cursor() as cursor:
        cursor.execute("SELECT GET_LOCK('portal_migracao', 10)")
        if cursor.fetchone()[0] != 1:
            raise ValueError("Outra migração está em andamento.")
        try:
            print(migrar(cursor))
            cursor.execute("SHOW COLUMNS FROM jogadoras")
            existentes = {linha[0] for linha in cursor.fetchall()}
            for coluna, tipo in {"posicao": "VARCHAR(80)", "clube": "VARCHAR(150)",
                                 "imagem_url": "VARCHAR(500)"}.items():
                if coluna not in existentes:
                    cursor.execute(f"ALTER TABLE jogadoras ADD COLUMN {coluna} {tipo} NULL")
            cursor.execute("""CREATE TABLE IF NOT EXISTS migracoes (
                nome VARCHAR(100) PRIMARY KEY,
                aplicada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB""")
            cursor.execute("SELECT nome FROM migracoes WHERE nome = %s", ("elenco_inicial",))
            if not cursor.fetchone():
                caminho = Path(__file__).parent / "migracoes" / "elenco_inicial.json"
                for atleta in json.loads(caminho.read_text(encoding="utf-8")):
                    cursor.execute("SELECT id FROM jogadoras WHERE nome = %s", (atleta["nome"],))
                    if not cursor.fetchone():
                        cursor.execute("INSERT INTO jogadoras (nome, posicao, clube) VALUES (%s, %s, %s)",
                                       (atleta["nome"], atleta["posicao"], atleta["clube"]))
                cursor.execute("INSERT INTO migracoes (nome) VALUES (%s)", ("elenco_inicial",))
            banco.commit()
            print("Estrutura atualizada e importação do elenco concluída.")
        except Exception:
            banco.rollback()
            raise
        finally:
            cursor.execute("SELECT RELEASE_LOCK('portal_migracao')")
            cursor.fetchone()


if __name__ == "__main__":
    try:
        executar()
    except (Error, ValueError) as erro:
        raise SystemExit(str(erro)) from None
