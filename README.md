# Projeto Interdisciplinar — Futebol Feminino

Portal para reunir notícias, informações do elenco, próximos jogos e a história de uma equipe de futebol feminino. O projeto separa a interface do servidor e está organizado para evoluir conforme a arquitetura MVC (Model–View–Controller).

## Estrutura atual
ProjetoInterdisciplinar/
├── back_end/
│   ├── Servidor.py
│   ├── controllers/
│   │   └── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── banco.py
│   └── uploads/
│       └── .gitkeep
├── front_end/
│   ├── index.html
│   ├── Telas/
│   │   ├── noticias.html
│   │   ├── elenco.html
│   │   ├── proximos-jogos.html
│   │   └── historia.html
│   ├── css/
│   │   ├── style.css
│   │   └── upload.css
│   ├── js/
│   │   ├── main.js
│   │   └── upload.js
│   └── assets/
│       ├── favicon-vazio.svg
│       └── .gitkeep
├── database/
│   └── schema.sql
├── venv/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md


## Arquitetura MVC

MVC distribui as responsabilidades em três camadas:

|    Camada  |                                            Responsabilidade                                       |      Local no projeto   |
| ---------- | ------------------------------------------------------------------------------------------------- | ----------------------- |
|    Model   | Representar os dados, aplicar regras de negócio e, quando implementado, acessar o banco de dados. | `back_end/models/`      |
|    View    | Exibir informações e oferecer a interface com que o usuário interage.                             | `front_end/`            |
| Controller | Receber requisições, coordenar operações dos modelos e devolver respostas para a interface.       | `back_end/controllers/` |

### Estado atual da implementação

As Views estão implementadas como páginas HTML estáticas, com CSS e JavaScript compartilhados. As quatro seções apresentam espaços aguardando conteúdo. Há uma função de conexão com o MySQL em `back_end/models/banco.py`, configurada por um arquivo `.env` local. As rotas ainda não utilizam o banco; cadastro, login e busca dinâmica de notícias, atletas ou partidas ainda não estão implementados.

A pasta `models` contém a função de conexão com o MySQL; a pasta `controllers` ainda contém somente a identificação do pacote Python. Atualmente, a inicialização do Flask, as rotas e a lógica de upload continuam em `Servidor.py`. Portanto, a separação completa das responsabilidades do MVC será feita nas próximas etapas.

### Fluxo previsto para uma funcionalidade

Ao carregar notícias dinamicamente, a View fará uma requisição ao servidor. O Controller receberá o pedido e consultará o Model; o Model buscará os dados e os devolverá ao Controller, que responderá à View. A interface então exibirá as notícias.

```text
View → requisição → Controller → Model
View ← resposta  ← Controller ← dados
```

## Função dos diretórios e arquivos

### Back-end

- **`back_end/`**: reúne o código executado pelo servidor e o armazenamento dos arquivos enviados. Abriga as camadas Model e Controller.
- **`back_end/Servidor.py`**: inicia a aplicação Flask, disponibiliza as páginas e os recursos do front-end e recebe uploads pela API.
- **`back_end/controllers/`**: receberá os controladores das funcionalidades, como notícias, elenco e jogos. Esses controladores deverão tratar as requisições e coordenar as operações dos modelos.
- **`back_end/models/`**: receberá os modelos dos dados e as regras de negócio. Por exemplo, poderá definir os dados necessários para cadastrar uma notícia ou uma atleta.
- **`back_end/uploads/`**: armazena os arquivos recebidos pela API. É uma pasta de armazenamento, não uma camada adicional do MVC. Seu conteúdo é ignorado pelo Git, exceto o `.gitkeep`; atualmente não existe uma rota pública para visualizar os arquivos salvos.
- **`__init__.py`**: identifica `models` e `controllers` como pacotes Python, permitindo organizar os módulos que serão importados pelo servidor.

### Front-end

