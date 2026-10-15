"""Transcribe reported table values; excerpt evidence stays outside model input."""
import hashlib
import json
from pathlib import Path
import pandas as pd
from ree_research.schema import prepare

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw/elsevier_expansion'


def main():
    groups = {}
    def add(doi, sample, value, table, snapshot, composition=None, **fields):
        source = RAW / snapshot
        if not source.exists():
            raise ValueError(f'Missing source snapshot: {source}')
        row = dict(composition or {})
        row.update(record_id=hashlib.sha256(f'{doi}|{table}|{sample}'.encode()).hexdigest()[:20],
                   paper_id=doi, doi=doi, sample_id=sample, icorr_A_cm2=value*1e-6,
                   original_icorr_value=value, original_icorr_unit='uA/cm2',
                   source_locator=f'{table};{sample}',
                   evidence_quote=f'{table}; {sample}; reported Icorr = {value} uA/cm2',
                   source_file=str(source), source_url='https://doi.org/'+doi,
                   source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                   retrieval_provider='publisher_search_excerpt',
                   extraction_method='agent_table_transcription',
                   evidence_match='table_cell_transcription_not_literal_quote',
                   review_status='pending', review_flag='full_source_required',
                   quality_hold_reason='publisher_excerpt_requires_full_source_review',
                   icorr_method_cat='Tafel_extrapolation')
        row.update(fields)
        groups.setdefault(doi, []).append(row)

    doi='10.1016/j.corcom.2022.06.004'
    # Table 1 column order is C, Si, Mn, Cr, S, P, RE, Fe. Do not swap P/S.
    composition={
        'GCr15':dict(C=.95,Si=.178,Mn=.285,Cr=1.50,S=.003,P=.006,RE_element_cat='none'),
        'R-GCr15':dict(C=.91,Si=.174,Mn=.282,Cr=1.49,S=.003,P=.006,RE_element_cat='La+Ce'),
    }
    for condition,values in [('hot_rolled',[4.20,3.17]),('annealed',[3.24,2.08]),('quenched_tempered',[6.82,5.35])]:
        for sample,value in zip(composition,values):
            add(doi,sample+'_'+condition,value,'Table 4','publisher_search_evidence.json',
                composition[sample],chloride_mol_L=.1,electrolyte_condition_cat='NaCl_0.1mol_L',
                heat_treatment_cat=condition,reference_electrode_cat='Ag_AgCl',
                composition_locator='Table 1',condition_locator='section 3.3;Table 4',
                composition_source_file=str(RAW/'gcr15_composition_provenance.json'),
                notes='Room temperature not quantified. Table 1 RE dash is not converted to measured zero. RE addition 0.003 wt.% is not assumed to be retained RE. Full original still required.')

    doi='10.1016/j.jmrt.2025.01.207'
    for sample,value,c in [
        ('0RE',2.98,dict(C=.06,Mn=1.43,Si=.36,S=.004,P=.003,Ni=.70,Cu=.41,Cr=.51,Nb=.03,RE_ppm=0,RE_element_cat='none')),
        ('0.09RE',3.377,dict(C=.07,Mn=1.49,Si=.38,S=.002,P=.003,Ni=.69,Cu=.41,Cr=.52,Nb=.04,RE_ppm=930,RE_element_cat='La+Ce')),
        ('0.18RE',3.603,dict(C=.07,Mn=1.52,Si=.39,S=.002,P=.003,Ni=.71,Cu=.42,Cr=.51,Nb=.04,RE_ppm=1800,RE_element_cat='La+Ce'))]:
        add(doi,sample,value,'Table 3','lace_table3_snapshot.json',c,pH=4,
            electrolyte_condition_cat='NaCl_concentration_conflict',
            reference_electrode_cat='SCE',matrix_family_reported='bainite',
            composition_locator='Table 1',condition_locator='section 3.2;Fig.10',
            notes='CONFLICT: polarization text says 0.5 wt.% NaCl, Fig.10 caption says 3.5%; concentration left missing. Narrative calls 0.09RE lowest current, but Table 3 gives 0RE lower. Preserve table values; requires full source and author clarification.')

    doi='10.1016/j.jmrt.2023.12.189'
    for hours,value in [(1,9.73),(3,8.87),(5,6.95)]:
        add(doi,f'0.2Y_hold_{hours}h',value,'Table 4','publisher_tables_snapshot.json',
            original_icorr_value=value*1e-6,original_icorr_unit='A/cm2',
            evidence_quote=f'Table 4; {hours}h; Icorr = {value} +/- 0.02 x 10^-6 A/cm2',
            heat_treatment_temperature_C=800,heat_treatment_duration_h=hours,
            RE_element_cat='Y',electrolyte_condition_cat='simulated_seawater',
            reference_electrode_cat='SCE',composition_locator='Table 1',
            notes='Table 1 reports censored/ranged core compositions; leave them missing. 0.2Y is a sample name, not measured Y wt.%. Holding time is heat treatment, not corrosion exposure. Full source and baseline condition mapping required.')
    # Keep six Table 6 results in a separate candidate ledger: other conditions and
    # possible repeated baselines are not established; do not inflate unique count.
    candidates=[('pH_5',8.37),('pH_8',5.93),('scan_0.2mV_s',3.15),
                ('scan_0.5mV_s',3.37),('25C',4.59),('35C',6.83)]
    pd.DataFrame([dict(doi=doi,source_locator='Table 6;'+setting,
                       reported_setting=setting,icorr_A_cm2=value*1e-6,
                       status='not_merged_condition_and_baseline_mapping_required')
                  for setting,value in candidates]).to_csv(RAW/'unmerged_table6_candidates.csv',index=False)

    for doi,rows in groups.items():
        frame=pd.DataFrame(rows)
        prepare(frame,allowed_review_statuses=('pending',))
        out=ROOT/'data/processed/extractions'/('elsevier_'+doi.rsplit('/',1)[-1])
        out.mkdir(exist_ok=True,parents=True)
        frame.to_csv(out/'pending_measurements.csv',index=False)
        (out/'run.json').write_text(json.dumps(dict(rows=len(frame),method='publisher_search_excerpt_table_transcription',usage={},human_verified=False),indent=2),encoding='utf-8')
    # Keep source-stage caution reproducible when rebuilding the mixed collection.
    springer=ROOT/'data/processed/extractions/springer_s42243-025-01553-x/pending_measurements.csv'
    if springer.exists():
        frame=pd.read_csv(springer)
        frame['quality_hold_reason']='LF_stage_composition_used_for_CC_test_requires_review'
        frame.to_csv(springer,index=False)
    print(f'{sum(map(len,groups.values()))} pending Elsevier table points; all held; 6 additional Table 6 candidates not merged')


if __name__=='__main__':main()
