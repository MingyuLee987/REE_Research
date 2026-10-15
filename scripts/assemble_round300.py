"""Audit this acquisition round and record the unresolved 300-point target."""
import hashlib
import json
from pathlib import Path
import pandas as pd
from ree_research.schema import prepare

ROOT=Path(__file__).resolve().parents[1]


def annotate():
    for name in ['r300_springer_S2070205124702265']:
        p=ROOT/'data/processed/extractions'/name/'pending_measurements.csv'
        if p.exists():
            f=pd.read_csv(p)
            f['quality_hold_reason']='shared_base_composition_not_sample_resolved_requires_review'
            f.to_csv(p,index=False)


def report():
    f=pd.read_csv(ROOT/'data/processed/pilot100/llm_pending_all.csv')
    fresh=f[f.extraction_source.str.startswith('r300_')].copy()
    out=ROOT/'data/processed/round300';out.mkdir(parents=True,exist_ok=True)
    fresh.to_csv(out/'new_measurements_pending.csv',index=False)
    context=pd.read_csv(ROOT/'data/processed/context_v2/provisional_enriched.csv')
    ready=prepare(context,allowed_review_statuses=('pending',))
    ready.to_csv(ROOT/'data/processed/context_v2/features_v3_pending.csv',index=False)
    groups=[dict(doi=doi,data_points=len(g),held=int(g.hold_reason.notna().sum())) for doi,g in fresh.groupby('paper_id')]
    ledger=ROOT/'data/raw/round300/ce_alkaline_images/unmerged_current_annotations.csv'
    status=dict(target_data_points=300,previous_data_points=167,total_data_points=len(f),
                new_data_points=len(fresh),papers=int(f.paper_id.nunique()),
                provisional_data_points=int(f.hold_reason.isna().sum()),
                held_data_points=int(f.hold_reason.notna().sum()),human_verified=0,
                shortfall=max(0,300-len(f)),target_met=len(f)>=300,
                new_studies=groups,unmerged_current_annotations=len(pd.read_csv(ledger)) if ledger.exists() else 0,
                excluded_candidate_reason='Current annotations in A cannot be normalized to A/cm2 without area and full condition mapping.',
                whole_dataset_sha256=hashlib.sha256((ROOT/'data/processed/pilot100/llm_pending_all.csv').read_bytes()).hexdigest())
    (out/'status.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
    print(json.dumps(status,indent=2))


if __name__=='__main__':
    import sys
    annotate() if '--annotate-only' in sys.argv else report()
