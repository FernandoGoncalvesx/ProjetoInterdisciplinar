from werkzeug.security import check_password_hash, generate_password_hash
from backend.models.banco import conectar_banco


def buscar_por_nome(nome_usuario):
    with conectar_banco() as banco, banco.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT id, nome_usuario, senha_hash FROM usuarios WHERE nome_usuario = %s", (nome_usuario,))
        return cursor.fetchone()


def criar_usuario(nome_usuario, senha):
    with conectar_banco() as banco, banco.cursor() as cursor:
        cursor.execute("INSERT INTO usuarios (nome, nome_usuario, senha_hash) VALUES (%s, %s, %s)",
                       ("", nome_usuario, generate_password_hash(senha)))
        banco.commit()


def alterar_nome(usuario_id, nome_usuario, senha):
    with conectar_banco() as banco, banco.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT senha_hash FROM usuarios WHERE id = %s", (usuario_id,))
        conta = cursor.fetchone()
        if not conta or not check_password_hash(conta["senha_hash"], senha):
            return False
        cursor.execute("UPDATE usuarios SET nome_usuario = %s WHERE id = %s", (nome_usuario, usuario_id))
        banco.commit()
        return True