- **`front_end/`**: contém a camada View, com páginas, estilos, scripts e imagens fixas.
- **`front_end/index.html`**: é a página principal e o ponto de entrada da navegação para as quatro seções do portal.
- **`front_end/Telas/`**: reúne as páginas de Notícias, Elenco, Próximos Jogos e História. Todas oferecem links para as demais seções e para a página principal.
- **`front_end/css/`**: guarda os estilos. O arquivo `style.css` define o visual comum, o layout e as adaptações para telas menores.
- **`front_end/js/`**: guarda os scripts da interface. Atualmente, `main.js` controla o menu em telas menores e atualiza o ano do rodapé.
- **`front_end/assets/`**: guarda futuras imagens fixas do projeto, como logos, ícones e banners adicionados durante o desenvolvimento.

**Diferença entre `assets` e `uploads`:** `assets` contém recursos da interface mantidos com o código; `uploads` recebe arquivos enviados durante o uso do sistema.

### Arquivos e diretórios da raiz

- **`venv/`**: ambiente virtual local que separa as dependências Python deste projeto das de outros projetos. Não deve ser enviado ao Git.
- **`requirements.txt`**: lista as dependências Python e suas versões para instalação com o pip.
- **`.gitignore`**: determina quais arquivos o Git deve ignorar, incluindo o ambiente virtual, caches Python e os arquivos enviados para `uploads`.
- **`README.md`**: documenta o objetivo, a estrutura, a arquitetura e a execução do projeto.

## Ferramentas utilizadas

| Ferramenta   |                                      Uso no projeto                                            |
| ------------ | ---------------------------------------------------------------------------------------------- |
| HTML         | Estrutura e conteúdo das páginas.                                                              |
| CSS          | Estilo compartilhado e layout responsivo.                                                      |
| JavaScript   | Interações no navegador, como o menu e o ano do rodapé.                                        |
| Python       | Linguagem utilizada no servidor.                                                               |
| Flask        | Framework do servidor: rotas HTTP, entrega de arquivos e respostas JSON.                       |
| Flask-CORS   | Configuração de CORS para permitir requisições entre origens diferentes.                       |
| Werkzeug     | Utilitários utilizados pelo Flask; `secure_filename` normaliza os nomes dos arquivos enviados. |
| pip e venv   | Instalação e isolamento das dependências Python.                                               |
| Git e GitHub | Controle de versões e hospedagem do repositório.                                               |

O `requirements.txt` também inclui dependências de apoio do Flask: Blinker, Click, ItsDangerous, Jinja2 e MarkupSafe. Embora Jinja2 esteja instalado, as páginas atuais são entregues como HTML estático, sem renderização de templates pelo servidor.

## Executar localmente

Com Python instalado, abra um terminal na raiz do projeto. Se ainda não houver ambiente virtual, crie-o:

```powershell
python -m venv venv
```

