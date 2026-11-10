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
    -- Apenas caminho ou URL da imagem, não os bytes do arquivo.
    foto_perfil VARCHAR(500) NULL,
    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Entidades e relacionamentos do portal.
CREATE TABLE IF NOT EXISTS jogadoras (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    -- Campo Jogadoras_vel do desenho: significado e unidade ainda a definir.
    vel VARCHAR(45) NULL,
    gols INT UNSIGNED NOT NULL DEFAULT 0,
    assistencias INT UNSIGNED NOT NULL DEFAULT 0,
    numero_camisa SMALLINT UNSIGNED NULL,
    status VARCHAR(30) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS proximos_jogos (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    api_fixture_id BIGINT UNSIGNED NULL UNIQUE,
    time_oponente VARCHAR(100) NOT NULL,
    mandante VARCHAR(100) NULL,
    visitante VARCHAR(100) NULL,
    competicao VARCHAR(150) NULL,
    placar_mandante SMALLINT UNSIGNED NULL,
    placar_visitante SMALLINT UNSIGNED NULL,
    situacao VARCHAR(8) NULL,
    minuto SMALLINT UNSIGNED NULL,
    atualizado_em DATETIME NULL,
    estadio VARCHAR(150) NULL,
    previsao_tempo VARCHAR(100) NULL,
    -- Horário local do evento; DATETIME não converte o fuso automaticamente.
    data DATETIME NOT NULL,
    preco_ingresso DECIMAL(10,2) NULL,
    CONSTRAINT chk_jogos_preco CHECK (preco_ingresso >= 0),
    INDEX idx_jogos_data (data)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS noticias (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    autor VARCHAR(100) NOT NULL,
    -- Guarda o endereço da imagem, não os bytes do arquivo.
    imagem_url VARCHAR(500) NULL,
    texto TEXT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- A chave composta impede repetir o mesmo par notícia/jogadora.
CREATE TABLE IF NOT EXISTS noticias_jogadoras (
    noticia_id INT UNSIGNED NOT NULL,
    jogadora_id INT UNSIGNED NOT NULL,
    PRIMARY KEY (noticia_id, jogadora_id),
    INDEX idx_nj_jogadora (jogadora_id),
    CONSTRAINT fk_nj_noticia FOREIGN KEY (noticia_id) REFERENCES noticias (id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_nj_jogadora FOREIGN KEY (jogadora_id) REFERENCES jogadoras (id)
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Cada linha representa uma jogadora convocada para um jogo.
CREATE TABLE IF NOT EXISTS proximos_jogos_jogadoras (
    jogo_id INT UNSIGNED NOT NULL,
    jogadora_id INT UNSIGNED NOT NULL,
    PRIMARY KEY (jogo_id, jogadora_id),
    INDEX idx_pjj_jogadora (jogadora_id),
    CONSTRAINT fk_pjj_jogo FOREIGN KEY (jogo_id) REFERENCES proximos_jogos (id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_pjj_jogadora FOREIGN KEY (jogadora_id) REFERENCES jogadoras (id)
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS noticias_proximos_jogos (
    noticia_id INT UNSIGNED NOT NULL,
    jogo_id INT UNSIGNED NOT NULL,
    PRIMARY KEY (noticia_id, jogo_id),
    INDEX idx_npj_jogo (jogo_id),
    CONSTRAINT fk_npj_noticia FOREIGN KEY (noticia_id) REFERENCES noticias (id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_npj_jogo FOREIGN KEY (jogo_id) REFERENCES proximos_jogos (id)
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
