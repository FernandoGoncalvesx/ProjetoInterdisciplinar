"""Notícias da versão de teste: leitura limpa e cache local."""
from datetime import datetime
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from hashlib import sha256
import re
import unicodedata
import json
import logging
from pathlib import Path
from threading import Lock, Thread
from time import time
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET
from back_end.jogos import FUSO
from back_end.noticias import FEED_URL, filtrar_futebol

CACHE = Path(__file__).resolve().parent / 'cache' / 'noticias-teste.json'


def identificar_noticia(noticia):
    noticia = dict(noticia)
    texto = noticia['titulo'] + ' ' + ' '.join(noticia.get('categorias', []))
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode().lower()
    assuntos = []
    if re.search(r'\bsub[ -]?\d{2}\b', texto):
        assuntos.append('base')
    if assuntos or 'selecao' in texto:
        assuntos.append('selecoes')
    if 'premio' in texto or 'premiacao' in texto:
        assuntos.append('premiacoes')
    if not assuntos:
        assuntos.append('clubes')
    noticia.update(id='noticia-' + sha256(noticia['link'].encode()).hexdigest()[:16], assuntos=assuntos)
    return noticia


class Artigo(HTMLParser):
    def __init__(self):
        super().__init__()
        self.blocos = []
        self.partes = []
        self.pilha = []
        self.tipo = 'p'
        self.relacionadas = False

    def finalizar(self):
        texto = ' '.join(''.join(self.partes).split())
        self.partes = []
        if texto.lower().startswith('notícias relacionadas'):
            self.relacionadas = True
        elif texto:
            self.blocos.append({'tipo': self.tipo, 'texto': texto})

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        oculto = tag in {'script', 'style', 'noscript'} or (tag == 'ul' and self.relacionadas)
        oculto = oculto or (tag == 'a' and 'whatsapp.com' in attrs.get('href', '').lower())
        if tag in {'p', 'div', 'h2', 'h3', 'li', 'blockquote', 'br'}:
            self.finalizar()
            self.tipo = 'h3' if tag in {'h2', 'h3'} else 'p'
        if tag not in {'img', 'br', 'hr', 'input', 'meta', 'link', 'source', 'wbr'}:
            self.pilha.append((tag, oculto))

    def handle_endtag(self, tag):
        if tag in {'p', 'div', 'h2', 'h3', 'li', 'blockquote'}:
            self.finalizar()
            self.tipo = 'p'
        for i in range(len(self.pilha) - 1, -1, -1):
            if self.pilha[i][0] == tag:
                self.pilha = self.pilha[:i]
                break
        if tag == 'ul':
            self.relacionadas = False

    def handle_data(self, data):
        if not any(oculto for _, oculto in self.pilha):
            self.partes.append(data)


def ler_feed(xml):
    if ET.fromstring(xml).find('channel') is None:
        raise ValueError('Resposta não é um feed RSS')
    noticias = filtrar_futebol(xml)
    itens = {i.findtext('link', '').strip(): i for i in ET.fromstring(xml).findall('./channel/item')}
    for noticia in noticias:
        item = itens[noticia['link']]
        noticia['categorias'] = [c.text or '' for c in item.findall('category')]
        artigo = Artigo()
        artigo.feed(item.findtext('description', ''))
        artigo.finalizar()
        noticia['blocos'] = artigo.blocos
        texto = next((b['texto'] for b in artigo.blocos if b['tipo'] == 'p'), '')
        noticia['resumo'] = texto[:240] + ('…' if len(texto) > 240 else '')
        try:
            data = parsedate_to_datetime(item.findtext('pubDate', '')).astimezone(FUSO)
            noticia.update(data_iso=data.isoformat(), data=data.strftime('%d/%m/%Y às %H:%M'))
        except (ValueError, TypeError, OverflowError):
            noticia.update(data_iso='', data='Data não informada pela fonte')
    return noticias


class CacheNoticias:
    def __init__(self, caminho=CACHE):
        self.caminho = caminho
        self.lock = Lock()
        self.noticias = None
        self.atualizado = 0
        self.tentativa = 0
        self.carregando = False
        self.erro = False
        try:
            dados = json.loads(caminho.read_text(encoding='utf-8'))
            if isinstance(dados['noticias'], list) and isinstance(dados['atualizado'], (int, float)):
                self.noticias, self.atualizado = dados['noticias'], dados['atualizado']
        except (OSError, ValueError, KeyError, TypeError):
            pass

    def atualizar(self):
        try:
            with urlopen(Request(FEED_URL, headers={'User-Agent': 'Mozilla/5.0'}), timeout=8) as resposta:
                xml = resposta.read(2 * 1024 * 1024 + 1)
            if len(xml) > 2 * 1024 * 1024:
                raise ValueError('Feed muito grande')
            noticias = ler_feed(xml)
            atualizado = time()
            with self.lock:
                self.noticias, self.atualizado, self.erro = noticias, atualizado, False
            try:
                self.caminho.parent.mkdir(parents=True, exist_ok=True)
                temporario = self.caminho.with_suffix('.tmp')
                temporario.write_text(json.dumps({'noticias': noticias, 'atualizado': atualizado}, ensure_ascii=False), encoding='utf-8')
                temporario.replace(self.caminho)
            except OSError:
                logging.getLogger(__name__).warning('Não foi possível gravar o cache de notícias.')
        except (OSError, ValueError, ET.ParseError):
            with self.lock:
                self.erro = True
            logging.getLogger(__name__).warning('Atualização do RSS indisponível.', exc_info=True)
        finally:
            with self.lock:
                self.carregando = False

    def consultar(self, forcar=False):
        with self.lock:
            agora = time()
            if not self.carregando and agora - self.tentativa >= 10 and (forcar or agora - self.atualizado > 300):
                self.carregando, self.tentativa = True, agora
                Thread(target=self.atualizar, daemon=True).start()
            return {'noticias': self.noticias or [], 'disponivel': self.noticias is not None,
                    'carregando': self.carregando, 'erro': self.erro, 'versao': self.atualizado,
                    'atualizado': datetime.fromtimestamp(self.atualizado, FUSO).strftime('%d/%m/%Y às %H:%M') if self.atualizado else None}


cache_noticias = CacheNoticias()
