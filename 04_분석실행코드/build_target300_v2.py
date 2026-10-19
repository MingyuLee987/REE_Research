"""Append source-supported new experiments and export an <=80%-missing ML view."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from ree_research.schema import ALL_FEATURES, FEATURE_PROFILES, COMPOSITION, prepare
from ree_research.benchmark import selected_features
if __package__:
    from .normalize_dataset_units import normalize
else:
    from normalize_dataset_units import normalize

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'01_논문원문과데이터/processed/target300_v2'
MASTER=ROOT/'01_논문원문과데이터/processed/pilot100/llm_pending_all.csv'
NAMES=['q355nhq','75industrial','amorphous_ce_dy']


def main():
    OUT.mkdir(exist_ok=True)
    current=pd.read_csv(MASTER)
    backup=OUT/'baseline_before_append.csv'
    if not backup.exists():current.to_csv(backup,index=False)
    additions=[]
    for name in NAMES:
        path=ROOT/'01_논문원문과데이터/processed/extractions'/('target300v2_'+name)/'pending_measurements.csv'
        data=pd.read_csv(path)
        data['extraction_source']='target300v2_'+name
        data['hold_reason']=np.nan
        data['original_icorr_value']=data.icorr_value
        data['original_icorr_unit']=data.icorr_unit
        data['target_unit_status']='explicit_density_unit_pending_review'
        data['reported_composition_count']=data.reindex(columns=COMPOSITION).notna().sum(axis=1)
        if name=='q355nhq':
            data['paper_title']='Effect of Rare Earth Lanthanum and Cerium on Corrosion Behavior of Q355NHq Steel in Simulated Marine Atmosphere Environment'
            expected={'Base':4.39e-5,'RE90':3.94e-5,'RE170':2.25e-5,'RE280':3.63e-5}
            np.testing.assert_allclose(data.icorr_A_cm2,data.sample_id.map(expected),rtol=1e-10)
            data['matrix_family_reported']='ferrite_pearlite'
            data['matrix_phase_reported']='ferrite and pearlite'
            data['phase_evidence_type']='pre_corrosion_characterization'
            data['phase_source_locator']='page:2;Figure 1;section 1.1'
            data['phase_evidence_quote']='其显微组织均为铁素体+珠光体'
            data['nacl_wt_pct']=3.5
            data['scan_rate_mV_s']=.33
            data['ocp_stabilization_min']=30
            data['reference_electrode_cat']='Ag/AgCl'
            data['surface_finish_grit']=2000
        elif name=='75industrial':
            data['paper_title']='Industrial experimental on inclusion characteristics and corrosion resistance of La-Ce treated 75Cr1 steel'
            np.testing.assert_allclose(data.icorr_A_cm2,data.sample_id.map({'C1':8.60e-5,'C2':2.05e-5}),rtol=1e-10)
            data['nacl_wt_pct']=3.5
            data['reference_electrode_cat']='SCE'
            data['notes']=data.notes+' Original Table 1 and Table 2 visually checked; laboratory Ce-only 75Cr1 study is distinct from this industrial La-Ce production trial. Group related 75Cr1 publications in future validation; reuse still requires human review.'
        else:
            data['paper_title']='Effect of Rare Earth Elements Addition on Corrosion Behavior of Fe-based Amorphous Composites'
            # Source gives nominal charge chemistry only; never silently promote it to measured bulk values.
            data['nominal_composition_wtpct']='Fe balance; Mn15; Si5; Cr14; C0.2; Ce1.0'
            data['nominal_RE_wtpct']=1.
            for column in COMPOSITION+['RE_ppm']:data[column]=np.nan
            data['reported_composition_count']=0
            data['hold_reason']='nominal_charge_composition_only_final_bulk_chemistry_unreported'
            data['quality_hold_reason']=data.hold_reason
            data['notes']=data.notes+' Nominal chemistry retained separately, not assigned as final measured composition; held from modeling. Bulk cast rod, not a surface coating.'
        data['review_status']='pending'
        data['review_flag']='needs_independent_source_review'
        additions.append(data)
    batch=pd.concat(additions,ignore_index=True)
    assert batch.record_id.is_unique
    new=batch[~batch.record_id.isin(current.record_id)].copy()
    # Reject rather than silently add renamed specimens from papers already in the master.
    if new.doi.str.lower().isin(current.doi.str.lower()).any():
        raise ValueError('Existing-paper experiments require manual specimen/condition deduplication')
    merged=pd.concat([current,new],ignore_index=True)
    pd.testing.assert_frame_equal(current,merged.iloc[:len(current)][current.columns].reset_index(drop=True),check_dtype=False)
    merged=normalize(merged)
    assert merged.record_id.is_unique
    eligible=merged[merged.hold_reason.isna()|merged.hold_reason.eq('')].copy()
    checked=prepare(eligible,('pending',))
    held=merged[~merged.record_id.isin(eligible.record_id)]
    numeric,categorical=selected_features(checked,'ml80',.2)
    selected=numeric+categorical
    coverage=[]
    for feature in ALL_FEATURES:
        present=checked[feature].notna()
        coverage.append(dict(feature=feature,observed=int(present.sum()),missing_rate=float(1-present.mean()),
            supporting_papers=int(checked.loc[present,'paper_id'].nunique()),distinct_values=int(checked[feature].nunique()),
            selected_for_ml80=feature in selected))
    cov=pd.DataFrame(coverage)
    assert (cov.loc[cov.selected_for_ml80,'missing_rate']<=.8+1e-12).all()
    batch.to_csv(OUT/'new_observations.csv',index=False)
    merged.to_csv(OUT/'llm_pending_all.csv',index=False)
    checked.to_csv(OUT/'features_pending.csv',index=False)
    checked[['record_id','paper_id','doi','sample_id','review_status']+selected+['icorr_A_cm2','target']].to_csv(OUT/'ml_input_max80_missing.csv',index=False)
    cov.to_csv(OUT/'feature_coverage.csv',index=False)
    pd.DataFrame({'record_id':checked.record_id,'missing_feature_count':checked[selected].isna().sum(axis=1),
        'missing_feature_rate':checked[selected].isna().mean(axis=1)}).to_csv(OUT/'sample_missingness.csv',index=False)
    report=dict(total_records=len(merged),total_papers=int(merged.paper_id.nunique()),target_records=300,
        shortfall=max(0,300-len(merged)),newly_appended=len(new),batch_records=len(batch),batch_papers=3,
        provisional_records=len(checked),held_records=len(held),normalized_target_present=int(merged.icorr_A_cm2.notna().sum()),
        unresolved_targets=int(merged.icorr_A_cm2.isna().sum()),candidate_features=sum(map(len,FEATURE_PROFILES['ml80'])),
        selected_features=len(selected),numeric_features=len(numeric),categorical_features=len(categorical),
        selected_feature_names=selected,feature_max_missing_rate=.8,min_supporting_papers=2,human_verified=0,
        note='Coverage report is descriptive, not a fixed validation feature list. Select features inside training folds. No new model scores.')
    (OUT/'status.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    # Validation above completes before publication; preserve a full backup.
    merged.to_csv(MASTER,index=False)
    checked.to_csv(ROOT/'01_논문원문과데이터/processed/pilot100/provisional_for_model.csv',index=False)
    held.to_csv(ROOT/'01_논문원문과데이터/processed/pilot100/held_for_review.csv',index=False)
    checked.to_csv(ROOT/'01_논문원문과데이터/processed/context_v2/provisional_enriched.csv',index=False)
    status_path=ROOT/'01_논문원문과데이터/processed/pilot100/current_status.json'
    status=json.loads(status_path.read_text(encoding='utf-8'))
    status.update(extracted_rows=len(merged),extracted_papers=int(merged.paper_id.nunique()),provisional_rows=len(checked),
        provisional_papers=int(checked.paper_id.nunique()),held_rows=len(held),shortfall_to_target=report['shortfall'],
        normalized_target_present_rows=report['normalized_target_present'],normalized_target_missing_rows=report['unresolved_targets'],latest_target300_v2=report)
    status_path.write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
