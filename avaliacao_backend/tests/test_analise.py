import csv
import json
import statistics
import tempfile
import unittest
from pathlib import Path

import pandas as pd
from backend import analise

class TestAnalise(unittest.TestCase):
    def fixture(self, frame):
        pasta = tempfile.TemporaryDirectory()
        self.addCleanup(pasta.cleanup)
        p = Path(pasta.name) / 'fixture.csv'
        frame.to_csv(p, index=False)
        return p

    def base(self):
        return pd.read_csv(analise.DEFAULT_CSV, dtype=str, encoding='utf-8-sig').iloc[:3].copy()

    def test_calculos_conferidos_sem_pandas(self):
        with analise.DEFAULT_CSV.open(encoding='utf-8-sig') as f:
            linhas = list(csv.DictReader(f))
        numeros = [float(r['minutos_atraso']) for r in linhas]
        d, q = analise.carregar()
        r = analise.resumo(d, q)
        self.assertEqual(q['registros_excluidos'], 0)
        self.assertEqual(len(numeros), 180)
        self.assertEqual(r['atraso_total_min_observacoes'], sum(numeros))
        self.assertEqual(r['atraso_medio_min'], round(statistics.mean(numeros), 4))
        self.assertEqual(r['atraso_mediano_min'], statistics.median(numeros))
        self.assertEqual(r['maior_atraso_min'], max(numeros))
        self.assertIsNone(r['viagens_completas'])
        json.dumps(r, allow_nan=False)

    def test_grupos_reconciliam_contagem_e_soma(self):
        d, _ = analise.carregar()
        for dim in analise.DIMENSOES:
            grupos = analise.agrupar(d, dim)
            self.assertEqual(sum(g['observacoes'] for g in grupos), 180)
            self.assertAlmostEqual(sum(g['atraso_total_min'] for g in grupos), 1362)

    def test_codigo_preserva_zeros(self):
        d, _ = analise.carregar()
        self.assertIn('001', d['codigo_linha'].tolist())

    def test_campos_invalidos_excluidos_sem_imputacao(self):
        frame = self.base()
        frame.loc[0, 'minutos_atraso'] = '-1'
        frame.loc[1, 'data_registro'] = 'data errada'
        frame.loc[2, 'cidade'] = '  '
        d, q = analise.carregar(self.fixture(frame))
        self.assertTrue(d.empty)
        self.assertEqual(q['registros_excluidos'], 3)
        self.assertEqual(q['linhas_csv_excluidas'], [2, 3, 4])
        r = analise.resumo(d, q)
        self.assertIsNone(r['atraso_medio_min'])
        self.assertIsNone(r['maior_atraso_min'])
        self.assertEqual(r['atraso_total_min_observacoes'], 0)
        json.dumps(r, allow_nan=False)

    def test_inf_nan_e_tempo_inconsistente(self):
        frame = self.base()
        frame.loc[0, 'tempo_real_min'] = 'inf'
        frame.loc[1, 'minutos_atraso'] = 'NaN'
        frame.loc[2, 'minutos_atraso'] = '100'
        d, q = analise.carregar(self.fixture(frame))
        self.assertEqual(q['registros_excluidos'], 3)
        self.assertTrue(d.empty)

    def test_duplicatas_sinalizadas_mantidas(self):
        frame = self.base().iloc[:1]
        frame = pd.concat([frame, frame], ignore_index=True)
        d, q = analise.carregar(self.fixture(frame))
        self.assertEqual(q['duplicatas_exatas_adicionais'], 1)
        self.assertEqual(len(d), 2)

    def test_coluna_ausente(self):
        with self.assertRaisesRegex(ValueError, 'minutos_atraso'):
            analise.carregar(self.fixture(self.base().drop(columns='minutos_atraso')))

    def test_csv_vazio_com_cabecalho(self):
        d, q = analise.carregar(self.fixture(self.base().iloc[:0]))
        self.assertEqual(q['registros_lidos'], 0)
        self.assertEqual(analise.agrupar(d, 'linha'), [])
        self.assertEqual(analise.maiores(d), [])
        self.assertIsNone(analise.resumo(d, q)['percentual_acima_10_min'])

    def test_todos_os_empates(self):
        d, _ = analise.carregar()
        r = analise.maiores(d)
        self.assertEqual(len(r), int((d['minutos_atraso'] == 12).sum()))
        self.assertTrue(all(x['minutos_atraso'] == 12 for x in r))

if __name__ == '__main__':
    unittest.main()
