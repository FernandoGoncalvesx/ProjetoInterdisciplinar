(() => {
    const dialogoNoticia = document.getElementById('detalhes-noticia');
    const listaNoticias = document.getElementById('lista-noticias');

    if (dialogoNoticia && listaNoticias) {

        async function crawlerNoticias() {
            try {
                const resposta = await fetch('/api/crawler');
                if (!resposta.ok) throw new Error('Falha na coleta: ' + resposta.status);
                await carregarNoticias();
            }
            catch (erro) {
                console.error('Erro ao acessar api crawler: ' + erro);
                document.getElementById('noticias-status').textContent = 'Não foi possível atualizar pela CBF. As notícias já salvas continuam disponíveis.';
            }
        }


        let noticias = JSON.parse(document.getElementById('noticias-iniciais').textContent);

        function inserirTextoComQuebras(elemento, texto) {
            elemento.replaceChildren();
            (texto || '').split(/(<br\s*\/?>)/gi).forEach((parte) => {
                if (/^<br\s*\/?>$/i.test(parte)) {
                    elemento.appendChild(document.createElement('br'));
                } else {
                    elemento.appendChild(document.createTextNode(parte));
                }
            });
        }

        // Busca todas as notícias na API Flask.
        async function carregarNoticias() {
            try {
                const resposta = await fetch('/api/noticias');

                if (!resposta.ok) {
                    throw new Error('Erro ao acessar api de notícias: ' + resposta.status);
                }

                noticias = await resposta.json();

                renderizarNoticias();
                document.getElementById('noticias-status').textContent = 'Notícias atualizadas.';

            } catch (erro) {
                console.error('Erro ao carregar notícias:', erro);
                document.getElementById('noticias-status').textContent = 'Não foi possível carregar as notícias. Tente novamente.';
            }
        }

        function renderizarNoticias() {
            if (noticias.length === 0) {
                listaNoticias.textContent = 'Nenhuma notícia publicada no momento.';
                return;
            }

            // Limpa o conteúdo inicial.
            listaNoticias.replaceChildren();

            // Cria um card para cada notícia recebida.
            noticias.forEach((noticia) => {

                const coluna = document.createElement('div');

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

                const textoResumo = (noticia.texto || '').replace(/<br\s*\/?>/gi, ' ');
                resumo.textContent = textoResumo.length > 160
                    ? textoResumo.substring(0, 160) + '...'
                    : textoResumo;

                const botao = document.createElement('button');
                botao.type = 'button';
                botao.className = 'btn btn-primary abrir-noticia';
                botao.textContent = 'Abrir notícia';

                // Guarda o identificador da notícia no botão.
                botao.dataset.id = noticia.id;

                corpo.append(titulo, resumo, botao);
                card.appendChild(corpo);
                coluna.appendChild(card);

                listaNoticias.appendChild(coluna);
            });
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

            inserirTextoComQuebras(
                document.getElementById('detalhes-texto'),
                noticia.texto
            );

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

        if (noticias.length) renderizarNoticias();
        const atualizar = document.getElementById('atualizar-noticias');
        atualizar.hidden = false;
        atualizar.addEventListener('click', async () => {
            atualizar.disabled = true;
            document.getElementById('noticias-status').textContent = 'Atualizando notícias…';
            try { await crawlerNoticias(); }
            finally { atualizar.disabled = false; atualizar.focus({preventScroll:true}); }
        });
    }

})();
