document.documentElement.classList.add('js');
const menuButton = document.querySelector('.menu-botao');
const menu = document.querySelector('.menu');
if (menuButton && menu) {
    function setMenu(open) {
        menu.classList.toggle('aberto', open);
        menuButton.setAttribute('aria-expanded', String(open));
        menuButton.querySelector('.sr-only').textContent = open ? 'Fechar menu' : 'Abrir menu';
    }
    menuButton.addEventListener('click', () => setMenu(!menu.classList.contains('aberto')));
    menu.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            setMenu(false);
            menuButton.focus();
        }
    });
    document.addEventListener('click', (event) => {
        if (!event.target.closest('.barra-navegacao')) setMenu(false);
    });
    window.matchMedia('(max-width: 1100px)').addEventListener('change', () => setMenu(false));
}
document.querySelectorAll('[data-ano]').forEach((element) => {
    element.textContent = new Date().getFullYear();
});
