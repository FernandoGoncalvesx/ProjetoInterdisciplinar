def migrar(cursor):
    cursor.execute("SHOW COLUMNS FROM usuarios")
    colunas = {linha[0] for linha in cursor.fetchall()}
    if "nome_usuario" in colunas and "email" not in colunas:
        return "A tabela já usa nome_usuario."
    if "email" not in colunas or "nome_usuario" in colunas:
        raise ValueError("Estrutura de usuarios inesperada. Confira as colunas antes de migrar.")
    cursor.execute("ALTER TABLE usuarios RENAME COLUMN email TO nome_usuario")
    return "Tabela atualizada. Os identificadores e as senhas existentes foram preservados."

