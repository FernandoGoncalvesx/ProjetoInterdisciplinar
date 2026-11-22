"""Consultas do conteúdo do portal."""
from backend.models.banco import conectar_banco

def listar_jogadoras():
    with conectar_banco() as banco, banco.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM jogadoras ORDER BY posicao, nome")
        return cursor.fetchall()

def listar_noticias():
    with conectar_banco() as banco, banco.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT id, titulo, autor, imagem_url, texto FROM noticias ORDER BY id DESC")
        return cursor.fetchall()
