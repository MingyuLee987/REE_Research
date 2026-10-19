"""Bounded three-paper pilot of evidence-backed context enrichment."""
import json
from pathlib import Path
from ree_research.context import enrich

ROOT = Path(__file__).resolve().parents[1]


def main():
    cases = [('PMC11433059','europepmc'),('PMC11720852','europepmc'),('metals_h13_y','additional')]
    results = []
    for name, folder in cases:
        try:
            rows = enrich(ROOT/'01_논문원문과데이터/processed/extractions'/name/'pending_measurements.csv',
                          ROOT/'01_논문원문과데이터/raw'/folder/name, ROOT/'01_논문원문과데이터/processed/context_v2'/name)
            result = {'source':name, 'rows':rows, 'status':'pending_field_review'}
        except (ValueError,RuntimeError) as error:
            result = {'source':name,'status':'failed','error':str(error)}
        print(json.dumps(result),flush=True)
        results.append(result)
    out=ROOT/'01_논문원문과데이터/processed/context_v2';out.mkdir(parents=True,exist_ok=True)
    (out/'manifest.json').write_text(json.dumps(results,indent=2),encoding='utf-8')


if __name__=='__main__':
    main()
