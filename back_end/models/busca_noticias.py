
from back_end.models.banco import conectar_banco


def buscar_noticias():
    """
    Recupera todas as notícias cadastradas no banco de dados.
    Retorna uma lista de dicionários.
    """

    try:
        conexao = conectar_banco()

        cursor = conexao.cursor(dictionary=True)

        consulta = """
            SELECT
                id,
                titulo,
                autor,
                imagem_url,
                texto
            FROM noticias
            ORDER BY id DESC
        """

        cursor.execute(consulta)

        noticias = cursor.fetchall()

        return noticias

    finally:
        if cursor is not None:
            cursor.close()

        if conexao is not None and conexao.is_connected():
            conexao.close()
