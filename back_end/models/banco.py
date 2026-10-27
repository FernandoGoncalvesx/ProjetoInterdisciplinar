"""Conexão com o MySQL e verificação manual, sem modificar os dados.

O Servidor.py ainda não importa este módulo. Ele permanece em uso pelo diagnóstico
manual (python -m back_end.models.banco), sem integrar as páginas ao banco.
"""

import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv


# O .env pertence à raiz do projeto, independentemente da pasta usada no terminal.
PASTA_PROJETO = Path(__file__).resolve().parents[2]


def conectar_banco():
    """Abre uma conexão; quem chama deve fechá-la após o uso."""
    # Por padrão, variáveis já definidas no ambiente têm prioridade sobre o arquivo.
    load_dotenv(PASTA_PROJETO / ".env")
    senha = os.getenv("DB_PASSWORD")
    if not senha:
        raise ValueError("Preencha DB_PASSWORD no arquivo .env na raiz do projeto.")

    # Cada chamada abre uma conexão própria; o código chamador deve fechá-la após o uso.
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=senha,
        database=os.getenv("DB_NAME", "projeto_interdisciplinar"),
        charset="utf8mb4",
        connection_timeout=5,
    )


def verificar_banco():
    """Confirma as tabelas do portal e lista as colunas de usuarios."""
    # Os contextos fecham o cursor e a conexão, inclusive se ocorrer uma exceção.
    with conectar_banco() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT DATABASE()")
            print(f"Conectado ao banco: {cursor.fetchone()[0]}")
            cursor.execute("SHOW TABLES")
            tabelas = {linha[0] for linha in cursor.fetchall()}
            print("Tabelas: " + ", ".join(sorted(tabelas)))
            esperadas = {
                "usuarios", "jogadoras", "noticias", "proximos_jogos",
                "noticias_jogadoras", "proximos_jogos_jogadoras",
                "noticias_proximos_jogos",
            }
            ausentes = esperadas - tabelas
            if ausentes:
                print("Tabelas ausentes: " + ", ".join(sorted(ausentes)))
                print("Consulte database/README.md para preparar a estrutura.")
            cursor.execute("SHOW COLUMNS FROM usuarios")
            colunas = [linha[0] for linha in cursor.fetchall()]
            print("Colunas de usuarios: " + ", ".join(colunas))
            if "foto_perfil" not in colunas:
                print("A coluna foto_perfil ainda não existe na tabela usuarios.")


# Executado por python -m back_end.models.banco; importar o módulo não abre a conexão.
if __name__ == "__main__":
    try:
        verificar_banco()
    except ValueError as erro:
        raise SystemExit(str(erro)) from None
    except mysql.connector.Error as erro:
        # Mensagens próprias evitam exibir detalhes internos da conexão no terminal.
        mensagens = {
            1045: "Acesso negado. Confira DB_USER e DB_PASSWORD no arquivo .env.",
            1049: "Banco inexistente. Confira DB_NAME no arquivo .env.",
            1146: "A tabela usuarios ainda não existe no banco selecionado.",
            2003: "Não foi possível alcançar o MySQL. Confira o serviço, host e porta.",
        }
        raise SystemExit(mensagens.get(erro.errno, f"Falha na conexão MySQL (código {erro.errno}).")) from None
