// Comportamentos de index.html.
// Base de navegação repetida em cada página; mantenha as cópias consistentes.
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
        menu.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
                setMenu(false);
                // Devolve o foco ao botão para a navegação por teclado continuar previsível.
                menuButton.focus();
            }
        });
        document.addEventListener('click', (event) => {
            if (!event.target.closest('.barra-navegacao')) setMenu(false);
        });
        // Este limite deve acompanhar o breakpoint do menu no CSS desta página.
        window.matchMedia('(max-width: 1100px)').addEventListener('change', () => setMenu(false));
    }
    document.querySelectorAll('[data-ano]').forEach((element) => {
        element.textContent = new Date().getFullYear();
    });
})();

// Upload exclusivo da página inicial; os estados são exibidos sem recarregar a página.
(() => {
    const inputUpload = document.getElementById('upload-foto');
    const listaArquivos = document.getElementById('lista-arquivos');
    const btnEnviar = document.getElementById('btn-enviar');
    const formUpload = document.getElementById('form-upload');
    const statusUpload = document.getElementById('upload-status');
    function mostrarStatus(mensagem, estado = '') {
        statusUpload.textContent = mensagem;
        statusUpload.dataset.estado = estado;
    }
    inputUpload.addEventListener('change', () => {
        listaArquivos.replaceChildren();
        mostrarStatus('');
        const arquivos = Array.from(inputUpload.files);
        // O MIME informado pelo navegador ajuda na seleção, mas não substitui validação no servidor.
        const invalidos = arquivos.some((arquivo) => !arquivo.type.startsWith('image/'));
        btnEnviar.hidden = arquivos.length === 0;
        btnEnviar.disabled = invalidos;
        if (invalidos) mostrarStatus('Selecione somente imagens para continuar.', 'erro');
        if (!arquivos.length) {
            listaArquivos.textContent = 'Nenhuma foto selecionada.';
            return;
        }
        const ul = document.createElement('ul');
        arquivos.forEach((arquivo) => {
            const li = document.createElement('li');
            // textContent impede interpretar nomes de arquivos como marcação HTML.
            li.textContent = arquivo.name;
            ul.appendChild(li);
        });
        listaArquivos.appendChild(ul);
    });
    formUpload.addEventListener('submit', async (event) => {
        event.preventDefault();
        if (!inputUpload.files.length || btnEnviar.disabled) return;
        const quantidade = inputUpload.files.length;
        const dados = new FormData();
        // Repete o campo fotos; o navegador define automaticamente o boundary do multipart.
        for (const arquivo of inputUpload.files) dados.append('fotos', arquivo);
        // O caminho relativo usa a origem atual, funcionando por Flask, Apache ou túnel.
        // O endereço fixo é apenas o fallback para HTML aberto diretamente como arquivo.
        const endpoint = location.protocol === 'file:' ? 'http://127.0.0.1:5000/api/upload' : '/api/upload';
        // Evita envios duplicados e alterações na seleção enquanto a requisição está em andamento.
        btnEnviar.disabled = true;
        inputUpload.disabled = true;
        btnEnviar.textContent = 'Enviando…';
        formUpload.setAttribute('aria-busy', 'true');
        mostrarStatus('Enviando as fotos. Aguarde a confirmação.');
        try {
            const resposta = await fetch(endpoint, { method: 'POST', body: dados });
            const resultado = await resposta.json();
            if (!resposta.ok) throw new Error(resultado.mensagem || 'Não foi possível enviar as fotos.');
            mostrarStatus(quantidade === 1 ? 'Foto enviada com sucesso.' : 'Fotos enviadas com sucesso.', 'sucesso');
            inputUpload.value = '';
            listaArquivos.textContent = 'Nenhuma foto selecionada.';
            btnEnviar.hidden = true;
            inputUpload.disabled = false;
            inputUpload.focus();
        } catch (erro) {
            mostrarStatus(erro instanceof TypeError || erro instanceof SyntaxError
                ? 'Não foi possível comunicar com o servidor. Verifique sua conexão e tente novamente.'
                : erro.message, 'erro');
            // Preserva a seleção para permitir uma nova tentativa.
        } finally {
            // Restaura os controles tanto no sucesso quanto no erro, permitindo nova tentativa.
            btnEnviar.textContent = 'Enviar fotos';
            btnEnviar.disabled = false;
            inputUpload.disabled = false;
            formUpload.setAttribute('aria-busy', 'false');
        }
    });
})();
