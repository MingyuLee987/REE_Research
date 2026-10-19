"""Collect bounded OA candidate XML and preserve table/paragraph evidence blocks."""
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]


def evidence_blocks(xml):
    root = ET.fromstring(xml)
    blocks = []
    for kind in ['article-title', 'abstract', 'table-wrap', 'p']:
        for index, node in enumerate(root.iter(kind)):
            if kind == 'p' and any(node is p for table in root.iter('table-wrap') for p in table.iter('p')):
                continue
            text = re.sub(r'\s+', ' ', ' '.join(node.itertext())).strip()
            if text:
                blocks.append({'locator': f'{kind}:{node.get("id", index)}', 'text': text,
                               'xml': ET.tostring(node, encoding='unicode') if kind == 'table-wrap' else None})
    return blocks


def main():
    directory = ROOT / '01_논문원문과데이터/raw/europepmc'
    saved = json.loads((directory / 'targeted_search.json').read_text(encoding='utf-8'))
    entries = saved['resultList']['result']
    # Additional ferrous-alloy candidates from the broader discovery search.
    broad = json.loads((directory / 'search.json').read_text(encoding='utf-8'))
    entries += [r for r in broad['resultList']['result'] if r.get('pmcid') in ('PMC12415021', 'PMC11266659', 'PMC11901239')]
    extended_path = directory / 'extended_search.json'
    if extended_path.exists():
        extended = json.loads(extended_path.read_text(encoding='utf-8'))
        entries += [r for r in extended['resultList']['result'] if r.get('pmcid') in
                    ('PMC9693607', 'PMC9864991', 'PMC5859157', 'PMC11818875')]
    entries = list({r['pmcid']: r for r in entries if r.get('pmcid')}.values())
    manifest = []
    for entry in entries:
        pmcid = entry.get('pmcid')
        if not pmcid:
            continue
        destination = directory / pmcid
        destination.mkdir(parents=True, exist_ok=True)
        xml_path = destination / 'article.xml'
        url = f'https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML'
        try:
            if not xml_path.exists():
                response = requests.get(url, timeout=45)
                response.raise_for_status()
                ET.fromstring(response.content)
                xml_path.write_bytes(response.content)
            blocks = evidence_blocks(xml_path.read_bytes())
            (destination / 'blocks.json').write_text(json.dumps(blocks, ensure_ascii=False, indent=2), encoding='utf-8')
            (destination / 'metadata.json').write_text(json.dumps(entry, ensure_ascii=False, indent=2), encoding='utf-8')
            manifest.append({'pmcid': pmcid, 'doi': entry.get('doi'), 'title': entry.get('title'), 'source_url': url,
                             'blocks': len(blocks), 'tables': sum(b['locator'].startswith('table-wrap:') for b in blocks),
                             'status': 'fulltext_acquired_not_reviewed'})
            print(pmcid, 'acquired', len(blocks), 'blocks', flush=True)
        except (requests.RequestException, ET.ParseError) as error:
            manifest.append({'pmcid': pmcid, 'status': 'failed', 'error_type': type(error).__name__})
            print(pmcid, 'failed', type(error).__name__, flush=True)
    (directory / 'collection_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
