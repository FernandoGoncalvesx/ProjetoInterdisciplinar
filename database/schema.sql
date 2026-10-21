-- Estrutura inicial, sem registros ou senhas de conexão.
-- IF NOT EXISTS não atualiza tabelas existentes; alterações exigem migrações.
CREATE DATABASE IF NOT EXISTS projeto_interdisciplinar
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE projeto_interdisciplinar;

-- Cadastro e autenticação ainda não foram ligados a esta tabela pela aplicação.
CREATE TABLE IF NOT EXISTS usuarios (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(254) NOT NULL UNIQUE,
    -- Reservado ao hash produzido pelo backend, nunca à senha original.
    senha_hash VARCHAR(255) NOT NULL,
    -- Caminho opcional do arquivo; não armazena os bytes da imagem.
    foto_perfil VARCHAR(500) NULL,
    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
