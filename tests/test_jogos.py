import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from backend import app as servidor
from backend.models import jogo as jogos
from backend.controllers import jogos_controller
from database.migracoes import jogos as migracao


class JogosTest(unittest.TestCase):
    def setUp(self):
        self.conexao = MagicMock()
        self.conexao.__enter__.return_value = self.conexao
        self.cursor = self.conexao.cursor.return_value.__enter__.return_value
        conexao = patch.object(jogos, "conectar_banco", return_value=self.conexao)
        conexao.start()
        self.addCleanup(conexao.stop)
        conexao_migracao = patch.object(migracao, "conectar_banco", return_value=self.conexao)
        conexao_migracao.start()
        self.addCleanup(conexao_migracao.stop)

    def test_migracao_idempotente(self):
        self.cursor.fetchall.return_value = [(nome,) for nome in migracao.COLUNAS]
        migracao.preparar_banco()
        self.assertEqual(self.cursor.execute.call_count, 1)
        self.cursor.fetchall.return_value = [(nome,) for nome in migracao.COLUNAS if nome != "minuto"]
        self.cursor.execute.reset_mock()
        migracao.preparar_banco()
        self.assertEqual(self.cursor.execute.call_count, 2)
        self.assertIn("ADD COLUMN minuto", self.cursor.execute.call_args.args[0])

    def test_pagina_mostra_zero_e_escapa_html(self):
        jogo = dict(data=datetime(2024, 11, 4, 19), time_oponente='Canadá',
                    mandante='Brasil', visitante='Canadá', situacao='FT',
                    placar_mandante=0, placar_visitante=0, competicao='<script>alert(1)</script>')
        with patch.object(jogos_controller, 'listar_jogos', return_value=[jogo]):
            resposta = servidor.app.test_client().get('/Telas/proximos_jogos.html')
        html = resposta.get_data(as_text=True)
        self.assertEqual(resposta.status_code, 200)
        self.assertIn('Placar: 0 × 0', html)
        self.assertNotIn('<script>alert(1)</script>', html)

    def test_jogos_antigos_nao_aparecem_como_proximos(self):
        agora = datetime.now(jogos.FUSO).replace(tzinfo=None)
        antigo = {'data': datetime(2024, 5, 1), 'situacao': 'FT'}
        futuro = {'data': agora + timedelta(days=1), 'situacao': 'NS'}
        cancelado = {'data': agora + timedelta(days=2), 'situacao': 'CANC'}
        grupos = jogos.agrupar_jogos([antigo, futuro, cancelado])
        self.assertEqual(grupos['proximos'], [futuro])
        self.assertIn(antigo, grupos['historico'])
        self.assertIn(cancelado, grupos['historico'])

    def test_consulta_inclui_historico_antigo(self):
        self.cursor.fetchall.side_effect = [[{'id': 1}], [{'id': 2}]]
        self.assertEqual(jogos.listar_jogos(), [{'id': 1}, {'id': 2}])
        consultas = [chamada.args[0] for chamada in self.cursor.execute.call_args_list]
        self.assertIn('WHERE data >=', consultas[0])
        self.assertIn('WHERE data <', consultas[1])


if __name__ == '__main__':
    unittest.main()
