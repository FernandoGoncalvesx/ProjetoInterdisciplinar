// Arquivo único das cinco páginas: menu e rodapé são comuns; notícias e upload são condicionais.
// A função imediata mantém estas variáveis fora do escopo global do navegador.
(() => {
    // Sem esta classe, o CSS mantém o menu visível quando o JavaScript não está disponível.
    document.documentElement.classList.add('js');
    const menuButton = document.querySelector('.menu-botao');
    const menu = document.querySelector('.menu');
    if (menuButton && menu) {
        // Atualiza juntos o estado visual e as informações usadas por leitores de tela.
        function setMenu(open) {
            menu.classList.toggle('aberto', open);
            menuButton.setAttribute('aria-expanded', String(open));
            menuButton.querySelector('.sr-only').textContent = open ? 'Fechar menu' : 'Abrir menu';
        }
        menuButton.addEventListener('click', () => setMenu(!menu.classList.contains('aberto')));
        // Escape fecha o menu estando o foco no botão ou em qualquer link.
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape' && menu.classList.contains('aberto')) {
                setMenu(false);
                // Devolve o foco ao botão para a navegação por teclado continuar previsível.
                menuButton.focus();
            }
        });
        document.addEventListener('click', (event) => {
            if (!event.target.closest('.barra-navegacao')) setMenu(false);
        });
        // Este limite deve acompanhar o breakpoint do menu no styles.css compartilhado.
        window.matchMedia('(max-width: 1100px)').addEventListener('change', () => setMenu(false));
    }
    document.querySelectorAll('[data-ano]').forEach((element) => {
        element.textContent = new Date().getFullYear();
    });

    // Apresenta os cards do elenco em sequência, respeitando a preferência por movimento reduzido.
    const cardsAtletas = document.querySelectorAll('.atleta-card');
    const movimentoReduzido = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (cardsAtletas.length && !movimentoReduzido) {
        cardsAtletas.forEach((card, indice) => {
            card.style.setProperty('--atraso-entrada', `${indice * 100}ms`);
            card.classList.add('atleta-entrada');
        });
    }

    // Array com os detalhes de cada notícia;
    const noticias = [
        {
            id: 1,
            titulo: 'Novo recorde mundial de atletismo',
            texto: 'A atleta brasileira bate o recorde mundial em saltos de longo alcance.',
            imagem: '../assets/logo.webp'
        },
        {
            id: 2,
            titulo: 'Garfo é encontrado na cozinha',
            texto: 'Um garfo comum de aço inoxidável foi encontrado na cozinha de uma casa do sul do Brasil. A polícia investiga o caso.',
            imagem: '../assets/logo.webp'
        },
        {
            id: 3,
            titulo: 'Novo site sobre a seleção brasileira de futebol',
            texto: 'Acaba de ser inaugurado um novo site sobre a seleção brasileira de futebol.',
            imagem: '../assets/logo.webp'
        }
    ];
    // Notícias (somente em noticias.html): mostra título e resumo do card em um diálogo. Eventualmente mostrará a notícia completa ao clicar, mas não há conteúdo real para isso no site de exemplo.
    const dialogoNoticia = document.getElementById('detalhes-noticia');
    // Esta condição é necessária: as outras quatro páginas não possuem o diálogo.
    if (dialogoNoticia) {
        document.querySelectorAll('.abrir-noticia').forEach((botao) => {
            botao.addEventListener('click', () => {
                const card = botao.closest('.card');
                let id = card.getAttribute('id');
                id = id ? parseInt(id.replace('noticia-', ''), 10) : null;
                if (id !== null) {
                    const noticia = noticias.find(n => n.id === id);
                    if (noticia !== null) {
                        document.getElementById('detalhes-titulo').textContent = noticia.titulo;
                        document.getElementById('detalhes-texto').textContent = noticia.texto;
                        document.getElementById('img-noticia').src = noticia.imagem;
                        dialogoNoticia.showModal();
                    }
                }
            });
        });
        dialogoNoticia.querySelector('.btn-close').addEventListener('click', () => dialogoNoticia.close());
        // O diálogo é só o card; um clique no próprio <dialog> acontece no fundo escurecido.
        dialogoNoticia.addEventListener('click', (event) => {
            if (event.target === dialogoNoticia) dialogoNoticia.close();
        });
    }

    // Somente a home possui este formulário; nas demais páginas o bloco é ignorado.
    // A seleção funciona localmente. O envio depende de um action explícito no HTML.
    const form = document.getElementById('form-upload');
    if (form) {
        // Limites de interface: não substituem a validação dos arquivos no servidor.
        const MAX_ARQUIVOS = 10;
        const MAX_MB = 5;
        const input = document.getElementById('upload-foto');
        const lista = document.getElementById('lista-arquivos');
        const botao = document.getElementById('btn-enviar');
        const status = document.getElementById('upload-status');
        // Esta lista controla o envio: remover uma foto daqui não altera o FileList do input.
        let arquivos = [];
        const aviso = (texto, erro) => {
            status.textContent = texto;
            status.classList.toggle('erro', Boolean(erro));
        };
        const tamanho = (bytes) => (bytes / 1024 / 1024).toFixed(1).replace('.', ',') + ' MB';
        function desenhar() {
            lista.replaceChildren();
            botao.hidden = arquivos.length === 0;
            if (!arquivos.length) {
                lista.textContent = 'Nenhuma foto selecionada.';
                return;
            }
            const ul = document.createElement('ul');
            arquivos.forEach((arquivo, indice) => {
                const li = document.createElement('li');
                const nome = document.createElement('span');
                nome.textContent = arquivo.name + ' (' + tamanho(arquivo.size) + ')';
                const remover = document.createElement('button');
                remover.type = 'button';
                remover.className = 'upload-remover';
                remover.textContent = 'Remover';
                remover.setAttribute('aria-label', 'Remover ' + arquivo.name);
                remover.addEventListener('click', () => {
                    arquivos.splice(indice, 1);
                    desenhar();
                    aviso('Foto removida.');
                    input.focus();
                });
                li.append(nome, remover);
                ul.append(li);
            });
            lista.append(ul);
        }
        input.addEventListener('change', () => {
            const recusadas = [];
            arquivos = [];
            Array.from(input.files).forEach((arquivo) => {
                if (!arquivo.type.startsWith('image/')) recusadas.push(arquivo.name + ': não é uma imagem');
                else if (arquivo.size > MAX_MB * 1024 * 1024) recusadas.push(arquivo.name + ': maior que ' + MAX_MB + ' MB');
                else if (arquivos.length >= MAX_ARQUIVOS) recusadas.push(arquivo.name + ': limite de ' + MAX_ARQUIVOS + ' fotos');
                else arquivos.push(arquivo);
            });
            desenhar();
            if (recusadas.length) aviso('Não foi possível adicionar: ' + recusadas.join('; ') + '.', true);
            else aviso(arquivos.length ? arquivos.length + ' foto(s) pronta(s) para envio.' : '');
        });
        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            const destino = form.getAttribute('action');
            // PENDÊNCIA: index.html não define action; todo envio atual termina neste aviso.
            // O trecho de FormData/fetch abaixo fica sem uso no fluxo atual. A rota existente
            // no Flask é POST /api/upload, mas sua ligação depende de configurar o formulário.
            if (!destino) {
                aviso('O envio de fotos ainda não está disponível neste site.', true);
                return;
            }
            const dados = new FormData();
            arquivos.forEach((arquivo) => dados.append('fotos', arquivo));
            botao.disabled = true;
            aviso('Enviando…');
            try {
                const resposta = await fetch(destino, { method: 'POST', body: dados });
                if (!resposta.ok) throw new Error(resposta.status);
                arquivos = [];
                input.value = '';
                desenhar();
                aviso('Fotos enviadas com sucesso.');
            } catch (erro) {
                // Preserva a seleção para nova tentativa quando houver falha de rede ou HTTP.
                aviso('Não foi possível enviar as fotos. Tente novamente.', true);
            } finally {
                botao.disabled = false;
            }
        });
    }
})();
