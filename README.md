# Projeto Interdisciplinar — Futebol Feminino

Portal da Seleção Feminina Brasileira com páginas de notícias, elenco, próximos jogos e história. Desenvolvido com HTML, CSS, JavaScript e Python/Flask, com estrutura inicial para MySQL.

## Funcionalidades e tecnologias

O sistema possui cinco páginas HTML, menu responsivo com suporte a teclado, identificação da página atual, logo no cabeçalho e formulário para enviar várias imagens. Notícias, elenco, jogos e história ainda apresentam conteúdo estático ou espaços aguardando dados. Cadastro, login, sessões e foto de perfil vinculada ao usuário ainda não foram implementados.

| Tecnologia | Uso |
| --- | --- |
| HTML, CSS e JavaScript | Conteúdo, aparência e interações das páginas. |
| Python e Flask | Entrega das páginas e recebimento de uploads. |
| Flask-CORS e Werkzeug | CORS e normalização dos nomes dos arquivos enviados. |
| MySQL Connector/Python e python-dotenv | Conexão com o MySQL e leitura da configuração local. |
| MySQL | Estrutura inicial de usuários, ainda não integrada às rotas. |
| Waitress | Execução do Flask sem o servidor de depuração. |
| Apache do XAMPP | Proxy reverso para encaminhar acessos ao Waitress. |
| Cloudflare Tunnel | Link HTTPS temporário para demonstração externa. |

As páginas são entregues como arquivos estáticos; não há framework JavaScript, compilação de frontend ou uso de templates Jinja nas rotas atuais.

## Estrutura atual do projeto

```text
ProjetoInterdisciplinar/
├── back_end/
│   ├── Servidor.py
│   ├── controllers/
│   ├── models/
│   │   └── banco.py
│   └── uploads/
│       └── .gitkeep
├── front_end/
│   ├── index.html
│   ├── Telas/
│   │   ├── elenco.html
│   │   ├── historia.html
│   │   ├── noticias.html
│   │   └── proximos_jogos.html
│   ├── css/
│   │   ├── index.css
│   │   ├── elenco.css
│   │   ├── historia.css
│   │   ├── noticias.css
│   │   └── proximos_jogos.css
│   ├── js/
│   │   ├── index.js
│   │   ├── elenco.js
│   │   ├── historia.js
│   │   ├── noticias.js
│   │   └── proximos_jogos.js
│   └── assets/
│       ├── logo.webp
│       ├── favicon.ico
│       └── favicon.png
├── database/
│   ├── README.md
│   └── schema.sql
├── venv/                   # Ambiente local, ignorado pelo Git
├── .env                    # Configuração local, ignorada pelo Git
├── .env.example
├── .gitignore
├── INICIAR_SERVIDOR.md
├── requirements.txt
└── README.md
```

A árvore omite os arquivos internos do ambiente virtual, os caches gerados pelo Python e os uploads dos usuários.

| Caminho | Responsabilidade |
| --- | --- |
| `front_end/index.html` | Página inicial com navegação e upload. |
| `front_end/Telas/` | Páginas internas do portal. |
| `front_end/css/` e `front_end/js/` | Um CSS e um JavaScript por HTML, com o mesmo nome da página. |
| `front_end/assets/` | Logo WebP e favicons. |
| `back_end/Servidor.py` | Aplicação Flask, entrega das páginas e API de upload. |
| `back_end/models/banco.py` | Conexão e verificação do MySQL. |
| `back_end/controllers/` | Pasta reservada para os controladores. |
| `back_end/uploads/` | Arquivos enviados pelo site, ignorados pelo Git. |
| `database/schema.sql` | Estrutura inicial do banco, sem registros. |
| `.env.example` | Modelo de configuração local do MySQL. |
| `requirements.txt` | Dependências Python. |
| [INICIAR_SERVIDOR.md](INICIAR_SERVIDOR.md) | Comandos para iniciar Apache, Waitress e túnel. |

