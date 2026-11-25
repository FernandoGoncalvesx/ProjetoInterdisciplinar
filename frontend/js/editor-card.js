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
    const modelos = JSON.parse(document.getElementById('modelos-card').textContent);
    const girar = document.getElementById('card-girar');
    const camposAtributos = [...document.querySelectorAll('[data-atributo]')];

    let selecionado = modelos[0];
    let fundo = null;
    let versaoModelo = 0;
    let atributos = {};
    let pessoa = null;
    let enquadramento = {zoom: 1, x: 0, y: 0};
    let arrasto = null;
    let alterado = false;
    let revisao = 0;

    function atualizarDownload() {
        baixar.disabled = !pessoa || !fundo || girar.disabled;
    }

    function lerNota(campo) {
        return campo && campo.value !== '' && campo.validity.valid ? Number(campo.value) : null;
    }

    function geralAtual() {
        const valores = Object.values(atributos);
        return valores.length === 6 && valores.every(valor => valor !== null)
            ? Math.round(valores.reduce((a, b) => a + b, 0) / 6) : '--';
    }

    function atualizarAtributos() {
        atributos = Object.fromEntries(camposAtributos.map(campo => [campo.dataset.atributo, lerNota(campo)]));
        desenhar();
    }

    function desenhar() {
        revisao++;
        if (pessoa) alterado = true;
        [zoom, x, y].forEach(campo => { document.getElementById(`${campo.id}-valor`).value = Number(campo.value).toFixed(campo === zoom ? 2 : 0); });
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
            ctx.drawImage(pessoa, modelo.foto_x + (modelo.foto_largura - largura) / 2 + Number(x.value),
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
        ctx.fillText(nome.textContent.trim().toUpperCase(), 185, 378 + deslocamento, 255);
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
        selecionado = modelos.find(item => item.id === id) || modelos[0];
        const versao = ++versaoModelo;
        fundo = null;
        atualizarDownload();
        desenhar();
        status.textContent = 'Carregando modelo…';
        try {
            const imagem = new Image();
            imagem.src = `/assets/cards/modelos/${selecionado.id}.png?v=10`;
            await imagem.decode();
            if (versao !== versaoModelo) return;
            fundo = imagem;
            desenhar();
            atualizarDownload();
            status.textContent = `Modelo ${selecionado.nome} selecionado.`;
        } catch (erro) {
            if (versao === versaoModelo) {
                status.textContent = 'Não foi possível carregar o modelo. Selecione outro ou recarregue a página.';
            }
        }
    }

    /* ══ Card swap (Bencho — MIT License) ════════════════════════════
       A stack of photo cards in depth, each a step further back and up
       to the right, slanted. Press the front card, or drag and fling it,
       and it goes straight to the back while the rest step forward.
       With Auto on it also does that by itself every few seconds,
       pausing while a pointer is on the stack.

       ── A CARD IS ITS SLOT ──────────────────────────────────
       The order is the only state: which card is in front, which is
       behind it. A slot is a fixed transform, so moving a card is
       changing its slot and letting the transition carry it — the card
       sent back takes the back slot's paint order AT ONCE and travels
       there behind the others. That needs the paint order to be the
       z-index and not the depth, so the stage is flat (no preserve-3d)
       and the perspective sits on the stage itself, aimed at the
       block's middle as it was when it sat on .csw. */

    const STEP_X = 106;
    const STEP_Y = 22;
    const STEP_Z = 65;
    const AUTO_SWAP = false;
    const AUTO_EVERY = 4;

    const slot = (k) =>
        `translate3d(${k * STEP_X}px, ${-k * STEP_Y}px, ${-k * STEP_Z}px) skewY(6deg)`;

    const cswRoot = document.getElementById('card-swap');
    const cardEls = [...document.querySelectorAll('.csw-card')];
    const elsById = Object.fromEntries(cardEls.map(el => [el.dataset.modeloId, el]));
    let order = cardEls.map(el => el.dataset.modeloId);

    const swapState = {
        hover: false,
        drag: null,
        unhook: () => {},
    };

    function renderSlots() {
        document.getElementById("modelo-atual").textContent = modelos.find(m => m.id === order[0]).nome;
        order.forEach((id, k) => {
            const el = elsById[id];
            if (!el) return;
            const front = k === 0;
            el.style.zIndex = String(order.length - k);
            /* the slot is a variable the stylesheet turns into the
               transform; the drag writes the transform itself, which
               wins until it is cleared */
            el.style.setProperty('--t', slot(k));
            if (front) {
                el.setAttribute('data-front', 'true');
            } else {
                el.removeAttribute('data-front');
            }
        });
    }

    /* send the front card to the back: it takes the back slot now, from
       wherever it is — the front slot, or where a drag left it */
    /* every card goes back to its slot: no drag survives a swap, so a
       card can never be left holding where a hand once put it */
    function settle() {
        for (const el of cardEls) {
            el.style.transition = '';
            el.style.transform = '';
        }
    }

    function swap() {
        settle();
        order = [...order.slice(1), order[0]];
        renderSlots();
        trocarModelo(order[0]);
    }

    /* ── the drag ────────────────────────────────────────────
       Only the card that was grabbed moves, and the window hears the
       gesture, so it cannot be lost off the edge of the block or picked
       up by a card the pointer passes over. A real press takes over from
       a scripted one. Past a little way the card is on a rubber band, so
       a long drag cannot carry it out of the block. */
    cardEls.forEach((el) => {
        const id = el.dataset.modeloId;
        el.addEventListener('pointerdown', (e) => {
            const front = order[0] === id;
            if (swapState.drag && e.isTrusted && !swapState.drag.real) {
                swapState.unhook();
                swapState.drag = null;
                settle();
            }
            if (!front || swapState.drag || e.button !== 0) return;

            swapState.drag = {
                id,
                real: e.isTrusted,
                pid: e.pointerId,
                x: e.clientX,
                y: e.clientY,
                dx: 0,
                dy: 0,
                t: performance.now(),
            };
            el.style.transition = 'none';

            const rub = (d) => 160 * Math.tanh(d / 160);
            const mine = (ev) =>
                !!swapState.drag &&
                ev.pointerId === swapState.drag.pid &&
                ev.isTrusted === swapState.drag.real;

            const mv = (ev) => {
                if (!mine(ev) || !swapState.drag) return;
                const d = swapState.drag;
                d.dx = ev.clientX - d.x;
                d.dy = ev.clientY - d.y;
                const x = rub(d.dx);
                const y = rub(d.dy);
                el.style.transform = `${slot(0)} translate(${x.toFixed(1)}px, ${y.toFixed(1)}px) rotate(${(x * 0.05).toFixed(2)}deg)`;
            };

            const up = (ev) => {
                if (!mine(ev) || !swapState.drag) return;
                const d = swapState.drag;
                swapState.drag = null;
                swapState.unhook();
                const far = Math.hypot(d.dx, d.dy);
                const quick = far / Math.max(1, performance.now() - d.t) > 0.6;
                /* a press, or a drag far or quick enough: to the back */
                if (ev.type !== 'pointercancel' && (far < 6 || far > 70 || (quick && far > 24))) {
                    swap();
                    return;
                }
                /* not far enough: it springs back into the front slot */
                settle();
            };

            window.addEventListener('pointermove', mv);
            window.addEventListener('pointerup', up);
            window.addEventListener('pointercancel', up);
            swapState.unhook = () => {
                window.removeEventListener('pointermove', mv);
                window.removeEventListener('pointerup', up);
                window.removeEventListener('pointercancel', up);
                swapState.unhook = () => {};
            };
        });
    });

    if (cswRoot) {
        cswRoot.addEventListener('pointerenter', () => { swapState.hover = true; });
        cswRoot.addEventListener('pointerleave', () => { swapState.hover = false; });
    }

    /* the timer: one swap every few seconds, unless a hand is on it */
    if (AUTO_SWAP) {
        window.setInterval(() => {
            if (!swapState.hover && !swapState.drag && !document.hidden) swap();
        }, Math.max(1.5, AUTO_EVERY) * 1000);
    }

    girar.addEventListener('click', async () => {
        if (girar.disabled) return;
        girar.disabled = true;
        atualizarDownload();
        girar.textContent = 'Girando…';
        if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            await new Promise(resolve => setTimeout(resolve, 500));
        }
        atributos = Object.fromEntries(camposAtributos.map(campo => {
            const valor = Math.floor(Math.random() * 99) + 1;
            campo.value = valor;
            return [campo.dataset.atributo, valor];
        }));
        girar.disabled = false;
        girar.textContent = 'Girar novamente';
        const geral = geralAtual();
        desenhar();
        atualizarDownload();
    });

    function centralizar() {
        zoom.value = enquadramento.zoom;
        x.value = enquadramento.x;
        y.value = enquadramento.y;
        desenhar();
    }

    window.editorCard = {
        limpar() {
            pessoa = null;
            ajustes.disabled = baixar.disabled = true;
            enquadramento = {zoom: 1, x: 0, y: 0};
            status.textContent = 'Envie uma foto para começar.';
            centralizar();
        },
        async carregar(src) {
            const imagem = new Image();
            imagem.src = src;
            await imagem.decode();
            status.textContent = 'Procurando rosto e ombros para enquadrar a pessoa…';
            let automatico = false;
            enquadramento = {
                zoom: Math.min(.94, modelo.foto_altura * .94 * imagem.width / (imagem.height * modelo.foto_largura)),
                x: 0, y: modelo.foto_altura * .03,
            };
            try {
                const {detectarPose, calcularEnquadramento} = await import('/js/enquadramento.js');
                const poses = await detectarPose(imagem);
                enquadramento = calcularEnquadramento(imagem.width, imagem.height, modelo, poses);
                automatico = enquadramento.automatico;
            } catch (erro) {
                // Falha de rede ou detecção não impede baixar e ajustar o recorte.
            }
            pessoa = imagem;
            ajustes.disabled = false;
            atualizarDownload();
            centralizar();
            status.textContent = automatico
                ? 'Enquadramento automático aplicado. Confira cabelo e braços; ajuste se necessário.'
                : 'Enquadramento básico aplicado. A detecção não foi conclusiva ou está indisponível; ajuste manualmente.';
        }
    };

    [posicao, zoom, x, y].forEach(campo => {
        campo.addEventListener('input', desenhar);
        campo.addEventListener('change', desenhar);
    });
    document.getElementById('card-reiniciar').addEventListener('click', centralizar);

    canvas.addEventListener('pointerdown', evento => {
        if (!pessoa) return;
        arrasto = {x: evento.clientX, y: evento.clientY, anteriorX: Number(x.value), anteriorY: Number(y.value)};
        canvas.setPointerCapture(evento.pointerId);
    });

    canvas.addEventListener('pointermove', evento => {
        if (!arrasto) return;
        const fator = 370 / canvas.getBoundingClientRect().width;
        x.value = arrasto.anteriorX + (evento.clientX - arrasto.x) * fator;
        y.value = arrasto.anteriorY + (evento.clientY - arrasto.y) * fator;
        desenhar();
    });

    ['pointerup', 'pointercancel', 'lostpointercapture'].forEach(tipo =>
        canvas.addEventListener(tipo, () => { arrasto = null; })
    );

    baixar.addEventListener('click', () => {
        if (!pessoa || !fundo || girar.disabled) return;
        const revisaoExportada = revisao;
        canvas.toBlob(blob => {
            if (!blob) {
                status.textContent = 'Não foi possível gerar o PNG.';
                return;
            }
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `meu-card-${selecionado.id}.png`;
            document.body.append(link);
            link.click();
            link.remove();
            setTimeout(() => URL.revokeObjectURL(url), 1000);
            if (revisao === revisaoExportada) alterado = false;
            status.textContent = 'Card gerado em PNG.';
        }, 'image/png');
    });


    document.getElementById('modelo-anterior').addEventListener('click', () => {
        settle(); order = [order.at(-1), ...order.slice(0,-1)]; renderSlots(); trocarModelo(order[0]);
    });
    document.getElementById('modelo-proximo').addEventListener('click', swap);
    new ResizeObserver(() => {
        const escala = Math.min(1, cswRoot.clientWidth / 650);
        document.getElementById('csw-stage').style.transform = `scale(${escala})`;
        cswRoot.style.height = `${410 * escala}px`;
    }).observe(cswRoot);
    document.querySelectorAll('[data-campo]').forEach(botao => botao.addEventListener('click', () => {
        const campo = document.getElementById(botao.dataset.campo);
        campo.value = Number(campo.value) + Number(botao.dataset.passo);
        campo.dispatchEvent(new Event('input', {bubbles:true}));
    }));
    window.addEventListener('beforeunload', evento => {
        if (alterado) { evento.preventDefault(); evento.returnValue = ''; }
    });
    renderSlots();
    atualizarAtributos();
    trocarModelo(order[0] || selecionado.id);
})();