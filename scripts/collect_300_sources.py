"""Acquire additional originals; failed retrievals never produce measurements."""
import concurrent.futures
import json
import os
from pathlib import Path
from urllib.parse import quote
import requests
from dotenv import load_dotenv
from ree_research.ingestion import prepare_pdf

ROOT=Path(__file__).resolve().parents[1]
SOURCES=[
 ('wiley','10.1002/maco.202414447'),
 ('springer','10.1134/S2070205125700261'),
 ('springer','10.1134/S2070205124702265'),
 ('springer','10.1038/s41529-026-00746-3'),
 ('springer','10.1038/s41598-018-23273-x'),
 ('springer','10.1038/s41529-022-00263-z'),
 ('degruyter','10.1515/rams-2022-0284'),
 ('iop','10.1088/2053-1591/ac2343'),
 ('iop','10.1088/2053-1591/acc236'),
]

def main():
 load_dotenv(ROOT/'.env');token=os.getenv('WILEY_TDM_TOKEN')
 def fetch(item):
  provider,doi=item
  urls={'springer':'https://link.springer.com/content/pdf/'+doi+'.pdf',
    'wiley':'https://api.wiley.com/onlinelibrary/tdm/v1/articles/'+quote(doi,safe=''),
    'degruyter':'https://www.degruyterbrill.com/document/doi/'+doi+'/pdf',
    'iop':'https://iopscience.iop.org/article/'+doi+'/pdf'}
  out=ROOT/'data/raw/round300/sources'/(provider+'_'+doi.split('/')[-1]);out.mkdir(parents=True,exist_ok=True)
  pdf=out/'article.pdf'
  if not pdf.exists():
   try:r=requests.get(urls[provider],headers={'Wiley-TDM-Client-Token':token} if provider=='wiley' else {},timeout=45)
   except requests.RequestException:return dict(doi=doi,status='network_error_redacted')
   if not r.content.startswith(b'%PDF'):return dict(doi=doi,http=r.status_code,status='no_pdf_acquired')
   pdf.write_bytes(r.content)
  pages=prepare_pdf(pdf,out,doi=doi,title=doi)
  return dict(doi=doi,pages=pages,status='full_pdf_acquired_not_reviewed',source=str(out))
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:rs=list(pool.map(fetch,SOURCES))
 (ROOT/'data/raw/round300/retrieval.json').write_text(json.dumps(rs,indent=2),encoding='utf-8')
 for r in rs:print(json.dumps(r),flush=True)

if __name__=='__main__':main()