Cada página carrega somente seu CSS e JavaScript. A base comum é repetida nos cinco arquivos; alterações gerais devem ser aplicadas a todos. `index.js` também controla o upload. Não há arquivos globais nem subpastas `pages/`.

A separação MVC ainda está em andamento:

| Camada | Situação atual |
| --- | --- |
| View | HTML, CSS e JavaScript em `front_end/`. |
| Model | `models/banco.py` abre a conexão e verifica o banco; os modelos de negócio ainda não existem. |
| Controller | `controllers/` está reservada; as rotas e o upload permanecem em `Servidor.py`. |

O upload atual segue `formulário → POST /api/upload → Flask → pasta uploads`. O fluxo com banco de dados ainda será implementado. A pasta vazia `controllers/` não é mantida automaticamente ao clonar o repositório.

## Requisitos

- Python com pip e suporte a ambientes virtuais.
- Windows e PowerShell para os comandos deste documento.
- Apache pelo XAMPP e portas locais 8081 e 8082 disponíveis, para o modo com proxy.
- `cloudflared` e internet, somente para acesso externo.
- MySQL Server, somente para preparar ou testar o banco. O Workbench é opcional.

Os caminhos de exemplo correspondem ao computador de desenvolvimento. Quem clonar o projeto deve ajustar a pasta do projeto e os caminhos do XAMPP e do MySQL. O ambiente virtual, as configurações do Apache e os dados locais não vêm prontos do Git.

## Preparar o ambiente

No PowerShell, dentro da pasta do projeto:

```powershell
cd "C:\Users\gcfer\Desktop\ProjetoInterdisciplinar"
```

Crie o ambiente e instale as dependências:

```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

Crie o ambiente virtual somente se ele não existir. O Waitress está incluído em `requirements.txt`. Não é necessário ativar o ambiente para usar esses comandos. Apache, MySQL Server e `cloudflared` são programas instalados separadamente, não pacotes Python desse arquivo.

Para acesso externo, instale o Apache pelo XAMPP e o cliente do túnel:

```powershell
winget install --id Cloudflare.cloudflared --exact
```

Abra um novo PowerShell após instalar o `cloudflared`.

```powershell
cloudflared --version
```

Para desenvolvimento apenas no computador, sem Apache ou túnel, execute:

```powershell
.\venv\Scripts\python.exe back_end\Servidor.py
```

Acesse [http://127.0.0.1:5000](http://127.0.0.1:5000). Esse modo usa depuração e não deve ser o destino do túnel público. Para o fluxo abaixo, use Waitress em vez desse comando. Abrir o HTML diretamente não inicia a API; prefira acessar o projeto por HTTP.

## Ligar o servidor

```text
Visitante → túnel HTTPS → Apache:8082 → Waitress:8081 → Flask
```

1. Inicie o **Apache** no XAMPP. A configuração inicial está abaixo.
2. Na raiz do projeto, execute e mantenha o terminal aberto:

   ```powershell
   .\venv\Scripts\waitress-serve.exe --host=127.0.0.1 --port=8081 back_end.Servidor:app
   ```

3. Confira o site em [http://127.0.0.1:8082](http://127.0.0.1:8082).
4. Em outro PowerShell, inicie o túnel:

   ```powershell
   cloudflared tunnel --protocol http2 --url http://127.0.0.1:8082
   ```

Compartilhe o link `.trycloudflare.com` exibido no terminal. O endereço é temporário e muda quando o túnel é recriado. Esse modo é destinado a testes, sem garantia de disponibilidade; não utiliza FreeDNS nem exige encaminhamento de portas no roteador.

A porta **8081** acessa diretamente o Waitress; a **8082** passa pelo Apache. Ambas aceitam conexões apenas do próprio computador. Visitantes externos usam o link do túnel.

Mantenha o computador ligado, sem suspensão, e os três componentes ativos. Para encerrar, use **Ctrl + C** nos terminais do túnel e do Waitress. Pare o Apache pelo XAMPP somente se nenhum outro projeto estiver usando-o. Os comandos também estão em [INICIAR_SERVIDOR.md](INICIAR_SERVIDOR.md).

Não inicie outra instância na mesma porta. Alterações em HTML, CSS e JavaScript aparecem após atualizar o navegador; use **Ctrl + F5** se houver cache. Ao alterar Python, pare e reinicie o Waitress, pois esse modo não recarrega o código automaticamente.

## Configurar o Apache uma vez

A configuração fica fora do Git. Em instalações XAMPP, faça uma cópia de segurança de `C:\xampp\apache\conf\extra\httpd-vhosts.conf` e adicione este bloco uma única vez:

```apache
Listen 127.0.0.1:8082

