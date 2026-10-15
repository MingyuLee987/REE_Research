"""API-key-backed supplementary discovery; preserve queries and failures."""
import concurrent.futures
import json
from pathlib import Path
from ree_research.mining import search

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/raw/round300'
QUERIES=[
 ('elsevier','TITLE-ABS-KEY((cerium OR lanthanum OR yttrium OR "rare earth") AND (steel OR iron) AND ("corrosion current" OR Tafel))'),
 ('elsevier','TITLE-ABS-KEY((cerium OR lanthanum OR "rare earth") AND steel AND corrosion) AND PUBYEAR < 2015'),
 ('elsevier','TITLE-ABS-KEY((yttrium OR praseodymium OR neodymium) AND steel AND corrosion)'),
 ('elsevier','TITLE-ABS-KEY((cerium OR lanthanum OR "rare earth") AND (steel OR iron) AND corrosion) AND PUBYEAR > 2024'),
 ('springer-meta','"rare earth" corrosion steel'),
 ('springer-meta','cerium corrosion stainless'),
 ('springer-meta','lanthanum corrosion steel'),
 ('springer-meta','yttrium corrosion steel'),
 ('springer-meta','praseodymium corrosion steel'),
 ('springer-meta','"rare earth" rebar corrosion'),
 ('springer-oa','"cerium" "steel" "corrosion"'),
 ('springer-oa','"lanthanum" "steel" "corrosion"'),
]

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 def run(item):
  i,(provider,query)=item;p=OUT/f'query_{i}.json'
  try:
   if not p.exists():search(provider,query,p,25)
   d=json.loads(p.read_text(encoding='utf-8'));r=d['response']
   entries=r.get('records',[]) if provider.startswith('springer') else r.get('search-results',{}).get('entry',[])
   return dict(provider=provider,query=query,status='ok',entries=[dict(doi=e.get('doi',e.get('prism:doi','')),title=e.get('title',e.get('dc:title',''))) for e in entries])
  except (ValueError,RuntimeError) as err:return dict(provider=provider,query=query,status=str(err))
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(run,enumerate(QUERIES)))
 (OUT/'discovery.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
 seen=set()
 for r in results:
  print(r['provider'],r['status'],flush=True)
  for e in r.get('entries',[]):
   if e['doi'] not in seen:
    seen.add(e['doi']);print(e['doi'],e['title'],flush=True)

if __name__=='__main__':main()
