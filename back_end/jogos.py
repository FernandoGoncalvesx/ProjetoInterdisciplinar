"""API-Football para MySQL. Execute com python -m back_end.jogos --help."""

import argparse
import json
import os
import re
import time
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import mysql.connector
from dotenv import load_dotenv

from back_end.models.banco import PASTA_PROJETO, conectar_banco

FUSO = timezone(timedelta(hours=-3))
COLUNAS = {
    "api_fixture_id": "BIGINT UNSIGNED NULL UNIQUE",
    "mandante": "VARCHAR(100) NULL",
    "visitante": "VARCHAR(100) NULL",
    "competicao": "VARCHAR(150) NULL",
    "placar_mandante": "SMALLINT UNSIGNED NULL",
    "placar_visitante": "SMALLINT UNSIGNED NULL",
    "situacao": "VARCHAR(8) NULL",
    "minuto": "SMALLINT UNSIGNED NULL",
    "atualizado_em": "DATETIME NULL",
}


def consultar_api(endpoint, parametros):
    load_dotenv(PASTA_PROJETO / ".env")
    chave = os.getenv("API_FOOTBALL_KEY", "").strip()
    if not chave:
        raise ValueError("Preencha API_FOOTBALL_KEY no .env. Use uma chave direta da API-Sports.")
    url = "https://v3.football.api-sports.io/" + endpoint + "?" + urlencode(parametros)
    requisicao = Request(url, headers={"x-apisports-key": chave, "Accept": "application/json"})
    try:
        with urlopen(requisicao, timeout=20) as resposta:
            dados = json.load(resposta)
    except HTTPError as erro:
        raise ValueError(f"API-Football retornou HTTP {erro.code}. Confira chave, plano e quota.") from None
    except (URLError, TimeoutError, OSError, ValueError):
        raise ValueError("Não foi possível obter JSON da API-Football. Tente novamente mais tarde.") from None
    if not isinstance(dados, dict) or not isinstance(dados.get("response"), list):
        raise ValueError("A API-Football retornou um formato inesperado.")
    if dados.get("errors"):
        # Traduz erros conhecidos sem imprimir dados da conta ou a chave.
        erros = dados["errors"]
        if isinstance(erros, dict) and "plan" in erros:
            anos = re.search(r"try from (\d{4}) to (\d{4})", str(erros["plan"]))
            if anos:
                raise ValueError(
                    f"Seu plano permite temporadas de {anos[1]} a {anos[2]}, "
                    "mas não a temporada consultada. Para dados históricos, ajuste "
                    "API_FOOTBALL_SEASON no .env. Para jogos atuais, use um plano ou fonte com essa cobertura."
                )
            raise ValueError("Seu plano não permite esta consulta. Confira a cobertura no painel da API-Football.")
        if isinstance(erros, dict) and "requests" in erros:
            raise ValueError("Limite de consultas da API atingido. Aguarde a renovação da quota no painel.")
        raise ValueError("A API recusou a consulta. Confira equipe, temporada permitida, chave e quota no painel.")
    if dados.get("paging", {}).get("total", 1) > 1:
        raise ValueError("A resposta possui várias páginas. Reduza o período consultado antes de sincronizar.")
    return dados["response"]


def preparar_banco():
    """Adiciona apenas campos ausentes; mantém IDs, registros e relacionamentos."""
    with conectar_banco() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("SHOW COLUMNS FROM proximos_jogos")
            existentes = {linha[0] for linha in cursor.fetchall()}
            for coluna, definicao in COLUNAS.items():
                if coluna not in existentes:
                    cursor.execute(f"ALTER TABLE proximos_jogos ADD COLUMN {coluna} {definicao}")
        conexao.commit()


def transformar_partida(partida, equipe_id):
    fixture, times = partida["fixture"], partida["teams"]
    casa, fora = times["home"], times["away"]
    if equipe_id not in (casa["id"], fora["id"]):
        raise ValueError("A API retornou uma partida que não pertence à equipe configurada.")
    data = datetime.fromisoformat(fixture["date"].replace("Z", "+00:00"))
    if data.tzinfo is None:
        raise ValueError("A API retornou uma data sem fuso horário.")
    return (
        int(fixture["id"]),
        fora["name"] if casa["id"] == equipe_id else casa["name"],
        fixture.get("venue", {}).get("name"),
        data.astimezone(FUSO).replace(tzinfo=None),
        casa["name"], fora["name"], partida["league"]["name"],
        partida["goals"]["home"], partida["goals"]["away"],
        fixture["status"]["short"], fixture["status"].get("elapsed"),
    )


