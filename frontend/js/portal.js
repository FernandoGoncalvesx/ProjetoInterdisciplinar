// INICIAR RECURSOS DA PÁGINA
iniciarMenu();

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
