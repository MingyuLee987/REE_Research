"""Extract only pre-measurement context with field-level source evidence."""
import hashlib
import json
import os
from pathlib import Path
import requests
import pandas as pd
from dotenv import load_dotenv
from .schema import OPTIONAL_NUMERIC, OPTIONAL_CATEGORICAL, LITERATURE_NUMERIC, LITERATURE_CATEGORICAL, DERIVED_FEATURES
from .extraction import resolve_locators, quote_matches

ROOT = Path(__file__).resolve().parents[2]
CONTEXT_NUMERIC = [c for c in OPTIONAL_NUMERIC + LITERATURE_NUMERIC if c not in DERIVED_FEATURES]
CONTEXT_CATEGORICAL = OPTIONAL_CATEGORICAL + LITERATURE_CATEGORICAL


def enrich(input_csv, source_dir, output_dir):
    load_dotenv(ROOT / '.env')
    key = os.getenv('OPENAI_API_KEY')
    if not key:
        raise ValueError('Set OPENAI_API_KEY')
    source, out = Path(source_dir), Path(output_dir)
    df = pd.read_csv(input_csv)
    if df.paper_id.nunique() != 1 or not df.record_id.is_unique:
        raise ValueError('Context input must be unique measurements from one paper')
    blocks = json.loads((source / 'blocks.json').read_text(encoding='utf-8'))
    fields = {f: {'type': ['number', 'null']} for f in CONTEXT_NUMERIC}
    fields.update({f: {'type': ['string', 'null']} for f in CONTEXT_CATEGORICAL})
    fields['record_id'] = {'type': 'string'}
    fields['evidence'] = {'type': 'array', 'items': {'type': 'object', 'properties': {
        'fields': {'type': 'array', 'items': {'type': 'string', 'enum': CONTEXT_NUMERIC + CONTEXT_CATEGORICAL}},
        'locator': {'type': 'string'}, 'quote': {'type': 'string'}},
        'required': ['fields','locator','quote'], 'additionalProperties': False}}
    schema = {'type': 'object', 'properties': {'rows': {'type': 'array', 'items': {
        'type': 'object', 'properties': fields, 'required': list(fields), 'additionalProperties': False}}},
        'required': ['rows'], 'additionalProperties': False}
    rows = df[['record_id','sample_id']].to_dict('records')
    content = json.dumps({'rows_to_enrich': rows, 'article_blocks': blocks}, ensure_ascii=False)
    digest = hashlib.sha256(content.encode()).hexdigest()
    instructions = (ROOT / '02_연구설명과논문작성/context_extraction.md').read_text(encoding='utf-8')
    out.mkdir(parents=True, exist_ok=True)
    cached = out / 'response.json'
    manifest = out / 'request.json'
    if cached.exists():
        if not manifest.exists() or json.loads(manifest.read_text())['source_sha256'] != digest:
            raise ValueError('Cached context response input differs; use a new output directory')
        result = json.loads(cached.read_text(encoding='utf-8'))
    else:
        manifest.write_text(json.dumps({'source_sha256': digest, 'model': 'gpt-6.1-sol'}), encoding='utf-8')
        payload = {'model': 'gpt-6.1-sol', 'instructions': instructions, 'input': content, 'store': False,
            'max_output_tokens': 9000, 'text': {'format': {'type': 'json_schema', 'name': 'corrosion_context', 'strict': True, 'schema': schema}}}
        try:
            response = requests.post('https://api.openai.com/v1/responses', headers={'Authorization':'Bearer '+key}, json=payload, timeout=180)
        except requests.RequestException:
            raise RuntimeError('Context request failed; details redacted') from None
        if response.status_code != 200:
            raise RuntimeError(f'Context API HTTP {response.status_code}; no context values created')
        result = response.json()
        cached.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    if result.get('status') != 'completed':
        raise RuntimeError('Context response incomplete; no values applied')
    parsed = json.loads(''.join(c['text'] for item in result.get('output',[]) for c in item.get('content',[]) if c.get('type')=='output_text'))
    extracted = parsed['rows']
    if len(extracted) != len(df) or {r['record_id'] for r in extracted} != set(df.record_id):
        raise ValueError('Context response row IDs/count differ')
    source_text = {b['locator']: b['text'] for b in blocks}
    audit = []
    enriched = df.set_index('record_id').copy()
    for field in CONTEXT_CATEGORICAL:
        if field not in enriched:
            enriched[field] = pd.Series(index=enriched.index, dtype=object)
        else:
            enriched[field] = enriched[field].astype(object)
    for row in extracted:
        supported = set()
        for cite in row['evidence']:
            locators = resolve_locators(cite['locator'], source_text)
            if not any(quote_matches(cite['quote'],source_text[k]) for k in locators):
                raise ValueError(f'Context evidence mismatch for {row["record_id"]}')
            supported.update(cite['fields'])
            audit.append({'record_id':row['record_id'], **cite})
        for field in CONTEXT_NUMERIC + CONTEXT_CATEGORICAL:
            value = row[field]
            if value is not None and field not in supported:
                raise ValueError(f'Missing field evidence: {field}')
            enriched.loc[row['record_id'], field] = value
    enriched.reset_index().to_csv(out/'enriched_pending.csv',index=False)
    (out/'field_evidence.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'run.json').write_text(json.dumps({'rows':len(df),'model':'gpt-6.1-sol','usage':result.get('usage'),
        'source_sha256':digest,'review_status':'pending'},indent=2),encoding='utf-8')
    return len(df)
