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
| usuarios | Identificação, nome de usuário único, hash de senha e caminho da foto |
| jogadoras | Nome, camisa e estatísticas |
| noticias | Título, autoria, texto e endereço da imagem |
| proximos_jogos | Adversário, local, data e ingresso |
| noticias_jogadoras | Jogadoras relacionadas a uma notícia |
| proximos_jogos_jogadoras | Jogadoras convocadas para um jogo |
| noticias_proximos_jogos | Jogos relacionados a uma notícia |

As três tabelas de relacionamento evitam listas e registros duplicados. Foram mantidas para preservar o modelo e eventuais registros existentes. `vel` permanece por compatibilidade; seu significado ainda precisa ser definido pela equipe.

As tabelas usam utf8mb4, utf8mb4_unicode_ci e InnoDB. Para acrescentar os campos da agenda a uma tabela antiga, execute `python -m backend.jogos preparar-banco`.

Configure `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD` e `DB_NAME` no `.env` da raiz. Para verificar a estrutura, sem modificar dados:

```powershell
.\venv\Scripts\python.exe -m backend.models.banco
```

O módulo de conexão atende ao diagnóstico e à leitura da página de jogos. Cadastre as partidas em `proximos_jogos`. Os arquivos de imagem ficam em `backend/uploads`.

## Contas de acesso

O login usa `nome_usuario` único e senha. `nome` é o nome de exibição.
Em bancos criados antes dessa alteração, execute na raiz do projeto:

```powershell
.\venv\Scripts\python.exe -m backend.contas migrar
.\venv\Scripts\python.exe -m backend.models.banco
```

A migração renomeia a coluna antiga e conserva os identificadores, hashes, IDs e
demais dados das contas. Pode ser executada novamente. O schema de instalações
novas já contém `nome_usuario`.

Para substituir o identificador de uma conta existente, execute
`python -m backend.contas renomear` e informe o identificador atual e o novo.
Para cadastrar uma conta, execute `python -m backend.contas criar`.
Esses comandos usam a conexão configurada no `.env`. As senhas cadastradas são
armazenadas como hashes compatíveis com o login.
