# Frontend: onde editar

```text
frontend/
├── assets/                     # Logo e ícone
├── css/
│   ├── base.css                # Estilos compartilhados
│   └── tema.css                # Identidade visual
├── js/
│   └── portal.js               # Menu, fotos e rodapé
└── templates/
    ├── base.html               # Estrutura comum e topo das páginas
    ├── componentes/            # Menu e rodapé
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
- Links, títulos e URLs das páginas: `PAGINAS` em `backend/app.py`.
- Rodapé: `templates/componentes/rodape.html`.
- Aparência: `css/base.css` e `css/tema.css`.
- Menu móvel e upload: `js/portal.js`.

CSS e JavaScript permanecem em arquivos compartilhados. Separe arquivos específicos quando uma funcionalidade crescer o suficiente para justificar isso.

## Abrir o site

Na raiz do projeto:

```powershell
.\venv\Scripts\python.exe -m backend.app
```

Abra http://127.0.0.1:5000. Os HTMLs precisam ser renderizados pelo Flask. As URLs existentes continuam funcionando. Os templates não são publicados como arquivos.

Notícias aponta para os comunicados oficiais da CBF. Jogos vêm do MySQL. Fotos enviadas ficam em `backend/uploads/`.

## Melhorias incorporadas

A interface inclui menu móvel compacto, histórico expansível e envio de fotos com prévias e seleção acumulada.

O rodapé principal tem Ajuda, Suporte, Privacidade e Versão 1.0.0. Os botões abrem informações em janelas acessíveis, fechadas pelo botão ou pela tecla Escape. Suporte apresenta orientações de solução de problemas; não há canal de contato configurado.

O elenco tem atualização manual, com data e fontes da CBF informadas na página.

## Papel da inicial e de Notícias

A inicial mostra o próximo jogo cadastrado e um atalho para a página Notícias, onde fica o link para a CBF.
