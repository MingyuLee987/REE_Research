"""Append six original-table observations without rebuilding historical extractions."""
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from ree_research.schema import prepare, COMPOSITION

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/processed/expand_20261016'
MASTER=ROOT/'data/processed/pilot100/llm_pending_all.csv'


def main():
    OUT.mkdir(exist_ok=True)
    baseline=OUT/'baseline_before_append.csv'
    if not baseline.exists():baseline.write_bytes(MASTER.read_bytes())
    current=pd.read_csv(MASTER)
    records=[]
    items=[('hrb400','10.20057/j.1003-8620.2024-00280',
        'Effect of Rare Earth Content on Microstructure and Corrosion Resistance of HRB400 Steel',
        ['0RE','0.003RE','0.010RE'],[7.612,4.937,4.727],1e-6,[0,30,100]),
        ('steel75cr1','10.11900/0412.1961.2022.00359',
        'Effect of Ce on Cleanliness, Microstructure, and Pitting Corrosion Resistance of 75Cr1 Steel',
        ['C1','C3','C5'],[8.53,4.03,5.07],1e-5,[0,195,416])]
    for name,doi,title,samples,values,scale,re_ppm in items:
        source=ROOT/'data/raw/expand_20261016'/name/'article.pdf'
        table,page=('Table 4',5) if name=='hrb400' else ('Table 2',8)
        unit='10^-6 A/cm2' if name=='hrb400' else '10^-5 A/cm2 (individual printed exponent)'
        for i,(sample,value,re_value) in enumerate(zip(samples,values,re_ppm)):
            rid=hashlib.sha256((doi+'|'+sample+'|'+table).encode()).hexdigest()[:20]
            row=dict(record_id=rid,paper_id=doi,doi=doi,sample_id=sample,paper_title=title,
                review_status='pending',review_flag='needs_independent_source_review',
                icorr_A_cm2=value*scale,original_icorr_value=value,original_icorr_unit=unit,
                target_unit_status='explicit_density_unit',RE_ppm=re_value,
                RE_element_cat='none' if i==0 else ('La+Ce' if name=='hrb400' else 'Ce'),
                electrolyte_condition_cat='NaCl_3.5wtpct',electrolyte_family_cat='NaCl',nacl_wt_pct=3.5,
                reference_electrode_cat='SCE',source_file=str(source.relative_to(ROOT)),
                source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),source_url='https://doi.org/'+doi,
                source_locator=f'page:{page};{table};{sample}',
                evidence_quote=f'{table}; {sample}; icorr={value} x {scale:g} A/cm2; printed header/row visually checked.',
                extraction_method='agent_original_pdf_table_transcription_with_separate_sol_extraction',
                extraction_source='expand_20261016_'+name,hold_reason=np.nan,
                notes='No human verification. Original PDF target table visually read; no curve digitization or replication of reported means.')
            if name=='hrb400':
                row.update(C=[.11,.10,.11][i],Si=[.38,.39,.42][i],Mn=[1.29,1.30,1.29][i],
                    Cu=[.28,.28,.29][i],Cr=[.92,.89,.90][i],V=[.022,.023,.027][i],
                    scan_rate_mV_s=1,grain_size_um=[19.9,17.5,15.5][i],
                    matrix_family_reported='ferrite_pearlite',matrix_phase_reported='ferrite and pearlite',
                    phase_evidence_type='pre_corrosion_characterization',
                    phase_context_status='source_evidenced_pending_review',
                    phase_source_locator='page:2;section 2.1;Figure 2',
                    phase_evidence_quote='主要为铁素体和珠光体',
                    composition_locator='page:2;Table 2',condition_locator='page:2;section 1;page:5;Figure 6',
                    heat_treatment_cat='hot_rolled_air_cooled')
                row['notes']+=' Table 2 gives sample-specific bulk compositions. RE blend La:Ce=3:1; individual final element concentrations not inferred. Temperature, pH, exposure duration not assigned from unspecified conditions.'
            else:
                row.update(hold_reason='final_bulk_major_composition_not_reported_feedstock_only',
                    quality_hold_reason='final_bulk_major_composition_not_reported_feedstock_only',
                    composition_locator='page:2;ICP-AES Ce analysis',condition_locator='page:3;electrochemical method')
                row['notes']+=' Major-element chemistry is reported for starting slab only and is not transferred to remelted final specimens. Final measured Ce: C1=0, C3=0.0195 wt%, C5=0.0416 wt%. High-temperature austenite characterization is not assigned as room-temperature matrix. Hold from modeling until composition correspondence is resolved.'
            row['reported_composition_count']=sum(pd.notna(row.get(c)) for c in COMPOSITION)
            records.append(row)
    added=pd.DataFrame(records)
    assert added.record_id.is_unique
    for name,doi,*_ in items:
        sol=pd.read_csv(ROOT/'data/processed/extractions'/('expand_20261016_'+name)/'pending_measurements.csv')
        manual=added[added.doi.eq(doi)].set_index('sample_id')
        sol=sol.set_index('sample_id').loc[manual.index]
        np.testing.assert_allclose(sol.icorr_A_cm2,manual.icorr_A_cm2,rtol=1e-10)
        np.testing.assert_allclose(sol.RE_ppm,manual.RE_ppm,rtol=1e-10)
    # Rerun only appends genuinely new IDs; existing edits are never overwritten.
    to_add=added[~added.record_id.isin(current.record_id)].copy()
    new_dois=set(to_add.doi)-set(current.doi)
    if len(to_add) and len(new_dois)!=to_add.doi.nunique():
        raise ValueError('DOI already present: inspect specimen duplication before appending')
    merged=pd.concat([current,to_add],ignore_index=True)
    pd.testing.assert_frame_equal(merged.iloc[:len(current)].reset_index(drop=True)[current.columns],
        current.reset_index(drop=True),check_dtype=False)
    assert merged.record_id.is_unique
    provisional=merged[merged.hold_reason.isna()|merged.hold_reason.eq('')].copy()
    checked=prepare(provisional,('pending',))
    held=merged[~merged.record_id.isin(checked.record_id)].copy()
    added.to_csv(OUT/'new_observations.csv',index=False)
    checked.to_csv(OUT/'features_pending.csv',index=False)
    merged.to_csv(OUT/'llm_pending_all.csv',index=False)
    checked.to_csv(OUT/'provisional_for_model.csv',index=False)
    held.to_csv(OUT/'held_for_review.csv',index=False)
    # All validation completes before updating current files.
    published=False
    try:
        merged.to_csv(MASTER,index=False)
        checked.to_csv(ROOT/'data/processed/pilot100/provisional_for_model.csv',index=False)
        held.to_csv(ROOT/'data/processed/pilot100/held_for_review.csv',index=False)
        checked.to_csv(ROOT/'data/processed/context_v2/provisional_enriched.csv',index=False)
        published=True
    except PermissionError:
        print('Current CSV locked; complete expansion snapshot saved separately. Close the file and rerun.')
    report=dict(total_records=len(merged),total_papers=int(merged.paper_id.nunique()),
        batch_records=len(added),newly_appended=len(to_add),batch_papers=2,
        provisional_records=len(checked),provisional_papers=int(checked.paper_id.nunique()),held_records=len(held),
        normalized_target_present=int(merged.icorr_A_cm2.notna().sum()),human_verified=0,
        historical_values_changed=0,previous_model_scores_not_recomputed=True,current_master_updated=published)
    (OUT/'status.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    status_path=ROOT/'data/processed/pilot100/current_status.json'
    status=json.loads(status_path.read_text(encoding='utf-8'))
    status.update(extracted_rows=len(merged),extracted_papers=int(merged.paper_id.nunique()),
        provisional_rows=len(checked),provisional_papers=int(checked.paper_id.nunique()),held_rows=len(held),
        normalized_target_present_rows=int(merged.icorr_A_cm2.notna().sum()),
        normalized_target_missing_rows=int(merged.icorr_A_cm2.isna().sum()),shortfall_to_target=max(0,300-len(merged)),
        latest_expansion=report)
    if published:status_path.write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
