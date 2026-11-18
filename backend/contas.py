"""Administração local das contas do portal."""
import argparse
from getpass import getpass

from mysql.connector import Error, IntegrityError
from werkzeug.security import generate_password_hash

from backend.models.banco import conectar_banco


def migrar(cursor):
    cursor.execute("SHOW COLUMNS FROM usuarios")
    colunas = {linha[0] for linha in cursor.fetchall()}
    if "nome_usuario" in colunas and "email" not in colunas:
        return "A tabela já usa nome_usuario."
    if "email" not in colunas or "nome_usuario" in colunas:
        raise ValueError("Estrutura de usuarios inesperada. Confira as colunas antes de migrar.")
    cursor.execute("ALTER TABLE usuarios RENAME COLUMN email TO nome_usuario")
    return "Tabela atualizada. Os identificadores e as senhas existentes foram preservados."


def criar(cursor):
    nome = input("Nome de exibição: ").strip()
    usuario = input("Nome de usuário: ").strip()
    if not (1 <= len(nome) <= 100 and 1 <= len(usuario) <= 254):
        raise ValueError("Informe o nome (até 100 caracteres) e o usuário (até 254).")
    senha = getpass("Senha: ")
    if not (1 <= len(senha) <= 1024) or senha != getpass("Confirme a senha: "):
        raise ValueError("Confira a senha e a confirmação.")
    cursor.execute("INSERT INTO usuarios (nome, nome_usuario, senha_hash) VALUES (%s, %s, %s)",
                   (nome, usuario, generate_password_hash(senha)))
    return "Conta criada."


def renomear(cursor):
    atual = input("Identificador atual da conta: ").strip()
    novo = input("Novo nome de usuário: ").strip()
    if not atual or not 1 <= len(novo) <= 254:
        raise ValueError("Informe o identificador atual e um novo usuário de até 254 caracteres.")
    cursor.execute("SELECT id FROM usuarios WHERE nome_usuario = %s", (atual,))
    conta = cursor.fetchone()
    if not conta:
        raise ValueError("Conta não encontrada.")
    cursor.execute("UPDATE usuarios SET nome_usuario = %s WHERE id = %s", (novo, conta[0]))
    return "Nome de usuário atualizado."


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("acao", choices=["migrar", "criar", "renomear"])
    acao = parser.parse_args().acao
    try:
        with conectar_banco() as banco, banco.cursor() as cursor:
            operacoes = {"migrar": migrar, "criar": criar, "renomear": renomear}
            mensagem = operacoes[acao](cursor)
            banco.commit()
        print(mensagem)
    except IntegrityError as erro:
        raise SystemExit("Nome de usuário já cadastrado." if erro.errno == 1062 else str(erro)) from None
    except (Error, ValueError) as erro:
        raise SystemExit(str(erro)) from None
