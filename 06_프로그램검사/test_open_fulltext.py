import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
from ree_research.open_fulltext import fetch_elsevier_open_copy


class OpenCopyTests(unittest.TestCase):
    def responses(self, xml):
        search=Mock()
        search.json.return_value={'resultList':{'result':[{'doi':'10.1016/test',
            'pmcid':'PMC123','isOpenAccess':'Y','title':'Test article'}]}}
        full=Mock(content=xml)
        return [search,full]

    @patch('ree_research.open_fulltext.requests.get')
    @patch('ree_research.open_fulltext.fetch_elsevier',side_effect=RuntimeError('HTTP 403'))
    def test_reads_real_body_and_records_api_failure_without_forwarding_credentials(self, api, get):
        get.side_effect=self.responses(b'<article><front><article-meta><article-id pub-id-type="doi">10.1016/test</article-id></article-meta></front><body><p>Measured source text</p><table-wrap id="T1"><p>table values</p></table-wrap></body></article>')
        with tempfile.TemporaryDirectory() as directory:
            result=fetch_elsevier_open_copy('10.1016/test',directory)
            self.assertFalse(result['publisher_api_fixed'])
            self.assertEqual(result['table_blocks'],1)
            self.assertIn('403',result['publisher_api_status'])
            blocks=json.loads((Path(directory)/'blocks.json').read_text())
            self.assertEqual(len(blocks),2)  # table paragraphs are not duplicated
            for call in get.call_args_list:
                self.assertNotIn('headers',call.kwargs)

    @patch('ree_research.open_fulltext.requests.get')
    @patch('ree_research.open_fulltext.fetch_elsevier',side_effect=RuntimeError('HTTP 403'))
    def test_wrong_doi_in_repository_xml_is_rejected(self, api, get):
        get.side_effect=self.responses(b'<article><front><article-meta><article-id pub-id-type="doi">10.1016/different</article-id></article-meta></front><body><p>Wrong paper</p></body></article>')
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError,'DOI mismatch'):
                fetch_elsevier_open_copy('10.1016/test',directory)
            self.assertFalse((Path(directory)/'article.xml').exists())


if __name__=='__main__':unittest.main()