<VirtualHost 127.0.0.1:8082>
    ServerName localhost
    ProxyRequests Off
    ProxyPass "/" "http://127.0.0.1:8081/"
    ProxyPassReverse "/" "http://127.0.0.1:8081/"

    <LocationMatch "(?i)^/(phpmyadmin|dashboard|xampp|server-status|server-info)(/|$)">
        Require all denied
    </LocationMatch>
</VirtualHost>
```

No `httpd.conf`, mantenha habilitados `proxy_module`, `proxy_http_module` e `Include conf/extra/httpd-vhosts.conf`, sem duplicar linhas. A porta 8080 já é usada por outro sistema no computador de desenvolvimento; preserve essa configuração.

Valide antes de iniciar ou reiniciar o Apache:

```powershell
& "C:\xampp\apache\bin\httpd.exe" -t
```

O resultado esperado é `Syntax OK`. Se houver erro de listeners duplicados, confira as declarações `Listen`. Se a porta 8082 retornar 503, verifique se o Waitress está ativo na 8081. Ajuste os caminhos caso o XAMPP esteja instalado em outro local.

## Páginas e organização do frontend

| HTML | CSS | JavaScript |
| --- | --- | --- |
| `index.html` | `css/index.css` | `js/index.js` |
| `Telas/elenco.html` | `css/elenco.css` | `js/elenco.js` |
| `Telas/historia.html` | `css/historia.css` | `js/historia.js` |
| `Telas/noticias.html` | `css/noticias.css` | `js/noticias.js` |
| `Telas/proximos_jogos.html` | `css/proximos_jogos.css` | `js/proximos_jogos.js` |

Os caminhos da tabela são relativos a `front_end/`. Nos HTMLs de `Telas/`, use `../css/`, `../js/` e `../assets/`. A logo exibida no cabeçalho é `assets/logo.webp`; os ícones da aba são `favicon.ico` e `favicon.png`.

O menu recolhe em telas de até 1100px. A variável `--espaco-menu`, em cada CSS, controla o espaçamento máximo dos links. Os scripts de cada página controlam o menu e o ano do rodapé; `index.js` também controla seleção, envio e mensagens do upload.

**Pendência encontrada:** os arquivos de próximos jogos usam `_`, mas ainda há links HTML apontando para `proximos-jogos.html` e referências a `proximos-jogos.css` e `proximos-jogos.js`, com hífen. Isso pode causar 404 e deixar essa página sem estilos ou scripts. É necessário alinhar todas as referências aos nomes reais da tabela acima. Esta documentação não modifica essas referências no código.

## API e armazenamento de arquivos

| Método | Caminho | Comportamento |
| --- | --- | --- |
| GET | `/` | Entrega `front_end/index.html`. |
| GET | `/<caminho>` | Entrega arquivos existentes dentro de `front_end/`; retorna 404 quando ausentes. |
| POST | `/api/upload` | Recebe arquivos pelo campo `fotos` e salva em `back_end/uploads/`. |

O Flask também registra a rota estática `/front_end/<caminho>`. Os HTMLs usam os caminhos relativos atendidos pelas rotas principais.

O envio usa `multipart/form-data`, com o mesmo campo `fotos` repetido para vários arquivos. A resposta de sucesso tem status 200 e o formato:

```json
{
  "mensagem": "Fotos enviadas com sucesso!",
  "arquivos": ["foto.webp"]
}
```

Sem o campo `fotos`, a API responde 400 com `{"mensagem": "Nenhuma foto enviada."}`. Seleções com nomes vazios são ignoradas; a API ainda pode retornar sucesso com a lista `arquivos` vazia. Erros de gravação não possuem tratamento específico.

O navegador filtra tipos declarados como imagem, apresenta os nomes e preserva a seleção quando o envio falha. No servidor, `secure_filename` normaliza o nome, e o arquivo é gravado no disco. Isso não valida o conteúdo da imagem nem garante um nome único. A pasta é criada automaticamente se não existir.

Atualmente, os arquivos não são gravados no MySQL, não são vinculados a usuários e não possuem rota para visualização. Os arquivos só ficam no computador que recebeu o upload; o túnel não os armazena.

## Banco de dados

A estrutura completa e as instruções de criação estão em [database/README.md](database/README.md). Execute somente `database/schema.sql` para criar o banco e as sete tabelas: `usuarios`, `jogadoras`, `noticias`, `proximos_jogos` e as três tabelas de relacionamento. O mesmo script pode ser usado em uma instalação nova ou para criar tabelas ausentes em um banco existente.

O banco `projeto_interdisciplinar` possui a estrutura de `usuarios`: `id`, `nome`, `email`, `senha_hash`, `foto_perfil` e `criado_em`. A coluna `foto_perfil` foi prevista para um caminho de arquivo; a imagem ainda não é armazenada no MySQL.

| Campo | Tipo | Finalidade |
| --- | --- | --- |
| `id` | `INT UNSIGNED` | Chave primária com incremento automático. |
| `nome` | `VARCHAR(100)` | Nome obrigatório. |
| `email` | `VARCHAR(254)` | E-mail obrigatório e único. |
| `senha_hash` | `VARCHAR(255)` | Campo destinado à senha protegida; não deve receber a senha original. |
| `foto_perfil` | `VARCHAR(500)` | Caminho opcional da foto; o upload ainda não preenche esse campo. |
| `criado_em` | `TIMESTAMP` | Data e hora preenchidas automaticamente. |

Conecte ao MySQL pelo PowerShell, ajustando o caminho da instalação se necessário:

```powershell
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p
```

Dentro do MySQL, execute o arquivo SQL e confira a tabela. Ajuste o caminho para a sua cópia do projeto:

```sql
SOURCE C:/Users/gcfer/Desktop/ProjetoInterdisciplinar/database/schema.sql;
DESCRIBE usuarios;
```

O script cria estruturas ausentes e preserva os registros, mas não atualiza colunas de tabelas existentes. Alterações nessas colunas exigem comandos `ALTER TABLE`.

Se uma tabela antiga não tiver `foto_perfil`, confirme com `DESCRIBE usuarios;` e, somente nessa situação, execute:

```sql
ALTER TABLE usuarios ADD COLUMN foto_perfil VARCHAR(500) NULL;
```

Copie `.env.example` para `.env`, caso ainda não exista, e preencha os dados de conexão localmente:

| Variável | Finalidade | Padrão do projeto |
| --- | --- | --- |
| `DB_HOST` | Endereço do MySQL | `127.0.0.1` |
| `DB_PORT` | Porta do MySQL | `3306` |
| `DB_USER` | Usuário de conexão | `root` no exemplo local |
| `DB_PASSWORD` | Senha desse usuário | Preencher localmente; não versionar. |
| `DB_NAME` | Nome do banco | `projeto_interdisciplinar` |

Não sobrescreva um `.env` já configurado. Para testar a conexão, com o MySQL em execução:

```powershell
.\venv\Scripts\python.exe -m back_end.models.banco
```

As rotas atuais ainda não consultam o banco; o MySQL não é necessário para abrir as páginas ou receber os uploads existentes.

O teste mostra o nome do banco e as colunas, sem alterar os dados. `root` é a conta usada no exemplo local, não um funcionário cadastrado. Para uma implantação definitiva, use uma conta própria da aplicação com as permissões necessárias.

## Verificação e diagnóstico

Depois de preparar o ambiente:

1. Abra a página inicial e as quatro páginas internas, conferindo estilos, logo e navegação. Considere a pendência de nomes em próximos jogos descrita acima.
2. Em tela estreita, abra o menu, navegue por teclado e confira o fechamento com Escape.
3. Envie uma imagem de teste e confira o arquivo em `back_end/uploads/`. A mensagem de sucesso ainda não representa um cadastro no banco.
4. Abra o link do túnel em um celular com Wi-Fi desligado para confirmar o acesso externo.
5. Execute a verificação do banco separadamente, se for utilizá-lo.

Não há suíte de testes automatizados versionada neste repositório. Esses passos são verificações manuais.

| Problema | Onde conferir |
| --- | --- |
| Porta 8081 não abre | Waitress ativo, dependências instaladas e terminal na raiz do projeto. |
| 8081 abre e 8082 não | Apache ativo e configuração validada com `httpd.exe -t`. |
| Apache retorna 503 | Waitress disponível em `127.0.0.1:8081`. |
| Porta em uso ou listeners duplicados | Instâncias já ativas e declarações `Listen` nos arquivos incluídos. |
| Link público indisponível | Túnel ativo, novo link correto, internet e acesso local pela 8082. |
| `cloudflared` não reconhecido | Reabrir o PowerShell após a instalação e conferir `cloudflared --version`. |
| Próximos jogos sem estilo ou com 404 | Referências com hífen versus arquivos com sublinhado. |
| Acesso negado ao MySQL | `DB_USER` e `DB_PASSWORD` no `.env`. |
| Banco ou tabela inexistente | `DB_NAME` e execução de `database/schema.sql`. |

## Git, manutenção e cópias de segurança

Versione código, assets, documentação, `requirements.txt`, `.env.example` e scripts SQL. Não inclua `.env`, ambiente virtual, caches, senhas ou dados pessoais. Os uploads são ignorados, exceto o `.gitkeep` que preserva a pasta.

Clonar o repositório não copia os registros do MySQL, uploads ou configurações do Apache. Faça backup do banco e da pasta `back_end/uploads/` separadamente. O `.env` deve ser guardado de forma privada.

Ao criar uma página, use o mesmo nome no HTML, CSS e JavaScript e atualize os links. Mantenha a grafia consistente, inclusive maiúsculas, hífens e sublinhados. Ajustes de estilo ou navegação comuns devem ser repetidos nos cinco arquivos, conforme a organização atual.

## Estado atual e cuidados

- Páginas, menu responsivo e upload estão implementados. As seções ainda aguardam conteúdo dinâmico.
- Cadastro, login, sessões e vínculo da foto de perfil ao usuário ainda não estão implementados.
- `POST /api/upload` recebe o campo `fotos` e salva os arquivos em `back_end/uploads/`, sem registro no banco nem rota de exibição.
- Antes do uso público contínuo, o upload precisa de autenticação, validação do conteúdo no servidor, limite de tamanho e nomes únicos para evitar sobrescrita.
- `.env`, `venv/` e uploads não devem ir para o Git. O repositório contém a estrutura SQL, não os registros reais do MySQL.

As próximas etapas são corrigir as referências de próximos jogos, integrar cadastro e autenticação ao banco, implementar a foto de perfil e distribuir as regras entre modelos e controladores. O armazenamento de imagens dentro do MySQL foi discutido, mas não está implementado.

Referências de infraestrutura: [Waitress com Flask](https://flask.palletsprojects.com/en/stable/deploying/waitress/), [proxy reverso do Apache](https://httpd.apache.org/docs/2.4/howto/reverse_proxy.html) e [Cloudflare Quick Tunnels](https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/).
