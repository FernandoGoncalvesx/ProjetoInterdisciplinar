const inputUpload = document.getElementById('upload-foto');
const listaArquivos = document.getElementById('lista-arquivos');
const btnEnviar = document.getElementById('btn-enviar');

// Atualiza a lista quando seleciona os arquivos
inputUpload.addEventListener('change', function() {
    listaArquivos.innerHTML = ''; 
    const arquivos = Array.from(inputUpload.files);

    if (arquivos.length > 0) {
        const ul = document.createElement('ul');

        arquivos.forEach(arquivo => {
            const li = document.createElement('li');
            li.textContent = arquivo.name;
            ul.appendChild(li);
        });

        listaArquivos.appendChild(ul);
        btnEnviar.style.display = 'block'; // Mostra o botão
    } else {
        listaArquivos.textContent = 'Nenhuma foto selecionada.';
        btnEnviar.style.display = 'none'; // Esconde o botão
    }
});

// Faz o POST para o Python quando clica em enviar
btnEnviar.addEventListener('click', async function() {
    const arquivos = inputUpload.files;
    if (arquivos.length === 0) return;

    const formData = new FormData();
    for (let i = 0; i < arquivos.length; i++) {
        // 'fotos' é o nome exato que o Python está esperando no request.files
        formData.append('fotos', arquivos[i]); 
    }

    try {
        btnEnviar.textContent = 'Enviando...';
        btnEnviar.disabled = true;

        // Envia para o servidor Flask
        const resposta = await fetch('http://127.0.0.1:5000/api/upload', {
            method: 'POST',
            body: formData
        });

        const resultado = await resposta.json();
        alert(resultado.mensagem); // Mensagem de sucesso do Python
        
        // Limpa a tela
        inputUpload.value = '';
        listaArquivos.textContent = 'Nenhuma foto selecionada.';
        btnEnviar.style.display = 'none';

    } catch (erro) {
        console.error('Erro:', erro);
        alert('Erro ao comunicar com o servidor.');
    } finally {
        btnEnviar.textContent = 'Enviar para o Servidor Python';
        btnEnviar.disabled = false;
    }
});