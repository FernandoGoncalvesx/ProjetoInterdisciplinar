import re
import unicodedata
from html.parser import HTMLParser
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET

FEED_URL = "https://agenciabrasil.ebc.com.br/rss/esportes/feed.xml"
# shortcut: termos editoriais podem omitir matérias sem identificação de futebol feminino;
# ampliar esta lista quando novas categorias aparecerem no feed.
TERMOS = re.compile(
    r"\b(futebol|brasileirao|campeonato brasileiro|copa do mundo|mundial feminino|"
    r"libertadores|copa do brasil|selecao brasileira|gol|gols|goleiro|goleira|"
    r"atacante|artilheira|artilheiro)\b|premio tv brasil petrobras para elas"
)
FEMININO = re.compile(r"\b(feminin[oa]s?|jogadoras?|goleiras?|artilheiras?)\b|premio tv brasil petrobras para elas")


class Texto(HTMLParser):
    def __init__(self):
        super().__init__()
        self.partes = []
        self.ocultos = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.ocultos += 1
        if tag in {"p", "div", "h2", "h3", "li", "br"}:
            self.partes.append("\n")

    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self.ocultos = max(0, self.ocultos - 1)
        if tag in {"p", "div", "h2", "h3", "li"}:
            self.partes.append("\n")

    def handle_data(self, data):
        if not self.ocultos:
            self.partes.append(data)


def filtrar_futebol(xml):
    noticias = []
    for item in ET.fromstring(xml).findall("./channel/item"):
        titulo = item.findtext("title", "").strip()
        categorias = " ".join(c.text or "" for c in item.findall("category"))
        assunto = unicodedata.normalize("NFKD", titulo + " " + categorias)
        assunto = assunto.encode("ascii", "ignore").decode().lower()
        if not (TERMOS.search(assunto) and FEMININO.search(assunto)):
            continue
        link = item.findtext("link", "").strip()
        destino = urlsplit(link)
        if destino.scheme != "https" or destino.hostname != "agenciabrasil.ebc.com.br":
            continue
        texto = Texto()
        texto.feed(item.findtext("description", ""))
        paragrafos = [" ".join(p.split()) for p in "".join(texto.partes).splitlines() if p.strip()]
        resumo = " ".join(" ".join(texto.partes).split())
        resumo = resumo.removeprefix("Notícias relacionadas:").strip()
        noticias.append({"titulo": titulo, "link": link,
                         "paragrafos": paragrafos,
                         "autor": item.findtext("{http://purl.org/dc/elements/1.1/}creator", "Agência Brasil"),
                         "resumo": resumo[:280] + ("…" if len(resumo) > 280 else "")})
    return noticias

