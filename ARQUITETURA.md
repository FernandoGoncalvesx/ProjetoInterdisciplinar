# MVC — fotos e cards

## Implementado

A página /Telas/fotos.html (também acessível por /cards) permite escolher uma foto,
processá-la e ajustar a pessoa num modelo azul editável. O PNG exportado tem
750 × 1050 pixels, com transparência fora da carta. Nome e posição são editáveis.
O modelo inicial é desenhado em canvas; os PNGs de referência não foram alterados.

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
exigirá limites de uso e fila. O modelo inicial não inclui bandeiras ou atributos.

## Compatibilidade

O endpoint legado /api/upload permanece em app.py para compatibilidade, mas a página
agora usa apenas /api/cards/processar. O JavaScript antigo de upload foi removido de
portal.js. Autenticação, conteúdo e jogos continuam com sua organização anterior.
A migração MVC do portal inteiro não faz parte deste módulo.

## Verificação

~~~powershell
.\.venv-cards\Scripts\python.exe -m unittest discover -s tests -v
~~~

tests/test_cards.py cobre contrato HTTP, erros, validação de imagens e segmentação
com modelo simulado. Casos de Pillow são pulados quando a biblioteca não está instalada.
Esses testes não comprovam a qualidade visual do modelo real.

