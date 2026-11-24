# Organização MVC do portal

O projeto mantém Flask, Jinja2, MySQL e JavaScript. As URLs existentes são preservadas.

## Responsabilidades

- `backend/app.py`: configura Flask, registra Blueprints, disponibiliza a navegação
  aos templates e serve apenas os recursos públicos (`css`, `js`, `assets`).
- `backend/controllers/`: recebe requisições, valida entradas HTTP, mantém a sessão
  e retorna páginas ou JSON. Cada funcionalidade possui um Blueprint.
- `backend/models/`: consultas e persistência de usuários, notícias, jogadoras e
  jogos; leitura da história; dados e limites de fotos e cards. Não importa Flask.
- `backend/services/`: coleta Playwright, armazenamento de uploads, validação de
  imagens e recorte. Não renderiza templates nem gera respostas HTTP.
- `frontend/templates/`: Views Jinja2; `base.html` reúne menu, rodapé e recursos,
  `componentes/` contém trechos reutilizáveis e `paginas/` contém cada tela.
- `frontend/js/`, `css/`, `assets/`: interação, estilos e recursos visuais.
- `database/`: schema e migrações; `tests/`: testes das rotas, models e serviços.

## Onde editar

| Funcionalidade | Controller | Model / serviço | View |
| --- | --- | --- | --- |
| Início | `inicio_controller.py` | `models/jogo.py` | `inicio.html` |
| Conta | `autenticacao_controller.py` | `models/usuario.py` | `login_page.html` |
| Notícias | `noticias_controller.py` | `models/noticia.py`, `services/coleta_noticias.py` | `noticias.html` |
| Elenco | `elenco_controller.py` | `models/jogadora.py` | `elenco.html` |
| Jogos | `jogos_controller.py` | `models/jogo.py` | `proximos_jogos.html` |
| História | `historia_controller.py` | `models/historia.py` | `historia.html` |
| Fotos e cards | `fotos_controller.py`, `cards_controller.py` | models e serviços de imagens | `fotos.html`, `editor_card.html` |

Os controllers estão em `backend/controllers/`, e as Views em
`frontend/templates/paginas/`. O contexto da agenda usado por Início e Jogos
é compartilhado por `contexto_jogos`, no controller de jogos.

Exemplo: `/Telas/noticias.html` → controller de notícias → model de notícia →
MySQL → template Jinja2. O JavaScript da página mantém os cards, o modal e a
atualização via `/api/crawler`. O coletor usa o model para salvar os dados.

## Convenções

- SQL de funcionalidades web fica nos models; controllers tratam erros e status HTTP.
- Templates exibem os dados recebidos e continuam escapando textos automaticamente.
- Sessão, mensagens e proteção CSRF continuam no controller de autenticação.
- Uma mudança no caminho físico de um arquivo não exige mudar sua URL pública.
- Não é necessário criar classes ou serviços que apenas repassem chamadas.
- `backend/contas.py` é a ferramenta administrativa local existente, separada das
  requisições web. `backend/jogos.py` preserva o comando de preparação do banco,
  delegando a migração a `database/migracoes/jogos.py`.
- O comando antigo `python -m backend.models.busca_noticias` permanece compatível;
  a implementação e o comando recomendado estão em `backend.services.coleta_noticias`.

## Execução e testes

```powershell
.\venv\Scripts\python.exe -m backend.app
.\venv\Scripts\python.exe -m unittest discover -s tests -v
```

A reorganização não executa migrações nem altera registros no banco.
Os testes simulam o MySQL, a coleta e o recorte; não comprovam a operação desses
serviços externos no ambiente real.

# Fotos e cards

## Implementado

A página /Telas/fotos.html (também acessível por /cards) permite escolher uma foto,
processá-la e escolher um dos seis modelos: azul, branco, dourado, preto, roxo e verde.
O PNG exportado tem 740 × 1240 pixels e usa a arte original, inclusive seu fundo.
Nome e posição são editáveis. O botão Girar atributos sorteia TEC, VIS, PAS, DRI,
FIN, DEF e FIS entre 1 e 99; a nota geral é a média arredondada. Os valores permanecem
ao trocar o modelo ou ajustar a foto. Os PNGs originais não são alterados: o canvas
sobrepõe painéis com os dados editáveis aos textos fixos da arte.
A rota /assets/cards/modelos/<id>.png permite somente os seis modelos cadastrados.

