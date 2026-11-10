# Banco de dados

O arquivo `schema.sql` é a única entrada para criar a estrutura. Dentro do MySQL:

```sql
SOURCE C:/Users/gcfer/Desktop/ProjetoInterdisciplinar/database/schema.sql;
USE projeto_interdisciplinar;
SHOW TABLES;
```

O script preserva os registros e cria tabelas ausentes; não migra colunas de tabelas existentes. Não é necessário apagar o banco para executá-lo.

| Tabela | Conteúdo |
| --- | --- |
| usuarios | Identificação, e-mail único, hash de senha e caminho da foto |
| jogadoras | Nome, camisa e estatísticas |
| noticias | Título, autoria, texto e endereço da imagem |
| proximos_jogos | Adversário, local, data e ingresso |
| noticias_jogadoras | Jogadoras relacionadas a uma notícia |
| proximos_jogos_jogadoras | Jogadoras convocadas para um jogo |
| noticias_proximos_jogos | Jogos relacionados a uma notícia |

As três tabelas de relacionamento evitam listas e registros duplicados. Foram mantidas para preservar o modelo e eventuais registros existentes. `vel` permanece por compatibilidade; seu significado ainda precisa ser definido pela equipe.

As tabelas declaram utf8mb4, utf8mb4_unicode_ci e InnoDB explicitamente, inclusive quando criadas em um banco existente com outros padrões. A cláusula repetida ON UPDATE RESTRICT foi removida porque já é o padrão do MySQL. Índices e chaves estrangeiras foram preservados. A integração da API-Football acrescentou campos de placar e identificação na tabela de jogos, preservando os dados. Veja [o guia da API](API_FOOTBALL.md).

Configure `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD` e `DB_NAME` no `.env` da raiz. Para verificar a estrutura, sem modificar dados:

```powershell
.\venv\Scripts\python.exe -m backend.models.banco
```

O módulo de conexão atende ao diagnóstico, à sincronização da API-Football e à leitura da página de jogos. Os uploads ainda não gravam no MySQL. Os arquivos de imagem ficam em `backend/uploads`, não em colunas binárias.
