"""Consultas das jogadoras."""
from backend.models.banco import conectar_banco

def listar_jogadoras():
    with conectar_banco() as banco, banco.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM jogadoras ORDER BY posicao, nome")
        return cursor.fetchall()