| Camada | Arquivos | Responsabilidade |
| --- | --- | --- |
| Inicialização | backend/app.py | Configurar Flask e registrar blueprints. |
| Controllers | backend/controllers/fotos_controller.py, cards_controller.py | API e renderização do editor. |
| Models | backend/models/foto.py, card.py | Dados, limites, erros e configuração do card; sem tabelas novas. |
| Serviços | backend/services/validacao_imagem.py | Decodificação, orientação EXIF, limites e avisos de qualidade. |
| Serviços | backend/services/recorte_pessoa.py | Segmentação local com rembg e u2net_human_seg. |
| Views | frontend/templates/paginas/editor_card.html, fotos.html | Formulário e controles. |
| Componente | frontend/templates/componentes/previa-card.html | Canvas da prévia. |
| Interação | frontend/js/fotos.js, editor-card.js | Upload, ajustes por arrasto/controles e exportação PNG. |
| Estilo | frontend/css/editor-card.css | Layout responsivo. |

## Instalação e execução

Use Python 3.11 a 3.13 para as dependências de segmentação. O ambiente encontrado
neste projeto usa Python 3.14; crie outro ambiente sem substituir o atual.
Com Python 3.13 e o launcher instalados, execute na raiz:

~~~powershell
py -3.13 -m venv .venv-cards
.\.venv-cards\Scripts\python.exe -m pip install -r requirements-imagens.txt
.\.venv-cards\Scripts\python.exe -m waitress --host=127.0.0.1 --port=8081 backend.app:app
~~~

Abra http://127.0.0.1:8081/Telas/fotos.html.
O primeiro recorte baixa o modelo para backend/cache_modelos/ (ignorado pelo Git).
É necessário acesso à internet para instalar dependências e baixar o modelo;
as fotos são processadas localmente. A sessão é reutilizada após carregar o modelo.
A instalação automática nesta sessão falhou por resolução de DNS do PyPI,
portanto o processamento real ainda precisa ser validado no ambiente preparado.

## Contrato da API

POST /api/cards/processar recebe multipart com exatamente um campo de arquivo foto.
Aceita PNG, JPEG e WebP estáticos, até 5 MB, até 20 megapixels e no mínimo
300 pixels em cada dimensão. Corrige orientação EXIF e reduz para até 1600 × 1600.

- 200: recorte (data URL PNG) e avisos (lista de textos).
- 400: arquivo ou quantidade inválida, ou recorte vazio.
- 413: requisição acima do limite.
- 503: dependência/modelo indisponível ou processamento ocupado.
- 500: falha inesperada, sem expor detalhes internos ao cliente.

A resposta de sucesso usa Cache-Control: no-store. Originais e recortes não são
gravados no disco nem no banco pelo novo endpoint. A imagem fica na memória da
página; recarregar a página perde o trabalho. O download é feito pelo navegador.

## Limites do protótipo

A iluminação e nitidez são heurísticas globais iniciais, não notas de qualidade
calibradas. Seus problemas geram avisos; fotos corrompidas ou pequenas são bloqueadas.
Não há identificação facial, contagem automática de pessoas ou detecção da cintura.
O usuário precisa enviar uma pessoa e ajustar manualmente o enquadramento.
A segmentação pode errar cabelos, roupas e contornos: a prévia permite conferir,
mas ainda não há borracha de correção.

Um processamento por vez por processo é aceito. Publicação para muitos usuários
exigirá limites de uso e fila. Os espaços de bandeira e escudo das artes permanecem decorativos. Os atributos são
sorteados localmente para personalização, sem persistência nem valor competitivo.

## Compatibilidade

O endpoint legado /api/upload fica em fotos_controller.py, com gravação em
services/armazenamento_fotos.py para compatibilidade, mas a página
agora usa apenas /api/cards/processar. O JavaScript antigo de upload foi removido de
portal.js. Autenticação, conteúdo e jogos seguem a organização MVC descrita acima.

## Verificação

~~~powershell
.\.venv-cards\Scripts\python.exe -m unittest discover -s tests -v
~~~

tests/test_cards.py cobre contrato HTTP, erros, validação de imagens e segmentação
com modelo simulado. Casos de Pillow são pulados quando a biblioteca não está instalada.
Esses testes não comprovam a qualidade visual do modelo real.

