import tempfile
import unittest
from unittest.mock import Mock, patch
from ree_research.mining import fetch_elsevier


class RetrievalTests(unittest.TestCase):
    @patch('ree_research.mining.requests.get')
    @patch.dict('os.environ', {'ELSEVIER_API_KEY': 'test-key'})
    def test_forbidden_is_not_full_text(self, get):
        get.return_value = Mock(status_code=403)
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RuntimeError, '403'):
                fetch_elsevier('10.1000/test', directory)

    @patch('ree_research.mining.requests.get')
    @patch.dict('os.environ', {'ELSEVIER_API_KEY': 'test-key'})
    def test_metadata_response_is_not_full_text(self, get):
        get.return_value = Mock(status_code=200, content=b'<article><coredata><title>Test</title></coredata></article>')
        with tempfile.TemporaryDirectory() as directory:
            result = fetch_elsevier('10.1000/test', directory)
            self.assertEqual(result['status'], 'metadata_only')
            self.assertEqual(result['measurement_status'], 'not_extracted')
