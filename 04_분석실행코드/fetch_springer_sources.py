"""Acquire selected Springer OA JATS sources, preserving API provenance."""
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import requests
from dotenv import load_dotenv
from collect_open_papers import evidence_blocks

ROOT = Path(__file__).resolve().parents[1]
DOIS = ['10.1038/s41529-026-00746-3', '10.1038/s41529-025-00682-8',
        '10.1038/s41598-018-23273-x', '10.1038/s41529-022-00263-z',
        '10.1038/s41598-024-67799-9']


def main():
    load_dotenv(ROOT / '.env')
    key = os.environ['SPRINGER_OPEN_ACCESS_API_KEY']
    for doi in DOIS:
        out = ROOT / '01_논문원문과데이터/raw/springer_round' / doi.split('/')[-1]
        out.mkdir(parents=True, exist_ok=True)
        xml_path = out / 'article.xml'
        if not xml_path.exists():
            response = requests.get('https://api.springernature.com/openaccess/jats',
                params={'q': 'doi:' + doi, 'p': 1, 'api_key': key}, timeout=45)
            if response.status_code != 200:
                print(doi, 'HTTP', response.status_code, flush=True)
                continue
            xml_path.write_text(response.text.replace(key, '[REDACTED]'), encoding='utf-8')
        root = ET.fromstring(xml_path.read_text(encoding='utf-8'))
        for node in root.iter():
            node.tag = node.tag.rsplit('}', 1)[-1]
        # Validate the requested article identity, not a DOI appearing in references.
        article = next((a for a in root.iter('article') if any(
            n.get('pub-id-type') == 'doi' and (n.text or '').lower() == doi
            for n in a.findall('./front/article-meta/article-id'))), None)
        if article is None:
            print(doi, 'no matching article', flush=True)
            continue
        blocks = evidence_blocks(ET.tostring(article, encoding='unicode'))
        title = ' '.join(article.find('./front/article-meta/title-group/article-title').itertext())
        (out/'blocks.json').write_text(json.dumps(blocks, ensure_ascii=False, indent=2), encoding='utf-8')
        (out/'metadata.json').write_text(json.dumps({'doi': doi, 'title': title,
            'retrieval_provider': 'springer_openaccess_jats',
            'source_url': 'https://doi.org/' + doi}, ensure_ascii=False, indent=2), encoding='utf-8')
        print(doi, len(blocks), 'blocks', flush=True)


if __name__ == '__main__':
    main()
