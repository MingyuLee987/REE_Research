import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
import json
import pandas as pd
from ree_research.model_selection import CoverageTransformer, compare
from ree_research.schema import prepare
from ree_research.cli import demo
from ree_research.extraction import extract, quote_matches, resolve_locators


class PilotTests(unittest.TestCase):
    def test_evidence_fragments_cannot_invent_numbers(self):
        self.assertTrue(quote_matches('Header\nSample2 1.23', 'Header Sample1 2.34 Sample2 1.23'))
        self.assertFalse(quote_matches('Header\nSample2 9.99', 'Header Sample1 2.34 Sample2 1.23'))
        self.assertEqual(resolve_locators('p:21; p:8, methods', {'p:2': '', 'p:21': '', 'p:8': ''}), ['p:21','p:8'])
    def test_feature_coverage_uses_fit_data_only(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'demo.csv'
            demo(path)
            data=prepare(pd.read_csv(path))
            data.loc[:19,'Mo']=float('nan')
            fitted=CoverageTransformer().fit(data.iloc[:20])
            self.assertNotIn('Mo',fitted.numeric_)
            self.assertEqual(fitted.transform(data.iloc[20:22]).shape[0],2)

    def test_insufficient_rows_cannot_be_padded(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'demo.csv'
            demo(path)
            with self.assertRaisesRegex(ValueError,'Need 200'):
                compare(path,Path(temp)/'out',rows=200,allow_synthetic=True)

    @patch('ree_research.extraction.requests.post')
    @patch.dict('os.environ',{'OPENAI_API_KEY':'test-key','OPENAI_MODEL':'gpt-6.1-sol'})
    def test_quota_failure_creates_no_measurements(self,post):
        post.return_value=Mock(status_code=429)
        post.return_value.json.return_value={'error':{'code':'credit_balance_exhausted'}}
        with tempfile.TemporaryDirectory() as temp:
            source=Path(temp)/'source'
            source.mkdir()
            (source/'blocks.json').write_text('[]')
            (source/'metadata.json').write_text(json.dumps({'doi':'10.1000/test'}))
            out=Path(temp)/'out'
            with self.assertRaisesRegex(RuntimeError,'credit_balance_exhausted'):
                extract(source,out)
            self.assertFalse((out/'pending_measurements.csv').exists())
