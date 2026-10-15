import tempfile
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
from ree_research.cli import demo
from ree_research.schema import prepare, FEATURES
from ree_research.benchmark import predictions, benchmark, selected_features


class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / 'demo.csv'
        demo(self.path)
        self.raw = pd.read_csv(self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_schema_and_unreviewed_rejection(self):
        frame = prepare(self.raw)
        self.assertEqual(len(FEATURES), 14)
        np.testing.assert_allclose(frame.target, np.log10(self.raw.icorr_A_cm2))
        self.raw.loc[0, 'review_status'] = 'pending'
        with self.assertRaises(ValueError):
            prepare(self.raw)

    def test_pool_labels_do_not_change_predictions_or_uncertainty(self):
        frame = prepare(self.raw)
        train, test, pool = frame.iloc[:24], frame.iloc[24:32], frame.iloc[32:40].copy()
        for name in ['ridge', 'svr', 'gpr']:
            pool = frame.iloc[32:40].copy()
            before = predictions(name, train, test, pool, 42, 3)
            pool['target'] = 999
            after = predictions(name, train, test, pool, 42, 3)
            for a, b in zip(before, after):
                np.testing.assert_allclose(a, b)

    def test_unreported_features_remain_missing_and_are_excluded(self):
        raw = self.raw.drop(columns=['Mo', 'pH', 'scan_rate_mV_s'])
        frame = prepare(raw)
        self.assertTrue(frame.Mo.isna().all())
        numeric, categorical = selected_features(frame.iloc[:20])
        self.assertNotIn('Mo', numeric)
        self.assertNotIn('pH', numeric)
        self.assertNotIn('scan_rate_mV_s', numeric)
        frame.loc[:9, 'Cr'] = np.nan
        self.assertNotIn('Cr', selected_features(frame.iloc[:20])[0])

    def test_grouped_split_and_budget(self):
        import json
        out = Path(self.tmp.name) / 'out'
        scores = benchmark(self.path, out, [11], initial=10, batch=3, budget=13, committee=2)
        manifest = json.loads((out / 'run.json').read_text())
        test_papers = set(manifest['splits'][0]['test_papers'])
        chosen = manifest['splits'][0]['initial_record_ids']
        for query in manifest['queries']:
            chosen += query['record_ids']
        train_papers = set(self.raw[self.raw.record_id.isin(chosen)].paper_id)
        self.assertFalse(test_papers & train_papers)
        self.assertEqual(set(scores.n_labeled), {10, 13})


if __name__ == '__main__':
    unittest.main()
