# Portal da Seleção Feminina Brasileira

Portal em Flask com seis páginas, notícias de futebol feminino e envio de fotos. As páginas herdam `base.html`, com menu e rodapé compartilhados em componentes. Jinja2 é usado para os dados dinâmicos de notícias e jogos. CSS e JavaScript são compartilhados; não há etapa de build nem dependência de Bootstrap.

## Preparação e execução

Na raiz do projeto, no PowerShell, crie o ambiente somente se ainda não existir:

```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\waitress-serve.exe --host=127.0.0.1 --port=8081 backend.app:app
```

Abra http://127.0.0.1:8081. Não abra os HTMLs diretamente: agora eles são templates renderizados pelo Flask. As URLs existentes, incluindo `/index.html` e `/Telas/historia.html`, continuam disponíveis.

Para desenvolvimento local também é possível usar:

```powershell
.\venv\Scripts\python.exe -m backend.app
```

Nesse caso, abra http://127.0.0.1:5000. O modo de depuração fica desativado. Apache e túnel são opcionais; consulte [INICIAR_SERVIDOR.md](INICIAR_SERVIDOR.md).

## Estrutura

| Caminho | Responsabilidade |
| --- | --- |
| `backend/app.py` | Rotas das páginas, arquivos públicos e upload |
| `backend/feed_noticias.py` | Atualização e cache do RSS |
| `backend/models/banco.py` | Conexão compartilhada e diagnóstico do MySQL |
| `backend/uploads/` | Arquivos recebidos, ignorados pelo Git |
| `frontend/templates/paginas/` | Conteúdo específico das páginas |
| `frontend/css/` | Estilos compartilhados em `base.css` e identidade visual em `tema.css` |
| `frontend/js/portal.js` | Menu, notícias e upload |
| `frontend/assets/` | Logo e ícone do portal |
| `database/schema.sql` | Criação das sete tabelas, sem registros |
| `tests/test_sistema.py` | Verificação de páginas, links, upload e diagnóstico |

## O que está funcionando

- Navegação entre início, notícias, elenco, próximos jogos, história e envio de fotos.
- Menu acessível e responsivo, com botão identificado no celular e ano atualizado.
- Notícias de exemplo: o diálogo usa o mesmo título e texto do card, sem duplicação no JavaScript.
- Upload de até 10 imagens PNG, JPEG, GIF ou WebP, de até 5 MB cada, para `backend/uploads`.

A API recebe `POST /api/upload`, com campo multipart `fotos`. Valida quantidade, tamanho e assinatura do formato antes de gravar. Gera nomes UUID para evitar sobrescritas e remove arquivos do lote caso ocorra falha de gravação. A verificação de assinatura não decodifica a imagem inteira nem substitui moderação. Uploads não têm rota pública de download.

Sucesso retorna status 200 com `mensagem` e `arquivos`. Erros retornam JSON com `mensagem`: 400 para seleção inválida, 413 para requisição acima do limite global e 500 para falha de gravação. O navegador mantém a seleção quando o envio falha.

## Banco de dados

Consulte [database/README.md](database/README.md). O schema preserva usuários, jogadoras, notícias, próximos jogos e suas três tabelas de relacionamento. Não há comandos de exclusão de tabelas ou registros.

Crie um `.env` na raiz, sem substituir uma configuração existente:

```dotenv
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=preencha_localmente
DB_NAME=projeto_interdisciplinar
```

Execute `database/schema.sql` no MySQL e verifique a conexão:

```powershell
.\venv\Scripts\python.exe -m backend.models.banco
```

A senha não deve ser versionada. O script SQL cria estruturas ausentes; alterações de colunas existentes precisam de migração própria. Faça backup antes de migrar estruturas.

A página de jogos lê o MySQL e recebe partidas importadas da API-Football. Consulte [como configurar e sincronizar](database/API_FOOTBALL.md). Cadastro/login e vínculo das fotos aos usuários continuam pendentes.

A página de notícias consulta o RSS de Esportes da Agência Brasil e filtra apenas futebol feminino (clubes, seleções e categorias de base) por título e categorias. Links relacionados no corpo não participam da classificação. A lista de termos fica em `backend/noticias.py` e pode precisar de ajustes conforme a classificação editorial da fonte. Falhas de conexão exibem uma mensagem na página, sem notícias de demonstração.

## Verificação

```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -v
```

Os testes usam uma pasta temporária para imagens e simulam a conexão do diagnóstico, sem alterar o MySQL nem os uploads reais.

Veja o guia de edição do [frontend](frontend/README.md). O formulário de fotos fica em `/Telas/fotos.html`.

Integração de partidas: `backend/jogos.py`. O comando `python -m backend.jogos --help` mostra como localizar equipes, preparar o banco e sincronizar.
