from backend.models.banco import conectar_banco

def listar_noticias():
    with conectar_banco() as banco, banco.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT id, titulo, autor, imagem_url, texto FROM noticias ORDER BY id DESC")
        return cursor.fetchall()


def noticia_existe(titulo):
    with conectar_banco() as banco, banco.cursor() as cursor:
        cursor.execute("SELECT id FROM noticias WHERE titulo = %s LIMIT 1", (titulo,))
        return cursor.fetchone() is not None


def salvar_se_nova(titulo, autor, imagem_url, texto):
    with conectar_banco() as banco, banco.cursor() as cursor:
        cursor.execute("SELECT id FROM noticias WHERE titulo = %s LIMIT 1", (titulo,))
        if cursor.fetchone():
            return False
        cursor.execute("INSERT INTO noticias (titulo, autor, imagem_url, texto) VALUES (%s, %s, %s, %s)",
                       (titulo, autor, imagem_url, texto))
        banco.commit()
        return True
