"""Bounded Springer OA discovery with cached responses and redacted credentials."""
import concurrent.futures
import json
import os
from pathlib import Path
import re
import requests
import time
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '01_논문원문과데이터/raw/springer_round'


def main():
    load_dotenv(ROOT / '.env')
    key = os.environ['SPRINGER_OPEN_ACCESS_API_KEY']
    OUT.mkdir(parents=True, exist_ok=True)
    queries = ['cerium corrosion steel microalloying',
               'lanthanum corrosion steel microalloying',
               '"rare earth" corrosion steel microalloying',
               'yttrium corrosion steel', 'cerium corrosion stainless',
               'lanthanum corrosion steel', '"rare earth" corrosion steel']
    records = {}

    def page(qi, start):
        path = OUT / f'query{qi}_start{start}.json'
        if path.exists():
            return json.loads(path.read_text(encoding='utf-8'))
        for attempt in range(4):
            response = requests.get('https://api.springernature.com/openaccess/json',
                params={'q': queries[qi], 's': start, 'p': 25, 'api_key': key}, timeout=45)
            if response.status_code != 429 or attempt == 3:
                break
            time.sleep(20)
        if response.status_code != 200:
            raise RuntimeError(f'Springer search HTTP {response.status_code}; credentials redacted')
        payload = response.json()
        path.write_text(json.dumps(payload, ensure_ascii=False).replace(key, '[REDACTED]'), encoding='utf-8')
        return payload

    for qi, query in enumerate(queries):
        first = page(qi, 1)
        total = int(first['result'][0]['total'])
        # Bounded to the first 1500 per query, never silently claim complete coverage.
        starts = list(range(26, min(total, 1500) + 1, 25))
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            payloads = [first] + list(pool.map(lambda start: page(qi, start), starts))
        for payload in payloads:
            for entry in payload.get('records', []):
                records[entry['doi'].lower()] = entry
        print(qi, 'total', total, 'unique', len(records), flush=True)
    (OUT/'candidates.json').write_text(json.dumps(list(records.values()), ensure_ascii=False, indent=2), encoding='utf-8')
    shortlist = [r for r in records.values() if
        re.search(r'corrosi|electrochem', r['title'], re.I) and
        re.search(r'cerium|lanthanum|rare.earth|yttrium|\bCe\b|\bLa\b|\bRE\b', r['title'], re.I) and
        re.search(r'steel|iron|ferrous|Fe[–−-]', r['title'], re.I)]
    (OUT/'shortlist.json').write_text(json.dumps(shortlist, ensure_ascii=False, indent=2), encoding='utf-8')
    for entry in shortlist:
        print(entry['doi'], entry['title'].encode('ascii', 'replace').decode(), flush=True)


if __name__ == '__main__':
    main()
