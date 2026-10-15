import json
import tempfile
import unittest
from pathlib import Path
from ree_research.screening import normalize_doi, screen, priority


class ScreeningTests(unittest.TestCase):
    def test_doi_normalization(self):
        self.assertEqual(normalize_doi('https://doi.org/10.1000/ABC'), '10.1000/abc')
        self.assertEqual(normalize_doi('not-a-doi'), '')

    def test_dedup_preserves_source_and_does_not_verify(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for i, doi in enumerate(['https://doi.org/10.1000/ABC', '10.1000/abc', '10.1000/other']):
                payload = {'provider': 'springer-meta', 'query': f'query-{i}',
                           'response': {'records': [{'title': 'Same title', 'doi': doi}]}}
                (root / f'{i}.json').write_text(json.dumps(payload), encoding='utf-8')
            result = screen(root, root / 'out')
            self.assertEqual(result['records_seen'], 3)
            self.assertEqual(result['unique_papers'], 2)
            merged = next(p for p in result['papers'] if p['doi'] == '10.1000/abc')
            self.assertEqual(len(merged['sources']), 2)
            self.assertEqual(merged['screen_status'], 'pending_manual_review')
            self.assertEqual(merged['measurement_status'], 'not_extracted')

    def test_bulk_and_coating_are_distinguished(self):
        bulk, _ = priority('Cerium microalloying and corrosion of stainless steel', '')
        coating, flags = priority('Cerium coating for corrosion protection of steel', '')
        self.assertGreater(bulk, coating)
        self.assertTrue(flags['surface_or_inhibitor'])
