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
    for (const arquivo of inputUpload.files) dados.append('fotos', arquivo);
    const endpoint = location.protocol === 'file:' ? 'http://127.0.0.1:5000/api/upload' : '/api/upload';
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
        btnEnviar.textContent = 'Enviar fotos';
        btnEnviar.disabled = false;
        inputUpload.disabled = false;
        formUpload.setAttribute('aria-busy', 'false');
    }
});
