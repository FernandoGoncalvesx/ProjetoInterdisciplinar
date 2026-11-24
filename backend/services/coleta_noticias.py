
import hashlib
import logging
import mimetypes
from pathlib import Path

from backend.models.noticia import salvar_se_nova

from playwright.sync_api import Error as PlaywrightError, sync_playwright


logger = logging.getLogger(__name__)
PASTA_IMAGENS = Path(__file__).resolve().parents[2] / "frontend" / "assets" / "noticias"

#Baixa a imagem extraída da notícia e a salva internamente
def _baixar_imagem(page, imagem_url):
    if not imagem_url:
        return None

    try:
        resposta = page.context.request.get(imagem_url)
    except PlaywrightError as erro:
        logger.warning("Falha ao baixar imagem %s: %s", imagem_url, erro)
        return None

    if not resposta.ok:
        logger.warning("Falha ao baixar imagem %s: HTTP %s", imagem_url, resposta.status)
        return None

    tipo_conteudo = resposta.headers.get("content-type", "").split(";", 1)[0].lower()
    if not tipo_conteudo.startswith("image/"):
        logger.warning(
            "Resposta da imagem %s não é uma imagem: %s",
            imagem_url,
            tipo_conteudo or "tipo desconhecido",
        )
        return None

    extensao = mimetypes.guess_extension(tipo_conteudo) or ".img"
    nome_arquivo = hashlib.sha256(imagem_url.encode("utf-8")).hexdigest()[:20] + extensao
    pasta_assets = PASTA_IMAGENS
    pasta_assets.mkdir(parents=True, exist_ok=True)
    (pasta_assets / nome_arquivo).write_bytes(resposta.body())

    return f"/assets/noticias/{nome_arquivo}"


def crawler_noticias ():
    #Seta os valores padrões para a busca inicial de links das notícias
    url_noticias = 'https://www.cbf.com.br/selecao-brasileira/noticias/selecao-feminina-principal'
    pref_links = '/selecao-brasileira/noticias/selecao-feminina-principal/a'
    seletor_links = f'a[href^="{pref_links}"]'

    with sync_playwright() as playwright:
        #Lança o navegador em modo headless
        browser = playwright.chromium.launch(headless=True)
        try:
            #Recupera todos os links de notícias da página inicial
            page = browser.new_page()
            page.goto(url_noticias, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_selector(seletor_links, timeout=15000)
            links = page.locator(seletor_links).evaluate_all(
                "(elementos) => [...new Set(elementos.map(a => a.getAttribute('href')))]"
            )

            #Percorre cada link para extrais os dados da notícia, como título, autor, imagem e texto
            for link in links:
                page.goto("https://www.cbf.com.br" + link, wait_until="domcontentloaded", timeout=30000)

                page.wait_for_selector('h1', timeout=15000)
                titulo = page.locator('h1').evaluate_all(
                            "(elementos) => [...new Set(elementos.map(a => a.textContent))]"
                        )[0].strip()

                page.wait_for_selector('div[class*="body-content-article"] > p:not(:has(img))', timeout=15000)
                textos = page.locator('div[class*="body-content-article"] > p:not(:has(img))').evaluate_all(
                    "(elementos) => [...new Set(elementos.map(a => a.textContent))]"
                )
                texto_noticia = "\n\n".join(texto.strip() for texto in textos)

                imagem_locator = page.locator(
                    'div[class *="styles_cover"] > img'
                ).first
                imagem_url = None
                if imagem_locator.count():
                    imagem_original_url = imagem_locator.evaluate(
                        "(imagem) => imagem.currentSrc || imagem.src"
                    )
                    imagem_url = _baixar_imagem(page, imagem_original_url)

                page.wait_for_selector('div[class*="authorContainer"]', timeout=15000)
                autor = page.locator('div[class*="authorContainer"]').evaluate_all(
                    "(elementos) => [...new Set(elementos.map(a => a.textContent))]"
                )[0].strip()

                salvar_se_nova(titulo, autor, imagem_url, texto_noticia)
        finally:
            browser.close()
        return {"mensagem": "Crawler finalizado e notícias salvas no banco de dados."}


if __name__ == "__main__":
    print(crawler_noticias()["mensagem"])
