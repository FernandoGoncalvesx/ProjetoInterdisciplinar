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

    const dialogoNoticia = document.getElementById('detalhes-noticia');
    const listaNoticias = document.getElementById('lista-noticias');

    if (dialogoNoticia && listaNoticias) {

        let noticias = [];

        // Busca todas as notícias na API Flask.
        async function carregarNoticias() {
            try {
                const resposta = await fetch('/api/noticias');

                if (!resposta.ok) {
                    throw new Error('Erro ao acessar api de notícias: ' + resposta.status);
                }

                noticias = await resposta.json();

                if (!resposta.ok) {
                    throw new Error('Erro gerar JSON de notícias: ' + resposta.status);
                }

                if (noticias.length === 0) {
                    return;
                }

                // Limpa o conteúdo inicial.
                listaNoticias.replaceChildren();

                // Cria um card para cada notícia recebida.
                noticias.forEach((noticia) => {

                    const coluna = document.createElement('div');
                    coluna.className = 'col-12 col-md-6 col-lg-4';

                    const card = document.createElement('article');
                    card.className = 'card noticia-card';
                    card.id = 'noticia-' + noticia.id;

                    const corpo = document.createElement('div');
                    corpo.className = 'card-body';

                    const titulo = document.createElement('h3');
                    titulo.className = 'card-title';
                    titulo.textContent = noticia.titulo;

                    const resumo = document.createElement('p');
                    resumo.className = 'card-text';

                    resumo.textContent =
                        noticia.texto.length > 160
                            ? noticia.texto.substring(0, 160) + '...'
                            : noticia.texto;

                    const botao = document.createElement('button');
                    botao.type = 'button';
                    botao.className = 'btn btn-primary abrir-noticia';
                    botao.textContent = 'Abrir notícia';
                    botao.setAttribute(
                        'aria-label',
                        'Abrir notícia'
                    );

                    // Guarda o identificador da notícia no botão.
                    botao.dataset.id = noticia.id;

                    corpo.append(titulo, resumo, botao);
                    card.appendChild(corpo);
                    coluna.appendChild(card);

                    listaNoticias.appendChild(coluna);
                });

            } catch (erro) {
                console.error('Erro ao carregar notícias:', erro);
            }
        }

        // Abre o diálogo utilizando os dados da notícia selecionada.
        listaNoticias.addEventListener('click', (event) => {

            const botao = event.target.closest('.abrir-noticia');

            if (!botao) return;

            const id = Number(botao.dataset.id);

            const noticia = noticias.find(
                n => Number(n.id) === id
            );

            if (!noticia) return;

            document.getElementById('detalhes-titulo').textContent =
                noticia.titulo;

            document.getElementById('detalhes-texto').textContent =
                noticia.texto;

            const imagem = document.getElementById('img-noticia');

            if (noticia.imagem_url) {
                imagem.src = noticia.imagem_url;
                imagem.hidden = false;
            } else {
                imagem.removeAttribute('src');
                imagem.hidden = true;
            }

            dialogoNoticia.showModal();
        });

        // Fecha o diálogo pelo botão.
        dialogoNoticia.querySelector('.btn-close')
            .addEventListener('click', () => {
                dialogoNoticia.close();
            });

        // Fecha ao clicar no fundo do diálogo.
        dialogoNoticia.addEventListener('click', (event) => {
            if (event.target === dialogoNoticia) {
                dialogoNoticia.close();
            }
        });

        // Inicia a consulta ao banco.
        carregarNoticias();
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
