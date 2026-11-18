// INICIAR RECURSOS DA PÁGINA
iniciarMenu();
iniciarUpload();
document.querySelectorAll('[data-ano]').forEach(elemento => {
    elemento.textContent = new Date().getFullYear();
});

function iniciarMenu() {
    const botao = document.querySelector('.menu-botao');
    const menu = document.querySelector('.menu');
    if (!botao || !menu) return;
    document.documentElement.classList.add('js');

    function abrirMenu(aberto) {
        menu.classList.toggle('aberto', aberto);
        botao.setAttribute('aria-expanded', String(aberto));
        botao.querySelector('.menu-rotulo').textContent = aberto ? 'Fechar' : 'Menu';
    }
    botao.addEventListener('click', () => abrirMenu(!menu.classList.contains('aberto')));
    document.addEventListener('keydown', evento => {
        if (evento.key === 'Escape' && menu.classList.contains('aberto')) {
            abrirMenu(false);
            botao.focus();
        }
    });
    document.addEventListener('click', evento => {
        if (!evento.target.closest('.barra-navegacao')) abrirMenu(false);
    });
    window.matchMedia('(max-width: 1100px)').addEventListener('change', () => abrirMenu(false));
}

// NOTÍCIAS
function iniciarUpload() {
    const form = document.getElementById('form-upload');
    if (!form) return;
    const input = document.getElementById('upload-foto');
    const lista = document.getElementById('lista-arquivos');
    const botao = document.getElementById('btn-enviar');
    const status = document.getElementById('upload-status');
    const contagem = document.getElementById('contagem-fotos');
    const tipos = ['image/png', 'image/jpeg', 'image/gif', 'image/webp'];
    let arquivos = [];
    let enviando = false;

    function avisar(texto, erro = false) {
        status.textContent = texto;
        status.classList.toggle('erro', erro);
    }
    function atualizarLista() {
        lista.replaceChildren();
        contagem.textContent = arquivos.length ? arquivos.length + ' de 10 fotos selecionadas.' : 'Nenhuma foto selecionada. Adicione até 10 fotos.';
        botao.disabled = enviando || arquivos.length === 0;
        input.disabled = enviando;
        botao.textContent = enviando ? 'Enviando fotos…' : 'Enviar fotos';
        form.setAttribute('aria-busy', String(enviando));
        if (!arquivos.length) {
            return;
        }
        const ul = document.createElement('ul');
        arquivos.forEach((arquivo, indice) => {
            const item = document.createElement('li');
            const nome = document.createElement('span');
            nome.textContent = arquivo.name + ' (' + (arquivo.size / 1024 / 1024).toFixed(1).replace('.', ',') + ' MB)';
            const remover = document.createElement('button');
            remover.type = 'button';
            remover.className = 'upload-remover';
            remover.textContent = 'Remover';
            remover.disabled = enviando;
            remover.setAttribute('aria-label', 'Remover ' + arquivo.name);
            remover.addEventListener('click', () => {
                arquivos.splice(indice, 1);
                atualizarLista();
                avisar('Foto removida. ' + arquivos.length + ' foto(s) selecionada(s).');
                input.focus();
            });
            const imagem = document.createElement('img');
            const url = URL.createObjectURL(arquivo);
            imagem.src = url;
            imagem.alt = 'Prévia de ' + arquivo.name;
            imagem.width = 80;
            imagem.height = 80;
            imagem.addEventListener('load', () => URL.revokeObjectURL(url), {once: true});
            imagem.addEventListener('error', () => URL.revokeObjectURL(url), {once: true});
            item.append(imagem, nome, remover);
            ul.append(item);
        });
        lista.append(ul);
    }
    input.addEventListener('change', () => {
        // MANTER FOTOS AO CANCELAR
        if (!input.files.length) return;
        const recusadas = [];
        for (const arquivo of input.files) {
            if (!tipos.includes(arquivo.type)) recusadas.push(arquivo.name + ': formato não aceito');
            else if (!arquivo.size || arquivo.size > 5 * 1024 * 1024) recusadas.push(arquivo.name + ': use um arquivo de até 5 MB');
            else if (arquivos.some(a => a.name === arquivo.name && a.size === arquivo.size && a.lastModified === arquivo.lastModified)) recusadas.push(arquivo.name + ': já está na lista');
            else if (arquivos.length >= 10) recusadas.push(arquivo.name + ': limite de 10 fotos');
            else arquivos.push(arquivo);
        }
        // PERMITIR SELECIONAR A MESMA FOTO
        input.value = '';
        atualizarLista();
        avisar(recusadas.length ? recusadas.join('; ') : arquivos.length + ' foto(s) pronta(s) para enviar.', recusadas.length > 0);
    });
    form.addEventListener('submit', async evento => {
        evento.preventDefault();
        if (enviando || !arquivos.length) return;
        const dados = new FormData();
        arquivos.forEach(arquivo => dados.append('fotos', arquivo));
        enviando = true;
        atualizarLista();
        avisar('Enviando fotos. Aguarde…');
        try {
            const resposta = await fetch(form.action, {method: 'POST', body: dados});
            const resultado = await resposta.json().catch(() => ({}));
            if (!resposta.ok) {
                avisar(resultado.mensagem || 'Não foi possível enviar. Confira os arquivos e tente novamente.', true);
                return;
            }
            arquivos = [];
            avisar('Fotos enviadas com sucesso! Você pode selecionar outras fotos.');
        } catch {
            avisar('Não foi possível conectar ao servidor. Sua seleção foi mantida; tente novamente.', true);
        } finally {
            enviando = false;
            atualizarLista();
        }
    });
    window.addEventListener('beforeunload', evento => {
        if (arquivos.length || enviando) {
            evento.preventDefault();
            evento.returnValue = '';
        }
    });
    atualizarLista();
}

// INFORMAÇÕES DO RODAPÉ
 document.querySelectorAll('[data-abrir-dialogo]').forEach(botao => {
    const dialogo = document.getElementById(botao.dataset.abrirDialogo);
    botao.addEventListener('click', () => dialogo.showModal());
    dialogo.querySelector('[data-fechar-dialogo]').addEventListener('click', () => dialogo.close());
    dialogo.addEventListener('click', evento => {
        if (evento.target === dialogo) {
            const r = dialogo.getBoundingClientRect();
            if (evento.clientX < r.left || evento.clientX > r.right || evento.clientY < r.top || evento.clientY > r.bottom) dialogo.close();
        }
    });
});
