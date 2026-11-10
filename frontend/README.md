# Frontend: onde editar

```text
frontend/
├── assets/                     # Logo e ícone
├── css/
│   ├── base.css                # Estilos compartilhados
│   └── tema.css                # Identidade visual
├── js/
│   └── portal.js               # Menu, notícias, fotos e rodapé
└── templates/
    ├── base.html               # Estrutura comum e topo das páginas
    ├── componentes/            # Menu, rodapé e componentes de notícias
    └── paginas/                # Conteúdo específico das seis páginas
```

## Alterar uma página

Edite o HTML correspondente em `templates/paginas/`. Cada página herda `base.html`, define sua descrição e preenche o bloco `conteudo`:

```html
{% extends "base.html" %}
{% set descricao = "Descrição da página." %}
{% block conteudo %}
<section class="secao container">
    <h2>Conteúdo da página</h2>
</section>
{% endblock %}
```

## Alterar elementos compartilhados

- Estrutura HTML, CSS e scripts carregados: `templates/base.html`.
- Cabeçalho e aparência do menu: `templates/componentes/menu.html`.
- Links, títulos e URLs das páginas: `PAGINAS` em `back_end/app.py`.
- Rodapé: `templates/componentes/rodape.html`.
- Aparência: `css/base.css` e `css/tema.css`.
- Menu móvel e upload: `js/portal.js`.

CSS e JavaScript permanecem em arquivos compartilhados. Separe arquivos específicos quando uma funcionalidade crescer o suficiente para justificar isso.

## Abrir o site

Na raiz do projeto:

```powershell
.\venv\Scripts\python.exe -m back_end.app
```

Abra http://127.0.0.1:5000. Os HTMLs precisam ser renderizados pelo Flask. As URLs existentes continuam funcionando. Os templates não são publicados como arquivos.

Notícias de futebol feminino vêm do RSS da Agência Brasil e podem ser lidas na própria página. Jogos vêm do MySQL. Fotos enviadas ficam em `back_end/uploads/`.

## Melhorias incorporadas

A interface inclui menu móvel compacto, notícias com datas e consulta em segundo plano, histórico expansível e envio de fotos com prévias e seleção acumulada.

Acesse http://127.0.0.1:8081/. A interface consulta `/api/noticias`, que usa o cache em `back_end/cache/noticias-teste.json`.

O rodapé principal tem Ajuda, Suporte, Privacidade e Versão 1.0.0. Os botões abrem informações em janelas acessíveis, fechadas pelo botão ou pela tecla Escape. Suporte apresenta orientações de solução de problemas; não há canal de contato configurado.

O elenco tem atualização manual, com data e fontes da CBF informadas na página.

## Papel da inicial e de Notícias

A inicial apresenta somente a primeira matéria disponível no feed, em formato de destaque curto, ao lado do próximo jogo da base. O link “Ler destaque” abre a matéria correspondente na página Notícias.

Notícias reúne as matérias disponíveis no feed (não é um arquivo histórico completo), com leitura integral recebida pelo RSS, busca por título ou resumo e filtros automáticos por assunto. A busca ignora diferenças de acento e maiúsculas. Busca e assunto são preservados nos parâmetros da URL; “Limpar filtros” restaura a lista completa.

Os assuntos são sugeridos a partir do título e das categorias do RSS. Seleções, categorias de base e premiações são identificadas por termos; as demais matérias de futebol feminino ficam em clubes e competições. A classificação pode precisar de ajustes conforme os termos usados pela fonte.
