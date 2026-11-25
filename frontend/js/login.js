const alternarSenha = document.getElementById("alternar-senha");
const campoSenha = document.getElementById("senha");

if (alternarSenha && campoSenha) {
    alternarSenha.hidden = false;
    alternarSenha.addEventListener("click", () => {
        const mostrar = campoSenha.type === "password";
        campoSenha.type = mostrar ? "text" : "password";
        alternarSenha.textContent = mostrar ? "Ocultar senha" : "Mostrar senha";
        alternarSenha.setAttribute("aria-pressed", String(mostrar));
    });
}

const cadastro = document.getElementById("cadastro-form");
const campoCadastroSenha = document.getElementById("cadastro-senha");
const campoConfirmacao = document.getElementById("cadastro-confirmacao");
const alternarCadastroSenha = document.getElementById("alternar-cadastro-senha");
const statusCadastro = document.getElementById("cadastro-status");

if (alternarCadastroSenha && campoCadastroSenha && campoConfirmacao) {
    alternarCadastroSenha.hidden = false;
    alternarCadastroSenha.addEventListener("click", () => {
        const mostrar = campoCadastroSenha.type === "password";
        campoCadastroSenha.type = mostrar ? "text" : "password";
        campoConfirmacao.type = mostrar ? "text" : "password";
        alternarCadastroSenha.textContent = mostrar ? "Ocultar senhas" : "Mostrar senhas";
        alternarCadastroSenha.setAttribute("aria-pressed", String(mostrar));
    });
}

if (cadastro && campoCadastroSenha && campoConfirmacao && statusCadastro) {
    cadastro.addEventListener("submit", (evento) => {
        if (campoCadastroSenha.value !== campoConfirmacao.value) {
            evento.preventDefault();
            statusCadastro.textContent = "As duas senhas precisam ser iguais.";
            campoConfirmacao.setAttribute('aria-invalid', 'true');
            campoConfirmacao.focus();
        }
    });

    function validarConfirmacao() {
        const invalido = Boolean(campoConfirmacao.value && campoCadastroSenha.value !== campoConfirmacao.value);
        campoConfirmacao.setAttribute('aria-invalid', String(invalido));
        statusCadastro.textContent = invalido ? 'As duas senhas precisam ser iguais.' : '';
    }
    [campoCadastroSenha, campoConfirmacao].forEach(campo => campo.addEventListener('input', validarConfirmacao));
}
