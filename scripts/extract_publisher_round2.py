"""Cached extraction of newly acquired Wiley sources; never pad to a target."""
import json
from pathlib import Path
from ree_research.extraction import extract

ROOT = Path(__file__).resolve().parents[1]


def main():
    results = []
    sources = [(provider, path.parent) for provider in ['wiley','springer']
               for path in sorted((ROOT/f'data/raw/{provider}_round2').glob('*/blocks.json'))]
    for provider, source in sources:
        name = source.name
        out = ROOT/'data/processed/extractions'/(provider+'_'+name)
        try:
            if (out/'run.json').exists():
                count = json.loads((out/'run.json').read_text())['rows']
            else:
                count = extract(source,out,reuse_response=(out/'response.json').exists())
            result = {'source':name,'rows':count,'status':'pending'}
        except (ValueError,RuntimeError) as error:
            result = {'source':name,'status':'extraction_or_validation_failed','error':str(error)}
        results.append(result)
        print(json.dumps(result),flush=True)
    path = ROOT/'data/processed/pilot100/publisher_round2_extraction.json'
    path.write_text(json.dumps(results,indent=2),encoding='utf-8')


if __name__ == '__main__':
    main()
