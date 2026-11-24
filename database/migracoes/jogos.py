"""Migração aditiva dos campos da agenda."""
from backend.models.banco import conectar_banco

COLUNAS = {
    "mandante": "VARCHAR(100) NULL",
    "visitante": "VARCHAR(100) NULL",
    "competicao": "VARCHAR(150) NULL",
    "placar_mandante": "SMALLINT UNSIGNED NULL",
    "placar_visitante": "SMALLINT UNSIGNED NULL",
    "situacao": "VARCHAR(8) NULL",
    "minuto": "SMALLINT UNSIGNED NULL",
    "atualizado_em": "DATETIME NULL",
}


def preparar_banco():
    """Adiciona apenas campos ausentes; mantém IDs, registros e relacionamentos."""
    with conectar_banco() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("SHOW COLUMNS FROM proximos_jogos")
            existentes = {linha[0] for linha in cursor.fetchall()}
            for coluna, definicao in COLUNAS.items():
                if coluna not in existentes:
                    cursor.execute(f"ALTER TABLE proximos_jogos ADD COLUMN {coluna} {definicao}")
        conexao.commit()