Instale as dependências e inicie o servidor:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe back_end\Servidor.py
```

Acesse [http://localhost:5000](http://localhost:5000). O servidor atual inicia com modo de depuração habilitado para desenvolvimento local.

Também é possível abrir `front_end/index.html` diretamente no navegador para visualizar as telas estáticas. As funcionalidades da API exigem que o servidor esteja em execução.

## Preparar o banco MySQL

O arquivo `database/schema.sql` cria somente o banco `projeto_interdisciplinar` e a tabela `usuarios`, incluindo a referência da foto de perfil. Não contém registros, senhas de conexão nem comandos para copiar outros bancos. As imagens ficam em `back_end/uploads`; a coluna `foto_perfil` guarda o caminho de cada arquivo.

No PowerShell, conecte ao MySQL (ajuste o caminho se sua instalação for diferente):

```powershell
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p
```

Depois de informar a senha, execute **dentro do MySQL**, onde aparece `mysql>`:

```sql
SOURCE C:/Users/gcfer/Desktop/ProjetoInterdisciplinar/database/schema.sql;
SHOW TABLES;
DESCRIBE usuarios;
```

Quem clonar o projeto deve ajustar o caminho de `SOURCE` para a própria pasta. `SOURCE` lê e executa os comandos do arquivo SQL. `SHOW TABLES` lista as tabelas e `DESCRIBE` mostra suas colunas.

O script usa `IF NOT EXISTS`: não apaga dados e não recria tabelas existentes. Isso também significa que ele **não adiciona colunas em uma tabela já criada**. Se `usuarios` já existir, confira `DESCRIBE usuarios;`. Somente se a coluna `foto_perfil` estiver ausente, execute:

```sql
ALTER TABLE usuarios ADD COLUMN foto_perfil VARCHAR(500) NULL;
```

Para configurar o Python, copie `.env.example` para `.env` na raiz do projeto, caso ainda não tenha esse arquivo, e preencha a senha localmente. Instale as dependências conforme a seção de execução e teste no PowerShell, a partir da raiz do projeto:

```powershell
.\venv\Scripts\python.exe -m back_end.models.banco
```

O teste consulta o nome do banco e as colunas de `usuarios`, sem alterar dados. A conexão preparada ainda não implementa as rotas de cadastro ou login.

### Banco de dados e Git

Versione `database/schema.sql`, o código Python, as dependências e `.env.example`. O arquivo `.env` com a senha e as fotos enviadas são ignorados pelo Git. O Git não copia automaticamente os bancos locais nem seus registros.

Quando a estrutura mudar, mantenha `schema.sql` atualizado para instalações novas e adicione um arquivo numerado em `database/migrations/` com os comandos de alteração para bancos existentes. Por exemplo, uma alteração futura poderia ficar em `001_adicionar_cargo.sql`. Registre no arquivo o que ele modifica e execute cada migração uma única vez, na ordem. Evite incluir senhas ou dados pessoais nesses scripts.

## Rotas atuais

| Método e caminho   |                                                 Função                                           |
| ------------------ | ------------------------------------------------------------------------------------------------ |
| `GET /`            | Entrega a página principal `index.html`.                                                         |
| `GET /<caminho>`   | Entrega os arquivos existentes em `front_end`, incluindo telas, CSS, JavaScript e imagens fixas. |
| `POST /api/upload` | Recebe arquivos no campo `fotos` de um formulário multipart e os salva em `back_end/uploads`.    |

A página inicial possui um formulário ligado à API de upload. As fotos são armazenadas em `back_end/uploads`, sem publicação automática.

## Interface e IHC

A interface foi ajustada para facilitar a orientação e a realização das tarefas:

- Nome da seleção, navegação e rodapé consistentes nas cinco páginas.
- Página atual indicada por texto destacado e `aria-current`.
- Fundo azul preservado, com superfícies escuras e cartões claros para facilitar a leitura.
- Espaçamento do menu adaptável: até 92px nas telas largas e menu recolhível em telas de até 1100px.
- Links e botões com áreas de interação de pelo menos 44px, foco visível e atalho para pular ao conteúdo.
- Menu acessível pelo teclado, fechamento com Escape e navegação disponível mesmo sem JavaScript.
- Upload integrado ao conteúdo, com seleção de arquivos visível, indicação de envio, confirmação e mensagens de erro sem alertas bloqueantes.
- Em caso de erro no envio, a seleção permanece disponível para uma nova tentativa.

O espaço máximo do menu pode ser alterado em `--espaco-menu`, no início de `front_end/css/style.css`. Os ajustes seguem princípios de IHC, mas ainda precisam de avaliação com usuários; não representam uma certificação de acessibilidade.

## Convenções para continuar o desenvolvimento

- Mantenha o estilo comum em `front_end/css/style.css` e os comportamentos compartilhados em `front_end/js/main.js`.
- Na página principal, use caminhos como `assets/logo.png`; nas páginas de `Telas`, use `../assets/logo.png`.
- Coloque novos dados e regras de negócio em `models` e os responsáveis por receber requisições em `controllers`, conforme a separação MVC for implementada.
- Mantenha arquivos enviados por usuários em `back_end/uploads`, separados dos recursos fixos da interface.

## Interfaces presentes no repositorio

A aplicacao Flask serve a pasta `front_end/`, que contem o portal e as alteracoes locais. A pasta `front-end/` foi recebida da equipe durante a integracao dos historicos e foi preservada com seus arquivos originais. Ela contem outra versao da interface e ainda nao e servida pelo Flask. A unificacao das duas interfaces deve ser combinada com a equipe.

## 📌 Próximos Passos



- [ ] Implementar o banco de dados para persistência das informações.

- [ ] Mover as rotas de `Servidor.py` para a pasta `controllers/`.

- [ ] Criar os modelos em `models/` para notícias, elenco e partidas.

- [ ] Integrar a View com a API para exibição dinâmica dos dados.
