const fecharAviso = document.getElementById('fechar-aviso-login');
if (fecharAviso) {
    fecharAviso.hidden = false;
    fecharAviso.addEventListener('click', () => {
        document.getElementById('aviso-login-card').hidden = true;
        document.getElementById('conteudo').focus();
    });
}
