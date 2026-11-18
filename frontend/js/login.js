const alternarSenha = document.getElementById("alternar-senha");
const campoSenha = document.getElementById("senha");

alternarSenha.hidden = false;
alternarSenha.addEventListener("click", () => {
    const mostrar = campoSenha.type === "password";
    campoSenha.type = mostrar ? "text" : "password";
    alternarSenha.setAttribute("aria-pressed", String(mostrar));
});
