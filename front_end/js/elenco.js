// Comportamentos de elenco.html.
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
