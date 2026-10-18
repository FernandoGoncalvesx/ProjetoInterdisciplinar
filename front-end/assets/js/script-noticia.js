function opennoticia(botao) {
    const card = botao.closest(".card");
    const dialog = document.getElementById("detalhes-noticia");

    document.getElementById("detalhes-titulo").textContent =
        card.querySelector(".card-title").textContent;
    document.getElementById("detalhes-resumo").textContent =
        card.querySelector(".card-text").textContent;

    dialog.showModal();
}