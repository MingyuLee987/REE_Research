import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from .schema import COMPOSITION, PROVENANCE, RAW, FEATURES, ALL_FEATURES, prepare


def demo(path):
    rng = np.random.default_rng(42)
    rows = []
    for paper in range(15):
        paper_effect = rng.normal(0, 0.2)
        for sample in range(8):
            row = dict(zip(COMPOSITION, [0.1, 0.3, 0.7, 0.02, 0.01, rng.uniform(0, 20), rng.uniform(0, 10), rng.uniform(0, 3), 0.1]))
            row.update(record_id=f'demo-{paper}-{sample}', paper_id=f'synthetic-{paper}', doi='',
                       source_locator='SYNTHETIC: no literature evidence', evidence_quote='SYNTHETIC TEST DATA',
                       review_status='verified', RE_ppm=float(rng.choice([0, 50, 100, 500])),
                       RE_element_cat=str(rng.choice(['none', 'Ce', 'La'])),
                       chloride_mol_L=rng.uniform(0.01, 1), temperature_C=rng.uniform(20, 60),
                       exposure_h=24, scan_rate_mV_s=0.5, ocp_stabilization_min=30,
                       gas_condition='air', matrix_family_reported='synthetic')
            if row['RE_ppm'] == 0:
                row['RE_element_cat'] = 'none'
            elif row['RE_element_cat'] == 'none':
                row['RE_element_cat'] = 'Ce'
            target = -5 - 0.065 * row['Cr'] + 0.5 * row['chloride_mol_L'] + 0.01 * (row['temperature_C'] - 25) + paper_effect + rng.normal(0, 0.12)
            row['icorr_A_cm2'] = 10 ** target
            row['pH'] = 7.0
            row['electrolyte_condition_cat'] = 'synthetic_chloride_solution'
            rows.append(row)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(path, index=False)


def main():
    parser = argparse.ArgumentParser(description='REE corrosion literature workflow')
    sub = parser.add_subparsers(dest='command', required=True)
    search = sub.add_parser('search')
    search.add_argument('--provider', choices=['elsevier', 'springer-meta', 'springer-oa'], required=True)
    search.add_argument('--query', required=True)
    search.add_argument('--limit', type=int, default=5)
    search.add_argument('--output', required=True)
    screening = sub.add_parser('screen')
    screening.add_argument('--input-dir', default='data/raw')
    screening.add_argument('--output-dir', default='data/processed/literature')
    fetch = sub.add_parser('fetch-elsevier')
    fetch.add_argument('--doi', required=True)
    fetch.add_argument('--output-dir', required=True)
    template = sub.add_parser('template')
    template.add_argument('--output', default='data/measurements_template.csv')
    synthetic = sub.add_parser('demo')
    synthetic.add_argument('--output', default='data/processed/synthetic_demo.csv')
    validate = sub.add_parser('validate')
    validate.add_argument('input')
    bench = sub.add_parser('benchmark')
    bench.add_argument('input')
    bench.add_argument('--output', default='outputs/benchmark')
    bench.add_argument('--seeds', type=int, nargs='+', default=[11, 22, 33])
    bench.add_argument('--initial', type=int, default=20)
    bench.add_argument('--batch', type=int, default=5)
    bench.add_argument('--budget', type=int, default=50)
    bench.add_argument('--committee', type=int, default=8)
    bench.add_argument('--profile', choices=['core', 'extended'], default='core')
    bench.add_argument('--min-coverage', type=float, default=0.8)
    args = parser.parse_args()
    try:
        if args.command == 'search':
            from .mining import search as run_search
            print(run_search(args.provider, args.query, args.output, args.limit))
        elif args.command == 'screen':
            from .screening import screen
            result = screen(args.input_dir, args.output_dir)
            print(f"{result['records_seen']} records -> {result['unique_papers']} unique candidates; {result['duplicates_merged']} duplicates merged")
        elif args.command == 'fetch-elsevier':
            from .mining import fetch_elsevier
            print(fetch_elsevier(args.doi, args.output_dir))
        elif args.command == 'template':
            columns = PROVENANCE + RAW + [f for f in ALL_FEATURES if f not in ('RE_log1p_ppm', 'high_Cr_indicator')]
            Path(args.output).parent.mkdir(parents=True, exist_ok=True)
            pd.DataFrame(columns=columns).to_csv(args.output, index=False)
            print(args.output)
        elif args.command == 'demo':
            demo(args.output)
            print(f'SYNTHETIC ONLY: {args.output}')
        elif args.command == 'validate':
            frame = prepare(pd.read_csv(args.input))
            print(f'Validated: {len(frame)} rows, {frame.paper_id.nunique()} papers, {len(FEATURES)} features')
            print(frame[FEATURES].isna().mean().to_string())
        else:
            from .benchmark import benchmark
            scores = benchmark(args.input, args.output, args.seeds, args.initial, args.batch, args.budget, args.committee, args.profile, args.min_coverage)
            print(scores.groupby(['model', 'strategy']).tail(1).to_string(index=False))
            print(f'Saved: {args.output}')
    except (ValueError, RuntimeError, FileNotFoundError) as error:
        parser.exit(1, f'{error}\n')


if __name__ == '__main__':
    main()
