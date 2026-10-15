"""Bounded API discovery. Metadata is never treated as a measured experiment."""
import json
import os
from pathlib import Path
import requests
from dotenv import load_dotenv
from urllib.parse import quote
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def fetch_elsevier(doi, output_dir):
    """Retrieve publisher XML through the official API; keep full-text status explicit."""
    from .screening import normalize_doi
    doi = normalize_doi(doi)
    if not doi:
        raise ValueError('A valid DOI is required')
    load_dotenv(ROOT / '.env')
    key = os.getenv('ELSEVIER_API_KEY')
    if not key or key.startswith('your_'):
        raise ValueError('Set ELSEVIER_API_KEY')
    try:
        response = requests.get('https://api.elsevier.com/content/article/doi/' + quote(doi, safe='/'),
                                headers={'X-ELS-APIKey': key, 'Accept': 'text/xml'},
                                params={'view': 'FULL'}, timeout=45)
    except requests.RequestException:
        raise RuntimeError('Elsevier full-text request failed (URL redacted)') from None
    if response.status_code != 200:
        raise RuntimeError(f'Elsevier article retrieval HTTP {response.status_code}; full-text not acquired')
    text = response.content.decode('utf-8-sig').replace(key, '[REDACTED]')
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        raise RuntimeError('Elsevier article response was not valid XML') from None
    if any(node.tag.rsplit('}', 1)[-1] in ('error', 'service-error') for node in root.iter()):
        raise RuntimeError('Elsevier returned an XML application error; full-text not acquired')
    # Metadata/abstract-only responses must never be reported as full-text.
    full_nodes = [node for node in root.iter() if node.tag.rsplit('}', 1)[-1] == 'originalText']
    full_text = '\n'.join(' '.join(node.itertext()) for node in full_nodes).strip()
    status = 'original_text_present_requires_review' if full_text else 'metadata_only'
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / 'article.xml').write_text(text, encoding='utf-8')
    if full_text:
        (out / 'article_text.txt').write_text(full_text, encoding='utf-8')
    manifest = {'doi': doi, 'provider': 'elsevier', 'status': status, 'original_text_characters': len(full_text),
                'measurement_status': 'not_extracted'}
    (out / 'retrieval.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    return manifest


def search(provider, query, output, limit=5):
    load_dotenv(ROOT / '.env')
    config = {
        'elsevier': ('https://api.elsevier.com/content/search/scopus', 'ELSEVIER_API_KEY'),
        'springer-meta': ('https://api.springernature.com/meta/v2/json', 'SPRINGER_META_API_KEY'),
        'springer-oa': ('https://api.springernature.com/openaccess/json', 'SPRINGER_OPEN_ACCESS_API_KEY'),
    }
    url, variable = config[provider]
    key = os.getenv(variable)
    if not key or key.startswith('your_'):
        raise ValueError(f'Set {variable} in .env')
    if not 1 <= limit <= 25:
        raise ValueError('limit must be 1..25')
    params = {'query': query, 'count': limit} if provider == 'elsevier' else {'q': query, 'p': limit, 'api_key': key}
    headers = {'Accept': 'application/json'}
    if provider == 'elsevier':
        headers['X-ELS-APIKey'] = key
    try:
        response = requests.get(url, params=params, headers=headers, timeout=45)
    except requests.RequestException:
        raise RuntimeError(f'{provider}: network request failed (URL redacted)') from None
    if response.status_code != 200:
        raise RuntimeError(f'{provider}: HTTP {response.status_code}; check key, subscription, institutional access')
    response.encoding = 'utf-8'
    try:
        payload = response.json()
    except ValueError:
        raise RuntimeError(f'{provider}: response was not JSON') from None
    if payload.get('error') or payload.get('service-error'):
        raise RuntimeError(f'{provider}: API returned an application error (details redacted)')
    # Scrub echoed credentials before writing publisher responses.
    serialized = json.dumps({'provider': provider, 'query': query, 'response': payload}, ensure_ascii=False, indent=2)
    for name in config.values():
        secret = os.getenv(name[1])
        if secret:
            serialized = serialized.replace(secret, '[REDACTED]')
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(serialized, encoding='utf-8')
    return destination
