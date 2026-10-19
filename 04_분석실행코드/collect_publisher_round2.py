"""Acquire publisher-original PDFs with explicit provenance and bounded failures."""
import concurrent.futures
import json
import os
from pathlib import Path
import re
from urllib.parse import quote
import requests
from dotenv import load_dotenv
from ree_research.ingestion import prepare_pdf

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    ('wiley','10.1002/maco.201911150'),
    ('wiley','10.1002/maco.202213672'),
    ('wiley','10.1002/maco.202213104'),
    ('wiley','10.1002/srin.201300438'),
    ('wiley','10.1002/srin.202300041'),
    ('springer','10.1007/s10853-025-11514-0'),
    ('springer','10.1007/s11665-019-04112-0'),
    ('springer','10.1007/s11663-026-04267-x'),
    ('springer','10.1007/978-3-030-05861-6_53'),
    ('springer','10.1007/s11665-015-1651-6'),
    ('wiley','10.1002/maco.201508380'),
    ('springer','10.1007/s11663-025-03792-5'),
    ('springer','10.1007/s11663-025-03817-z'),
    ('springer','10.1023/B:MASC.0000023502.72468.31'),
    ('wiley','10.1002/mawe.201900045'),
]


def main():
    load_dotenv(ROOT/'.env')
    token = os.getenv('WILEY_TDM_TOKEN')

    def collect(item):
        provider, doi = item
        name = re.sub(r'[^\w.-]', '_', doi.split('/')[-1])
        name = {'maco.201911150':'maco201911150',
                'maco.202213672':'maco202213672'}.get(name,name)
        out = ROOT/f'01_논문원문과데이터/raw/{provider}_round2'/name
        out.mkdir(parents=True,exist_ok=True)
        url = ('https://api.wiley.com/onlinelibrary/tdm/v1/articles/'+quote(doi,safe='')
               if provider=='wiley' else 'https://link.springer.com/content/pdf/'+doi+'.pdf')
        if not (out/'article.pdf').exists():
            try:
                r = requests.get(url, headers={'Wiley-TDM-Client-Token':token} if provider=='wiley' else {}, timeout=45)
            except requests.RequestException:
                return {'provider':provider,'doi':doi,'status':'network_error_redacted'}
            if not r.content.startswith(b'%PDF'):
                return {'provider':provider,'doi':doi,'http':r.status_code,'status':'no_pdf_acquired'}
            (out/'article.pdf').write_bytes(r.content)
        pages = prepare_pdf(out/'article.pdf',out,doi=doi,title=doi)
        metadata = json.loads((out/'metadata.json').read_text(encoding='utf-8'))
        metadata.update(retrieval_provider=provider, acquisition_url=url)
        (out/'metadata.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
        return {'provider':provider,'doi':doi,'pages':pages,'status':'acquired_not_extracted'}

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(collect,SOURCES))
    out = ROOT/'01_논문원문과데이터/raw/publisher_round2'
    out.mkdir(parents=True,exist_ok=True)
    (out/'additional_retrieval.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    for result in results:
        print(json.dumps(result),flush=True)


if __name__=='__main__':
    main()
