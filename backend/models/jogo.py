from datetime import datetime, timedelta, timezone
from backend.models.banco import conectar_banco

FUSO = timezone(timedelta(hours=-3))


def listar_jogos():
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
