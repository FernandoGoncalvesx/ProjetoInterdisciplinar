# Portal da Seleção Feminina Brasileira

Portal em Flask organizado em MVC, com autenticação, notícias, elenco, agenda, história e editor de cards. As páginas herdam `base.html`, com menu e rodapé compartilhados em componentes. Jinja2 exibe os dados dos jogos. CSS e JavaScript são compartilhados; não há etapa de build nem dependência de Bootstrap.

## Preparação e execução

Na raiz do projeto, no PowerShell, crie o ambiente somente se ainda não existir:

```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\waitress-serve.exe --host=127.0.0.1 --port=8081 backend.app:app
```

Abra http://127.0.0.1:8081. Não abra os HTMLs diretamente: agora eles são templates renderizados pelo Flask. As URLs existentes, incluindo `/index.html` e `/Telas/historia.html`, continuam disponíveis.

O `requirements.txt` reúne as dependências do portal, da coleta de notícias e do
editor de cards, incluindo Pillow e rembg com processamento em CPU. O ambiente
local usa Python 3.14.7. O navegador da coleta é instalado separadamente com
`.\venv\Scripts\python.exe -m playwright install chromium`. O modelo de remoção
de fundo é baixado no primeiro recorte e reutilizado em `backend/cache_modelos/`.

Para desenvolvimento local também é possível usar:

```powershell
.\venv\Scripts\python.exe -m backend.app
```

Nesse caso, abra http://127.0.0.1:5000. O modo de depuração fica desativado. Apache e túnel são opcionais; consulte [INICIAR_SERVIDOR.md](INICIAR_SERVIDOR.md).

## Estrutura

| Caminho | Responsabilidade |
| --- | --- |
| `backend/app.py` | Configuração do Flask, registro de controllers e arquivos públicos |
| `backend/controllers/` | Rotas por funcionalidade, validação HTTP e respostas HTML/JSON |
| `backend/models/` | Dados e consultas ao banco, sem dependência de Flask |
| `backend/services/` | Coleta Playwright, uploads e processamento de imagens |
| `backend/models/banco.py` | Conexão compartilhada e diagnóstico do MySQL |
| `backend/uploads/` | Arquivos recebidos, ignorados pelo Git |
| `frontend/templates/paginas/` | Conteúdo específico das páginas |
| `frontend/css/` | Estilos compartilhados em `base.css` e identidade visual em `tema.css` |
| `frontend/js/` | Menu, rodapé e interação específica de cada página |
| `frontend/assets/` | Logo e ícone do portal |
| `database/schema.sql` | Criação das sete tabelas, sem registros |
| `tests/test_sistema.py` | Verificação de páginas, links, upload e diagnóstico |

O mapa de arquivos e as regras de cada camada estão em [ARQUITETURA.md](ARQUITETURA.md).

## O que está funcionando

- Navegação entre início, notícias, elenco, próximos jogos, história e envio de fotos.
- Menu acessível e responsivo, com botão identificado no celular e ano atualizado.
- Notícias consultadas no MySQL, com coleta da CBF e leitura em modal.
- Login, cadastro, logout e alteração de usuário com sessão e proteção CSRF.
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

A página de jogos lê as partidas cadastradas no MySQL. Para acrescentar campos da agenda a um banco antigo, execute `python -m backend.jogos preparar-banco`. Login e cadastro estão implementados; o upload legado não vincula fotos a usuários.

## Atualização das notícias

As notícias são lidas do MySQL em `/Telas/noticias.html` e `/api/noticias`.
O coletor da CBF usa a estrutura atual e salva imagens em `frontend/assets/noticias/`.
Com o banco configurado, execute na raiz:

```powershell
.\venv\Scripts\python.exe -m playwright install chromium
.\venv\Scripts\python.exe -m backend.services.coleta_noticias
```

Instale antes as dependências de `requirements.txt`. Ao abrir a página, o JavaScript mostra as notícias salvas. O botão Atualizar notícias chama `/api/crawler`
e consulta a lista novamente após a coleta. O comando acima também permite coleta manual.
A apresentação usa os templates compartilhados, com leitura em diálogo e alternativa
sem JavaScript. Os antigos `back_end/Servidor.py` e `front_end/js/script.js` foram
substituídos pela aplicação `backend.app` e pelos scripts em `frontend/js/`.

## Testes

```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -v
node --test tests/enquadramento.test.mjs
```

Os testes usam uma pasta temporária para imagens e simulam a conexão do diagnóstico, sem alterar o MySQL nem os uploads reais.
Os testes de enquadramento usam o executor nativo do Node.js, sem pacotes npm.

Veja o guia de edição do [frontend](frontend/README.md). O formulário de fotos fica em `/Telas/fotos.html`.
