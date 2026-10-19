"""Merge evidence-backed context only; never change labels/review status."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from ree_research.context import CONTEXT_NUMERIC, CONTEXT_CATEGORICAL
from ree_research.schema import prepare, ALL_FEATURES

ROOT=Path(__file__).resolve().parents[1]


def main():
    baseline=pd.read_csv(ROOT/'01_논문원문과데이터/processed/pilot100/provisional_for_model.csv')
    rows={r['record_id']:r for r in baseline.to_dict('records')}
    updates=0
    for path in sorted((ROOT/'01_논문원문과데이터/processed/context_v2').glob('*/enriched_pending.csv')):
        for context in pd.read_csv(path).to_dict('records'):
            if context['record_id'] not in rows:continue
            original=rows[context['record_id']]
            assert original['icorr_A_cm2']==context['icorr_A_cm2']
            for field in CONTEXT_NUMERIC+CONTEXT_CATEGORICAL:
                value=context.get(field)
                if value is None or pd.isna(value):continue
                existing=original.get(field)
                if existing is not None and not pd.isna(existing):
                    same=np.isclose(existing,value) if field in CONTEXT_NUMERIC else existing==value
                    if not same:raise ValueError(f'Conflicting context value {field}: review before merge')
                original[field]=value
                updates+=1
    merged=pd.DataFrame(rows.values())
    assert merged.review_status.eq('pending').all()
    checked=prepare(merged,allowed_review_statuses=('pending',))
    out=ROOT/'01_논문원문과데이터/processed/context_v2'
    merged.to_csv(out/'provisional_enriched.csv',index=False)
    checked[ALL_FEATURES].notna().mean().rename('coverage_fraction').to_csv(out/'feature_coverage.csv')
    (out/'assembly.json').write_text(json.dumps({'rows':len(merged),'context_nonnull_values_applied':updates,
        'labels_changed':False,'review_status':'pending','evaluation':'not_evaluated_on_old_holdout'},indent=2),encoding='utf-8')
    print(f'Preserved {len(merged)} targets; {updates} non-null context values applied; all pending')


if __name__=='__main__':main()
