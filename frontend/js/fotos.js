(() => {
    const form = document.getElementById('form-foto-card');
    if (!form) return;
    const input = document.getElementById('foto-card');
    const botao = document.getElementById('processar-foto');
    const status = document.getElementById('foto-status');
    const previa = document.getElementById('foto-original');
    const avisos = document.getElementById('foto-avisos');
    let url = null;
    let ocupado = false;
    function mensagem(texto, erro = false) {
        status.textContent = texto;
        status.classList.toggle('erro', erro);
    }
    input.addEventListener('change', () => {
        window.editorCard.limpar();
        avisos.replaceChildren();
        if (url) URL.revokeObjectURL(url);
        previa.hidden = true;
        previa.removeAttribute('src');
        const foto = input.files[0];
        botao.disabled = true;
        if (!foto) { mensagem('Selecione uma foto.'); return; }
        if (!['image/png', 'image/jpeg', 'image/webp'].includes(foto.type) || !foto.size || foto.size > 5 * 1024 * 1024) {
            mensagem('Escolha uma foto PNG, JPEG ou WebP de até 5 MB.', true);
            return;
        }
        url = URL.createObjectURL(foto);
        previa.src = url;
        previa.hidden = false;
        botao.disabled = false;
        mensagem('Foto selecionada. Clique em remover fundo.');
    });
    form.addEventListener('submit', async evento => {
        evento.preventDefault();
        if (ocupado || botao.disabled || !input.files[0]) return;
        const dados = new FormData();
        dados.append('foto', input.files[0]);
        ocupado = true;
        input.disabled = botao.disabled = true;
        window.editorCard.limpar();
        avisos.replaceChildren();
        form.setAttribute('aria-busy', 'true');
        mensagem('Processando a foto. Na primeira execução, a preparação pode demorar alguns minutos.');
        try {
            const resposta = await fetch(form.action, {method: 'POST', body: dados});
            const resultado = await resposta.json();
            if (!resposta.ok) throw new Error(resultado.mensagem || 'Falha ao processar a foto.');
            await window.editorCard.carregar(resultado.recorte);
            for (const aviso of resultado.avisos || []) {
                const item = document.createElement('li');
                item.textContent = aviso;
                avisos.append(item);
            }
            mensagem('Recorte pronto. Ajuste a pessoa no card e confira os contornos.');
        } catch (erro) {
            mensagem(erro.message || 'Não foi possível conectar ao servidor.', true);
        } finally {
            ocupado = false;
            input.disabled = botao.disabled = false;
            form.setAttribute('aria-busy', 'false');
        }
    });
    window.addEventListener('beforeunload', evento => {
        if (ocupado) { evento.preventDefault(); evento.returnValue = ''; }
    });
})();

