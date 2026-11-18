(() => {
    const canvas = document.getElementById('previa-card');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const modelo = JSON.parse(document.getElementById('modelo-card').textContent);
    const nome = document.getElementById('card-nome');
    const posicao = document.getElementById('card-posicao');
    const zoom = document.getElementById('card-zoom');
    const x = document.getElementById('card-x');
    const y = document.getElementById('card-y');
    const baixar = document.getElementById('card-baixar');
    const ajustes = document.getElementById('ajustes-card');
    const status = document.getElementById('editor-status');
    let pessoa = null;
    let arrasto = null;
    function escudo() {
        ctx.beginPath();
        ctx.moveTo(45, 60); ctx.lineTo(270, 60); ctx.lineTo(375, 20);
        ctx.lineTo(480, 60); ctx.lineTo(705, 60); ctx.lineTo(705, 885);
        ctx.quadraticCurveTo(620, 965, 375, 1020);
        ctx.quadraticCurveTo(130, 965, 45, 885); ctx.closePath();
    }
    function desenhar() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.save(); escudo(); ctx.clip();
        const gradiente = ctx.createLinearGradient(0, 0, 750, 1050);
        gradiente.addColorStop(0, '#073d86'); gradiente.addColorStop(1, '#020b24');
        ctx.fillStyle = gradiente; ctx.fillRect(0, 0, 750, 1050);
        ctx.fillStyle = '#ffffff0d';
        for (let i = 0; i < 8; i++) {
            ctx.beginPath(); ctx.moveTo(i*130, 0); ctx.lineTo(i*130+300, 0);
            ctx.lineTo(i*130-200, 1050); ctx.fill();
        }
        ctx.save();
        ctx.beginPath(); ctx.rect(modelo.foto_x, modelo.foto_y, modelo.foto_largura, modelo.foto_altura); ctx.clip();
        if (pessoa) {
            const escala = modelo.foto_largura / pessoa.width * Number(zoom.value);
            const largura = pessoa.width * escala, altura = pessoa.height * escala;
            ctx.drawImage(pessoa, modelo.foto_x+(modelo.foto_largura-largura)/2+Number(x.value),
                modelo.foto_y+Number(y.value), largura, altura);
        } else {
            ctx.fillStyle = '#ffffffaa'; ctx.font = '28px sans-serif'; ctx.textAlign = 'center';
            ctx.fillText('Sua foto aqui', 375, 420);
        }
        ctx.restore();
        ctx.fillStyle = '#07142c'; ctx.fillRect(65, 750, 620, 250);
        ctx.fillStyle = '#e6c581'; ctx.textAlign = 'center';
        ctx.font = 'bold 52px sans-serif';
        ctx.fillText((nome.value.trim() || 'SEU NOME').toUpperCase(), 375, 825, 570);
        ctx.fillRect(115, 850, 520, 3);
        ctx.font = 'bold 44px sans-serif'; ctx.fillText(posicao.value, 375, 920);
        ctx.restore();
        escudo(); ctx.strokeStyle = '#ad854a'; ctx.lineWidth = 16; ctx.stroke();
    }
    function centralizar() { zoom.value = 1; x.value = y.value = 0; desenhar(); }
    window.editorCard = {
        limpar() {
            pessoa = null; ajustes.disabled = baixar.disabled = true;
            status.textContent = 'Envie uma foto para começar.'; centralizar();
        },
        async carregar(src) {
            const imagem = new Image();
            imagem.src = src; await imagem.decode();
            pessoa = imagem; ajustes.disabled = baixar.disabled = false;
            centralizar();
            status.textContent = 'Arraste a pessoa ou use os controles para enquadrar da cintura para cima.';
        }
    };
    [nome, posicao, zoom, x, y].forEach(campo => campo.addEventListener('input', desenhar));
    document.getElementById('card-reiniciar').addEventListener('click', centralizar);
    canvas.addEventListener('pointerdown', evento => {
        if (!pessoa) return;
        arrasto = {x: evento.clientX, y: evento.clientY, anteriorX: Number(x.value), anteriorY: Number(y.value)};
        canvas.setPointerCapture(evento.pointerId);
    });
    canvas.addEventListener('pointermove', evento => {
        if (!arrasto) return;
        const fator = canvas.width / canvas.getBoundingClientRect().width;
        x.value = arrasto.anteriorX + (evento.clientX-arrasto.x)*fator;
        y.value = arrasto.anteriorY + (evento.clientY-arrasto.y)*fator;
        desenhar();
    });
    ['pointerup', 'pointercancel', 'lostpointercapture'].forEach(tipo => canvas.addEventListener(tipo, () => {arrasto = null;}));
    baixar.addEventListener('click', () => {
        if (!pessoa) return;
        canvas.toBlob(blob => {
            if (!blob) {status.textContent = 'Não foi possível gerar o PNG.'; return;}
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url; link.download = 'meu-card.png';
            document.body.append(link); link.click(); link.remove();
            setTimeout(() => URL.revokeObjectURL(url), 1000);
            status.textContent = 'Card gerado em PNG.';
        }, 'image/png');
    });
    desenhar();
})();

