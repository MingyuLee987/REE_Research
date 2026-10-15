import tempfile
import unittest
from unittest.mock import Mock, patch
from ree_research.mining import fetch_elsevier


class RetrievalTests(unittest.TestCase):
    @patch('ree_research.mining.load_dotenv')
    @patch('ree_research.mining.requests.get')
    @patch.dict('os.environ', {'ELSEVIER_API_KEY': ' test-key ', 'ELSEVIER_INST_TOKEN': ' institution-token '})
    def test_institution_token_forwarded_and_never_saved(self, get, load):
        get.return_value = Mock(status_code=200, content=b'<article><originalText>institution-token test-key</originalText></article>')
        with tempfile.TemporaryDirectory() as directory:
            fetch_elsevier('10.1000/test', directory)
            headers = get.call_args.kwargs['headers']
            self.assertEqual(headers['X-ELS-APIKey'], 'test-key')
            self.assertEqual(headers['X-ELS-Insttoken'], 'institution-token')
            self.assertNotIn('Authorization', headers)
            from pathlib import Path
            for path in Path(directory).iterdir():
                self.assertNotIn('institution-token', path.read_text())
                self.assertNotIn('test-key', path.read_text())

    @patch('ree_research.mining.load_dotenv')
    @patch('ree_research.mining.requests.get')
    @patch.dict('os.environ', {'ELSEVIER_API_KEY': 'test-key'})
    def test_configuration_error_is_actionable_and_redacted(self, get, load):
        get.return_value = Mock(status_code=403, content=b'<service-error><status><statusCode>AUTHENTICATION_ERROR</statusCode><statusText>Requestor configuration settings insufficient: test-key</statusText></status></service-error>')
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(RuntimeError) as raised:
                fetch_elsevier('10.1000/test', directory)
            self.assertIn('configuration settings insufficient', str(raised.exception))
            self.assertNotIn('test-key', str(raised.exception))

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
