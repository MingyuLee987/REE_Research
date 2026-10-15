"""Bounded paid Sol extraction for selected bulk-REE candidate papers only."""
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from ree_research.extraction import extract

ROOT = Path(__file__).resolve().parents[1]
PAPERS = ['PMC13304421', 'PMC12156170', 'PMC11720852', 'PMC11433059',
          'PMC6829360', 'PMC11901239', 'PMC12415021', 'PMC11266659',
          'PMC9693607', 'PMC9864991', 'PMC5859157', 'PMC11818875']


def run(pmcid):
    source = ROOT / 'data/raw/europepmc' / pmcid
    output = ROOT / 'data/processed/extractions' / pmcid
    if not (source / 'blocks.json').exists():
        return {'pmcid': pmcid, 'status': 'source_not_acquired'}
    try:
        # Successful results are not billed again; previously rejected responses are revalidated.
        if (output / 'run.json').exists():
            saved = json.loads((output / 'run.json').read_text(encoding='utf-8'))
            return {'pmcid': pmcid, 'status': 'cached', 'rows': saved['rows']}
        rows = extract(source, output, reuse_response=(output / 'response.json').exists())
        return {'pmcid': pmcid, 'status': 'pending_review', 'rows': rows}
    except (ValueError, RuntimeError) as error:
        return {'pmcid': pmcid, 'status': 'failed_validation_or_api', 'error': str(error)}


def main():
    results = []
    with ThreadPoolExecutor(max_workers=1) as executor:
        futures = [executor.submit(run, p) for p in PAPERS]
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(json.dumps(result), flush=True)
    destination = ROOT / 'data/processed/pilot100/extraction_manifest.json'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(results, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
