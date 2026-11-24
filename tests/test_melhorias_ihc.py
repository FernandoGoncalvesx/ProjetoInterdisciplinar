import unittest
from unittest.mock import patch

from backend import app as servidor
from backend.controllers import jogos_controller


class MelhoriasTest(unittest.TestCase):
    def test_historico_limita_seis_cartoes_iniciais(self):
        from datetime import datetime, timedelta
        jogos = [dict(data=datetime.now()-timedelta(days=n+2), mandante='Brasil', visitante='Time',time_oponente='Time',situacao='FT',placar_mandante=1,placar_visitante=0,minuto=None,atualizado_em=None) for n in range(10)]
        with patch.object(jogos_controller, 'listar_jogos', return_value=jogos):
            html = servidor.app.test_client().get('/Telas/proximos_jogos.html').get_data(as_text=True)
        self.assertIn('Ver mais 4 resultados', html)
        self.assertEqual(html.split('<details class="historico-extra">')[0].count('<article class="card">'), 6)
