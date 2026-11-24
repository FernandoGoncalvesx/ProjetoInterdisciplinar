(() => {
    const canvas = document.getElementById('previa-card');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const modelo = JSON.parse(document.getElementById('modelo-card').textContent);
    const nome = document.getElementById('card-nome');
    const posicao = document.getElementById('card-posicao');
    const notaGeral = document.getElementById('card-geral');
    const zoom = document.getElementById('card-zoom');
    const x = document.getElementById('card-x');
    const y = document.getElementById('card-y');
    const baixar = document.getElementById('card-baixar');
    const ajustes = document.getElementById('ajustes-card');
    const status = document.getElementById('editor-status');
    const modelos = JSON.parse(document.getElementById('modelos-card').textContent);
    const girar = document.getElementById('card-girar');
    const sorteioStatus = document.getElementById('sorteio-status');
    const camposAtributos = [...document.querySelectorAll('[data-atributo]')];
    let selecionado = modelos[0];
    let fundo = null;
    let versaoModelo = 0;
    let atributos = {};
    let pessoa = null;
    let arrasto = null;
    function atualizarDownload() { baixar.disabled = !pessoa || !fundo || girar.disabled; }
    function lerNota(campo) {
        return campo.value !== '' && campo.validity.valid ? Number(campo.value) : null;
    }
    function geralAtual() {
        const manual = lerNota(notaGeral);
        if (manual !== null) return manual;
        const valores = Object.values(atributos);
        return valores.length === 6 && valores.every(valor => valor !== null)
            ? Math.round(valores.reduce((a, b) => a + b, 0) / 6) : '--';
    }
    function atualizarAtributos() {
        atributos = Object.fromEntries(camposAtributos.map(campo => [campo.dataset.atributo, lerNota(campo)]));
        desenhar();
    }
    function desenhar() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        if (!fundo) return;
        ctx.save();
        // Coordenadas da arte original (370 x 620), exportadas em resolução dupla.
        ctx.scale(canvas.width / 370, canvas.height / 620);
        ctx.drawImage(fundo, 0, 0, 370, 620);
        ctx.save();
        ctx.beginPath();
        ctx.rect(modelo.foto_x, modelo.foto_y, modelo.foto_largura, modelo.foto_altura);
        ctx.clip();
        if (pessoa) {
            const escala = modelo.foto_largura / pessoa.width * Number(zoom.value);
            const largura = pessoa.width * escala, altura = pessoa.height * escala;
            ctx.drawImage(pessoa, modelo.foto_x + (modelo.foto_largura-largura)/2 + Number(x.value),
                modelo.foto_y + Number(y.value), largura, altura);
        }
        ctx.restore();
        // Textos variáveis sobre a textura, sem painéis que encubram a arte.
        const baixo = ['preto', 'verde', 'dourado'].includes(selecionado.id);
        const deslocamento = baixo ? -20 : 0;
        const coluna = ['branco', 'preto'].includes(selecionado.id) ? 12 : 0;
        ctx.fillStyle = selecionado.texto || '#ffe4a1';
        ctx.textAlign = 'center';
        ctx.font = 'italic bold 52px "Arial Narrow", sans-serif';
        ctx.fillText(String(geralAtual()), 76 + coluna, 134 + deslocamento, 65);
        ctx.font = 'bold 27px "Arial Narrow", sans-serif';
        ctx.fillText(posicao.value.trim().toUpperCase(), 76 + coluna, 167 + deslocamento, 65);
        ctx.font = 'italic bold 40px "Arial Narrow", sans-serif';
        ctx.fillText((nome.value.trim() || 'NOME').toUpperCase(), 185, 378 + deslocamento, 255);
        ctx.font = 'bold 28px "Arial Narrow", sans-serif';
        ctx.textAlign = 'right';
        ['RIT', 'FIN', 'PAS', 'DRI', 'DEF', 'FIS'].forEach((sigla, i) => {
            const px = (i < 3 ? 98 : 245) + coluna;
            const py = 434 + (i % 3) * 35 + deslocamento;
            ctx.fillText(atributos[sigla] != null ? String(atributos[sigla]).padStart(2, '0') : '--', px, py, 34);
        });
        ctx.restore();
    }
    async function trocarModelo(id) {
        selecionado = modelos.find(item => item.id === id);
        const versao = ++versaoModelo;
        fundo = null; atualizarDownload(); desenhar();
        status.textContent = 'Carregando modelo…';
        try {
            const imagem = new Image();
            imagem.src = `/assets/cards/modelos/${id}.png?v=10`;
            await imagem.decode();
            if (versao !== versaoModelo) return;
            fundo = imagem; desenhar(); atualizarDownload();
            status.textContent = `Modelo ${selecionado.nome} selecionado.`;
        } catch (erro) {
            if (versao === versaoModelo) status.textContent = 'Não foi possível carregar o modelo. Selecione outro ou recarregue a página.';
        }
    }
    document.querySelectorAll('[name="card-modelo"]').forEach(campo => {
        campo.addEventListener('change', () => trocarModelo(campo.value));
    });
    girar.addEventListener('click', async () => {
        if (girar.disabled) return;
        girar.disabled = true; atualizarDownload();
        girar.textContent = 'Girando…';
        sorteioStatus.textContent = 'Sorteando atributos…';
        if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            await new Promise(resolve => setTimeout(resolve, 500));
        }
        atributos = Object.fromEntries(camposAtributos.map(campo => {
            const valor = Math.floor(Math.random() * 99) + 1;
            campo.value = valor;
            return [campo.dataset.atributo, valor];
        }));
        girar.disabled = false; girar.textContent = 'Girar novamente';
        const geral = geralAtual();
        sorteioStatus.textContent = `Atributos sorteados. Nota geral: ${geral}.`;
        desenhar(); atualizarDownload();
    });
    function centralizar() { zoom.value = 1; x.value = y.value = 0; desenhar(); }
    window.editorCard = {
        limpar() {
            pessoa = null; ajustes.disabled = baixar.disabled = true;
            status.textContent = 'Envie uma foto para começar.'; centralizar();
        },
        async carregar(src) {
            const imagem = new Image();
            imagem.src = src; await imagem.decode();
            pessoa = imagem; ajustes.disabled = false; atualizarDownload();
            centralizar();
            status.textContent = 'Arraste a pessoa ou use os controles para enquadrar da cintura para cima.';
        }
    };
    [nome, posicao, notaGeral, zoom, x, y].forEach(campo => campo.addEventListener('input', desenhar));
    document.getElementById('card-reiniciar').addEventListener('click', centralizar);
    canvas.addEventListener('pointerdown', evento => {
        if (!pessoa) return;
        arrasto = {x: evento.clientX, y: evento.clientY, anteriorX: Number(x.value), anteriorY: Number(y.value)};
        canvas.setPointerCapture(evento.pointerId);
    });
    canvas.addEventListener('pointermove', evento => {
        if (!arrasto) return;
        const fator = 370 / canvas.getBoundingClientRect().width;
        x.value = arrasto.anteriorX + (evento.clientX-arrasto.x)*fator;
        y.value = arrasto.anteriorY + (evento.clientY-arrasto.y)*fator;
        desenhar();
    });
    ['pointerup', 'pointercancel', 'lostpointercapture'].forEach(tipo => canvas.addEventListener(tipo, () => {arrasto = null;}));
    baixar.addEventListener('click', () => {
        if (!pessoa || !fundo || girar.disabled) return;
        canvas.toBlob(blob => {
            if (!blob) {status.textContent = 'Não foi possível gerar o PNG.'; return;}
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url; link.download = `meu-card-${selecionado.id}.png`;
            document.body.append(link); link.click(); link.remove();
            setTimeout(() => URL.revokeObjectURL(url), 1000);
            status.textContent = 'Card gerado em PNG.';
        }, 'image/png');
    });
    camposAtributos.forEach(campo => campo.addEventListener('input', atualizarAtributos));
    atualizarAtributos();
    trocarModelo(selecionado.id);
})();

