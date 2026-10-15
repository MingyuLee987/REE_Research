"""Sequential, cached extraction of five additional bulk-REE papers."""
import json
from pathlib import Path
from ree_research.extraction import extract

ROOT = Path(__file__).resolve().parents[1]


def main():
    results = []
    names = ['coatings_eh36', 'metals_bridge_ce', 'metals_h13_y', 'metals_weld_ce', 'metals_wetdry']
    for name in names:
        source = ROOT / 'data/raw/additional' / name
        output = ROOT / 'data/processed/extractions' / name
        try:
            if (output / 'run.json').exists():
                rows = json.loads((output / 'run.json').read_text(encoding='utf-8'))['rows']
            else:
                rows = extract(source, output, reuse_response=(output / 'response.json').exists())
            result = {'source': name, 'status': 'pending_review', 'rows': rows}
        except (ValueError, RuntimeError) as error:
            result = {'source': name, 'status': 'failed_validation_or_api', 'error': str(error)}
        results.append(result)
        print(json.dumps(result), flush=True)
    (ROOT / 'data/processed/pilot100/additional_extraction_manifest.json').write_text(json.dumps(results, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
