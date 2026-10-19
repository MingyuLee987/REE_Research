"""Merge evidenced phase context into a versioned, clean snapshot without changing labels."""
import hashlib
import argparse
import json
from pathlib import Path
import re
import numpy as np
import pandas as pd
from ree_research.schema import (ALL_FEATURES, COMPOSITION, ADDITIONAL_COMPOSITION,
    CORROSION_RAW_FEATURES, DERIVED_FEATURES, FEATURE_PROFILES, prepare)
from ree_research.phase_features import (PHASE_FRACTIONS, PHASE_RAW_CATEGORICAL,
    PHASE_DERIVED_NUMERIC, PHASE_DERIVED_CATEGORICAL, engineer_phase)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'01_논문원문과데이터/processed/phase_v4'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish',action='store_true',help='Update current CSVs from this evidenced snapshot')
    args=parser.parse_args()
    frame=pd.read_csv(OUT/'baseline_all.csv').set_index('record_id')
    previous=pd.read_csv(OUT/'baseline_context.csv').set_index('record_id')
    # Previously evidenced context is kept, including records outside the primary CSV's old raw fields.
    for column in previous:
        if column in ['icorr_A_cm2','paper_id','doi','sample_id','review_status','hold_reason']:continue
        if column not in frame:frame[column]=np.nan
        frame[column]=frame[column].combine_first(previous[column].reindex(frame.index))
    for column in PHASE_RAW_CATEGORICAL+['phase_evidence_type']:
        frame[column]=pd.Series(index=frame.index,dtype=object)
    for column in PHASE_FRACTIONS:frame[column]=np.nan
    applied=[];conflicts=[];skipped=[]
    for path in sorted((OUT/'readings').glob('*/validated_fields.json')):
        updates=json.loads(path.read_text(encoding='utf-8'))
        type_supported={u['record_id'] for u in updates if u['field']=='phase_evidence_type'
            and u['value'] in ('author_material_family','pre_corrosion_characterization')}
        for item in updates:
            rid,field,value=item['record_id'],item['field'],item['value']
            if rid not in frame.index:raise ValueError('Unknown record in phase evidence')
            if field in PHASE_FRACTIONS+PHASE_RAW_CATEGORICAL and rid not in type_supported:
                skipped.append(dict(item,reason='phase_context_type_missing_valid_evidence'));continue
            if field in PHASE_FRACTIONS and item['phase_evidence_type']!='pre_corrosion_characterization':
                skipped.append(dict(item,reason='fraction_not_characterization_evidence'));continue
            if field not in frame:frame[field]=np.nan
            old=frame.loc[rid,field]
            if pd.notna(old):
                equal=np.isclose(float(old),float(value),rtol=1e-6,atol=1e-10) if isinstance(value,(int,float)) else str(old)==str(value)
                if not equal:conflicts.append(dict(item,existing_value=str(old),action='existing_value_preserved'))
                continue
            frame.loc[rid,field]=value
            applied.append(item)
    # Reported family/matrix and secondary phase text remain distinct; no grade-based phase imputation.
    phase_records={r['record_id'] for r in applied if r['field']=='matrix_phase_reported'}
    frame['phase_context_status']=['source_evidenced_pending_review' if rid in phase_records else 'not_recovered' for rid in frame.index]
    frame['phase_source_locator']=[';'.join(dict.fromkeys(c['locator'] for u in applied
        if u['record_id']==rid and u['field']=='matrix_phase_reported' for c in u['evidence'])) or np.nan for rid in frame.index]
    frame['phase_evidence_quote']=[' | '.join(dict.fromkeys(c['quote'] for u in applied
        if u['record_id']==rid and u['field']=='matrix_phase_reported' for c in u['evidence'])) or np.nan for rid in frame.index]
    # Never silently release old holds or overwrite target units/values during input-context re-reading.
    original=pd.read_csv(OUT/'baseline_all.csv').set_index('record_id')
    for field in ['icorr_A_cm2','original_icorr_value','review_status','hold_reason']:
        if field in original:
            pd.testing.assert_series_equal(frame[field],original[field],check_dtype=False)
    frame=frame.reset_index()
    for column in COMPOSITION+ADDITIONAL_COMPOSITION:
        if column not in frame:frame[column]=np.nan
        frame[column]=pd.to_numeric(frame[column],errors='raise')
    frame['RE_log1p_ppm']=np.log1p(pd.to_numeric(frame.RE_ppm,errors='raise'))
    frame=engineer_phase(frame)
    identity=['record_id','paper_id','doi','sample_id','review_status','hold_reason']
    raw=list(dict.fromkeys(CORROSION_RAW_FEATURES+ADDITIONAL_COMPOSITION+['RE_ppm']+PHASE_RAW_CATEGORICAL+PHASE_FRACTIONS))
    target=['icorr_A_cm2','original_icorr_value','original_icorr_unit','target_unit_status']
    provenance=['phase_evidence_type','phase_context_status','phase_source_locator','phase_evidence_quote',
        'source_locator','evidence_quote','composition_locator','condition_locator','source_file','source_url','extraction_source','notes']
    first=[c for c in identity+raw+PHASE_DERIVED_NUMERIC+PHASE_DERIVED_CATEGORICAL+target+provenance if c in frame]
    first=list(dict.fromkeys(first))
    frame=frame[first+[c for c in frame if c not in first]]
    frame.to_csv(OUT/'measurements_audit.csv',index=False)
    # A compact record log has raw values and provenance, with single-line quotations for CSV viewers.
    clean=frame.reindex(columns=first).copy()
    for column in clean.select_dtypes(include='object'):
        clean[column]=clean[column].map(lambda x:re.sub(r'\s+',' ',x).strip() if isinstance(x,str) else x)
    clean.to_csv(OUT/'measurements_clean.csv',index=False)
    provisional=frame[frame.hold_reason.isna()|frame.hold_reason.eq('')].copy()
    checked=prepare(provisional,allowed_review_statuses=('pending',))
    checked.to_csv(OUT/'features_pending.csv',index=False)
    numeric,categorical=FEATURE_PROFILES['phase_corrosion']
    model_columns=identity[:5]+numeric+categorical+['icorr_A_cm2','target']
    checked[model_columns].to_csv(OUT/'model_input_pending.csv',index=False)
    frame[~frame.record_id.isin(provisional.record_id)].to_csv(OUT/'held_for_review.csv',index=False)
    coverage=[]
    for c in numeric+categorical:
        present=checked[c].notna()
        coverage.append(dict(feature=c,nonmissing=int(present.sum()),coverage_fraction=float(present.mean()),
            papers=int(checked.loc[present,'paper_id'].nunique()),distinct_values=int(checked[c].nunique())))
    pd.DataFrame(coverage).to_csv(OUT/'feature_coverage.csv',index=False)
    (OUT/'applied_field_evidence.json').write_text(json.dumps(applied,ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'conflicting_field_evidence.json').write_text(json.dumps(conflicts,ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'skipped_field_evidence.json').write_text(json.dumps(skipped,ensure_ascii=False,indent=2),encoding='utf-8')
    report=dict(records=len(frame),papers=int(frame.paper_id.nunique()),provisional=len(checked),
        held=len(frame)-len(checked),human_verified=0,targets_changed=0,old_holds_released=0,
        phase_context_records=int(frame.matrix_phase_reported.notna().sum()),
        provisional_phase_context_records=int(checked.matrix_phase_reported.notna().sum()),
        added_fields=len(applied),existing_value_conflicts_not_overwritten=len(conflicts),
        input_profile='phase_corrosion',candidate_features=len(numeric+categorical),
        audit_sha256=hashlib.sha256((OUT/'measurements_audit.csv').read_bytes()).hexdigest())
    (OUT/'assembly.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    if args.publish:
        frame.to_csv(ROOT/'01_논문원문과데이터/processed/pilot100/llm_pending_all.csv',index=False)
        checked.to_csv(ROOT/'01_논문원문과데이터/processed/pilot100/provisional_for_model.csv',index=False)
        frame[~frame.record_id.isin(provisional.record_id)].to_csv(ROOT/'01_논문원문과데이터/processed/pilot100/held_for_review.csv',index=False)
        checked.to_csv(ROOT/'01_논문원문과데이터/processed/context_v2/provisional_enriched.csv',index=False)
        status_path=ROOT/'01_논문원문과데이터/processed/pilot100/current_status.json'
        status=json.loads(status_path.read_text(encoding='utf-8'))
        status['phase_v4']=report
        status_path.write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