def sincronizar(so_hoje=False):
    load_dotenv(PASTA_PROJETO / ".env")
    try:
        equipe = int(os.getenv("API_FOOTBALL_TEAM_ID", ""))
        temporada = int(os.getenv("API_FOOTBALL_SEASON", ""))
        if equipe <= 0 or not 1900 <= temporada <= 2200:
            raise ValueError
    except ValueError:
        raise ValueError("Preencha API_FOOTBALL_TEAM_ID e API_FOOTBALL_SEASON com números válidos no .env.") from None
    parametros = {"team": equipe, "season": temporada, "timezone": "America/Sao_Paulo"}
    if so_hoje:
        parametros["date"] = datetime.now(FUSO).date().isoformat()
    partidas = consultar_api("fixtures", parametros)
    try:
        linhas = [transformar_partida(p, equipe) for p in partidas]
    except (KeyError, TypeError, AttributeError):
        raise ValueError("Partida incompleta recebida da API. Nenhum registro foi salvo.") from None
    if not linhas:
        return 0
    # executemany + commit mantém a atualização do lote em uma transação.
    sql = """INSERT INTO proximos_jogos
        (api_fixture_id, time_oponente, estadio, data, mandante, visitante, competicao,
         placar_mandante, placar_visitante, situacao, minuto, atualizado_em)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) AS novos
        ON DUPLICATE KEY UPDATE time_oponente=novos.time_oponente, estadio=novos.estadio,
        data=novos.data, mandante=novos.mandante, visitante=novos.visitante,
        competicao=novos.competicao, placar_mandante=novos.placar_mandante,
        placar_visitante=novos.placar_visitante, situacao=novos.situacao,
        minuto=novos.minuto, atualizado_em=novos.atualizado_em"""
    atualizado = datetime.now(FUSO).replace(tzinfo=None)
    valores = [(*linha, atualizado) for linha in linhas]
    with conectar_banco() as conexao:
        try:
            with conexao.cursor() as cursor:
                cursor.executemany(sql, valores)
            conexao.commit()
        except mysql.connector.Error:
            conexao.rollback()
            raise
    return len(linhas)


def listar_jogos():
    """Lê somente o banco; nenhuma chamada externa ocorre ao abrir a página."""
    with conectar_banco() as conexao:
        with conexao.cursor(dictionary=True) as cursor:
            agora = datetime.now(FUSO).replace(tzinfo=None)
            cursor.execute("""SELECT * FROM proximos_jogos
                WHERE data >= %s ORDER BY data LIMIT 50""",
                (agora,))
            futuros = cursor.fetchall()
            cursor.execute("""SELECT * FROM proximos_jogos
                WHERE data < %s ORDER BY data DESC LIMIT 50""", (agora,))
            return futuros + cursor.fetchall()


def agrupar_jogos(partidas):
    agora = datetime.now(FUSO).replace(tzinfo=None)
    hoje = agora.replace(hour=0, minute=0, second=0, microsecond=0)
    encerrados = {"FT", "AET", "PEN", "CANC", "ABD", "AWD", "WO"}
    ao_vivo = {"1H", "HT", "2H", "ET", "BT", "P", "LIVE", "INT", "SUSP"}
    grupos = {"proximos": [], "historico": []}
    for partida in partidas:
        situacao = partida.get("situacao")
        atual = partida["data"] >= agora or (situacao in ao_vivo and partida["data"] >= hoje)
        destino = "proximos" if atual and situacao not in encerrados else "historico"
        grupos[destino].append(partida)
    grupos["proximos"].sort(key=lambda jogo: jogo["data"])
    grupos["historico"].sort(key=lambda jogo: jogo["data"], reverse=True)
    return grupos


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    comandos = parser.add_subparsers(dest="comando", required=True)
    comandos.add_parser("preparar-banco", help="Acrescenta campos da API sem apagar dados")
    busca = comandos.add_parser("buscar-equipes", help="Lista IDs para confirmar a equipe feminina correta")
    busca.add_argument("nome")
    sync = comandos.add_parser("sincronizar", help="Busca e salva partidas da equipe e temporada do .env")
    sync.add_argument("--hoje", action="store_true", help="Busca somente os jogos de hoje")
    sync.add_argument("--ciclos", type=int, default=1, help="Número de consultas (1 a 60)")
    sync.add_argument("--intervalo", type=int, default=120, help="Segundos entre consultas, mínimo 120")
    args = parser.parse_args()
    if args.comando == "sincronizar" and (not 1 <= args.ciclos <= 60 or args.intervalo < 120):
        parser.error("Use de 1 a 60 ciclos e intervalo mínimo de 120 segundos.")
    try:
        if args.comando == "preparar-banco":
            preparar_banco()
            print("Banco preparado. Dados existentes preservados.")
        elif args.comando == "buscar-equipes":
            for item in consultar_api("teams", {"search": args.nome}):
                equipe = item["team"]
                print(f"{equipe['id']} | {equipe['name']} | {equipe['country']} | seleção: {equipe['national']}")
        else:
            for ciclo in range(args.ciclos):
                if ciclo:
                    time.sleep(args.intervalo)
                print(f"Consulta {ciclo + 1}/{args.ciclos}: {sincronizar(args.hoje)} partida(s) recebida(s).", flush=True)
    except ValueError as erro:
        parser.exit(1, f"{erro}\n")
    except mysql.connector.Error as erro:
        parser.exit(1, f"Erro MySQL ({erro.errno}). Confira o .env e execute preparar-banco após criar o schema.\n")


if __name__ == "__main__":
    main()
