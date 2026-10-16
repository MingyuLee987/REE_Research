"""Append 30 source-reported points, keeping 23 explicitly held from modeling.

This is a dated, reproducible transcription batch, not a human verification.
AH36's printed A/cm2 values are preserved literally and MUST NOT enter training.
"""
import hashlib
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/raw/add30_20261016'
OUT = ROOT / 'data/processed/add30_20261016'


def save(name, rows, source_file, method, usage=None):
    source_file = Path(source_file)
    for row in rows:
        row.update(record_id=hashlib.sha256((row['doi'] + '|' + row['sample_id']).encode()).hexdigest()[:20],
            paper_id=row['doi'], review_status='pending', source_file=str(source_file.relative_to(ROOT)),
            source_sha256=hashlib.sha256(source_file.read_bytes()).hexdigest(),
            extraction_method=method, review_flag='needs_independent_source_review',
            evidence_match='visual_or_primary_excerpt_transcription_not_exact_text_validation')
        row.setdefault('source_url', 'https://doi.org/' + row['doi'])
    folder = ROOT / 'data/processed/extractions' / ('add30_' + name)
    folder.mkdir(parents=True, exist_ok=True)
    if (folder / 'run.json').exists() and not (folder / 'text_extraction_run.json').exists():
        (folder / 'text_extraction_run.json').write_bytes((folder / 'run.json').read_bytes())
    pd.DataFrame(rows).to_csv(folder / 'pending_measurements.csv', index=False)
    (folder / 'run.json').write_text(json.dumps(dict(rows=len(rows), method=method,
        source=str(source_file.relative_to(ROOT)), usage=usage or {}, human_verified=False), indent=2), encoding='utf-8')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    baseline = ROOT / 'data/processed/pilot100/llm_pending_all.csv'
    backup = OUT / 'baseline_189.csv'
    if not backup.exists():
        previous = pd.read_csv(baseline)
        if len(previous) != 189:
            raise ValueError('Unexpected baseline; review before changing the dated batch')
        backup.write_bytes(baseline.read_bytes())

    # PDF Table 3 is visually legible but its text encoding is broken. Check with Sol image input.
    check = json.loads((SOURCE / 'ah36/table3_check.json').read_text())
    if not check['all_values_match'] or check['unit_validated']:
        raise ValueError('Expected printed-value check plus unresolved unit flag')
    compositions = [dict(C=.11, Si=.24, Mn=1.40, Cr=.11, Al=.03, RE_ppm=0),
                    dict(C=.10, Si=.25, Mn=1.45, Cr=.11, Al=.03, RE_ppm=90),
                    dict(C=.12, Si=.24, Mn=1.39, Cr=.11, Al=.03, RE_ppm=340)]
    currents = [[2.463, 2.536, 3.482, 3.537, 2.652],
                [1.357, 1.984, 2.152, 2.409, 2.127],
                [2.289, 2.359, 2.365, 3.034, 2.209]]
    rows = []
    for i, (c, values) in enumerate(zip(compositions, currents), 1):
        for days, value in zip([3, 5, 7, 14, 21], values):
            rows.append(dict(c, doi='10.13228/j.boyuan.issn1006-9356.20240777',
                sample_id=f'AH36_No{i}_{days}d', RE_element_cat='none' if i == 1 else 'Ce',
                icorr_A_cm2=None, original_icorr_value=value, original_icorr_unit='A/cm2 (printed; scale unresolved)',
                target_unit_status='unresolved_as_printed_DO_NOT_TRAIN',
                electrolyte_condition_cat='NaCl_3.5wtpct', nacl_wt_pct=3.5,
                electrolyte_family_cat='NaCl', exposure_h=days*24, scan_rate_mV_s=.5,
                source_locator=f'page:6;Table 3;No.{i};{days}d',
                evidence_quote=f'Table 3: No.{i}; {days} d; Jcorr={value}; header Jcorr/(A cm^-2).',
                composition_locator='page:2;Table 1', condition_locator='page:3;section 1.2',
                quality_hold_reason='printed_current_density_scale_unresolved_DO_NOT_TRAIN',
                notes='Table 3 and abstract print A/cm2 without a multiplier. Figure 5 shows microamp-scale curves and Table 4 Rp is hundreds of ohm cm2; source-scale inconsistency. No missing exponent or micro-prefix has been guessed. Only original_icorr_value preserves the printed number; icorr_A_cm2 is deliberately empty and this record is blocked from model inputs. No human verification.'))
    save('ah36', rows, SOURCE/'ah36/article.pdf', 'agent_visual_table_plus_sol_image_numeric_check', check.get('usage'))

    # Full-width digits in PDF text prevented exact-fragment LLM validation; read the printed table.
    compositions = [dict(C=.0130, Si=.466, Mn=1.060, Nb=.052, Ti=.038, Cu=.665, Mo=.100, Ni=1.020, Al=.007, RE_ppm=0),
        dict(C=.0150, Si=.473, Mn=1.060, Nb=.052, Ti=.079, Cu=.666, Mo=.097, Ni=1.020, Al=.018, RE_ppm=14),
        dict(C=.0078, Si=.471, Mn=1.030, Nb=.055, Ti=.072, Cu=.649, Mo=.093, Ni=1.040, Al=.018, RE_ppm=25)]
    rows = []
    for i, (c, value) in enumerate(zip(compositions, [95.60, 74.50, 72.10]), 1):
        rows.append(dict(c, doi='10.19947/j.issn.1001-7208.2024.09.05', sample_id=f'Q370qNHY_No{i}_14d',
            RE_element_cat='none' if i == 1 else 'Ce', icorr_A_cm2=value*1e-6,
            original_icorr_value=value, original_icorr_unit='uA/cm2', target_unit_status='explicit_density_unit',
            electrolyte_condition_cat='NaCl_3.5wtpct', nacl_wt_pct=3.5, electrolyte_family_cat='NaCl',
            exposure_h=336, scan_rate_mV_s=.5, reference_electrode_cat='SCE',
            matrix_family_reported='ferrite_pearlite', icorr_method_cat='polarization_curve_fit',
            source_locator=f'page:5;Table 2;No.{i}', evidence_quote=f'Table 2: No.{i}; Icorr/(microA cm^-2) {value:.2f}; 14 d.',
            composition_locator='page:2;Table 1', condition_locator='page:2;section 1.2;page:5;Table 2 caption',
            notes='Printed Table 2 visually read; 1 microA/cm2=1e-6 A/cm2. Room temperature not assigned a numeric value. LLM text attempt failed exact-fragment validation; this is an explicit agent visual transcription. Check related Q370 bridge-steel material families together in future grouped validation; no new model test performed.'))
    save('ce_shanghai', rows, SOURCE/'ce_shanghai/article.pdf', 'agent_visual_table_transcription')

    # Primary publisher's indexed table, not a full-text API response. Unreported/ranged composition stays missing.
    folder = SOURCE/'ymarine_table6'; folder.mkdir(exist_ok=True)
    table = dict(doi='10.1016/j.jmrt.2023.12.189', source_url='https://doi.org/10.1016/j.jmrt.2023.12.189',
        retrieval='primary_ScienceDirect_indexed_table_excerpt', retrieved_date='2026-10-16',
        table='Table 6', unit='A/cm2',
        values={'pH5':8.37e-6,'pH8':5.93e-6,'scan0.2':3.15e-6,'scan0.5':3.37e-6,'T25':4.59e-6,'T35':6.83e-6},
        composition_note='Table 1 reports Y=0.3 wt% for sample 0.2Y; most other elements are ranges or upper limits.',
        condition_note='0.2Y selected for follow-up. Table 5 lists 0.8 mV/s, Table 6 lists 0.5 mV/s. Keep held.')
    evidence = folder/'primary_table_excerpt.json'; evidence.write_text(json.dumps(table, indent=2), encoding='utf-8')
    rows = []
    for label, value in table['values'].items():
        row = dict(doi=table['doi'], sample_id='0.2Y_Table6_'+label, RE_element_cat='Y', RE_ppm=3000, Al=.05,
            icorr_A_cm2=value, original_icorr_value=value, original_icorr_unit='A/cm2',
            target_unit_status='explicit_density_unit', electrolyte_condition_cat='simulated_seawater',
            electrolyte_family_cat='seawater', reference_electrode_cat='SCE',
            source_locator='Table 6;'+label, evidence_quote=f'Table 6; {label}; Icorr={value:g} A/cm2.',
            composition_locator='Table 1;0.2Y', condition_locator='Experimental;Table 6',
            quality_hold_reason='primary_excerpt_only_composition_ranges_and_condition_mapping_require_fulltext_review',
            notes='Source-reported mean, not independent replicates. Additional conditions from an existing paper, distinct from its already stored Table 4 heat-treatment rows. Do not substitute range midpoints or upper bounds as measured compositions. Scan label conflict between Table 5 and Table 6. No unstated common temperature, pH, exposure or heat treatment assigned. Not human verified.')
        if label.startswith('pH'): row['pH']=float(label[2:])
        elif label.startswith('scan'): row['scan_rate_mV_s']=float(label[4:])
        else: row['temperature_C']=float(label[1:])
        rows.append(row)
    save('ymarine_table6', rows, evidence, 'primary_publisher_indexed_table_transcription')

    folder = SOURCE/'windtower'; folder.mkdir(exist_ok=True)
    evidence = folder/'primary_abstract_excerpt.json'
    evidence.write_text(json.dumps(dict(doi='10.1016/j.jmrt.2026.03.287',
        source_url='https://www.sciencedirect.com/science/article/pii/S2238785426007799',
        retrieval='primary_ScienceDirect_indexed_abstract', retrieved_date='2026-10-16',
        base_icorr_A_cm2=4.13e-5, RE_icorr_A_cm2=2.35e-5, measured_rolled_RE_wt_pct=.0098,
        note='Only abstract is available; no composition/condition values inferred.'), indent=2), encoding='utf-8')
    rows = []
    for label, value, ppm in [('base',4.13e-5,0),('RE',2.35e-5,98)]:
        rows.append(dict(doi='10.1016/j.jmrt.2026.03.287',sample_id='Q355_windtower_'+label,
            RE_ppm=ppm, RE_element_cat='none' if label=='base' else 'RE_unspecified',
            icorr_A_cm2=value,original_icorr_value=value,original_icorr_unit='A/cm2',
            target_unit_status='explicit_density_unit',source_locator='Abstract;'+label,
            evidence_quote=f'Abstract; {label}; corrosion current density {value:g} A cm^-2.',
            quality_hold_reason='abstract_only_composition_and_test_conditions_unavailable',
            notes='Primary publisher abstract reports measured rolled RE .0098 wt%, distinct from wire feed .010 wt%. Full experimental composition and electrochemical conditions unavailable. Do not assign NaCl concentration, time, temperature or elemental RE species. Not human verified.'))
    save('windtower',rows,evidence,'primary_publisher_abstract_numeric_transcription')

    # Includes the four already extracted met0066 points, excludes zero-result source runs.
    frames=[]
    for p in sorted((ROOT/'data/processed/extractions').glob('add30_*/run.json')):
        run=json.loads(p.read_text())
        if run['rows']:
            frame=pd.read_csv(p.parent/'pending_measurements.csv');frame['extraction_source']=p.parent.name
            frames.append(frame)
    new=pd.concat(frames,ignore_index=True)
    if len(new)!=30 or new.record_id.duplicated().any():
        raise ValueError('Dated batch must contain 30 unique reported points')
    if set(new.record_id)&set(pd.read_csv(backup).record_id):
        raise ValueError('Record overlaps the baseline')
    new.to_csv(OUT/'new_measurements_pending.csv',index=False)
    print('30 source-reported points prepared: 7 provisional candidates, 23 held; NONE human verified')


def report():
    from ree_research.schema import prepare
    whole=pd.read_csv(ROOT/'data/processed/pilot100/llm_pending_all.csv')
    new=whole[whole.extraction_source.str.startswith('add30_')]
    old=pd.read_csv(OUT/'baseline_189.csv').set_index('record_id')
    current=whole.set_index('record_id')
    if len(whole)!=219 or len(new)!=30 or not whole.record_id.is_unique:
        raise ValueError('Unexpected merged collection size or duplicate record IDs')
    for field in ['paper_id','sample_id','icorr_A_cm2','review_status']:
        if not old[field].fillna('').astype(str).eq(current.loc[old.index,field].fillna('').astype(str)).all():
            raise ValueError('A baseline measurement changed')
    provisional=pd.read_csv(ROOT/'data/processed/pilot100/provisional_for_model.csv')
    held=whole[whole.hold_reason.notna()]
    if len(provisional)!=142 or provisional.record_id.isin(held.record_id).any():
        raise ValueError('Held records leaked into model candidates')
    if new.icorr_A_cm2.isna().sum()!=15 or not whole.review_status.eq('pending').all():
        raise ValueError('Unresolved unit/status handling changed')
    context=pd.read_csv(ROOT/'data/processed/context_v2/provisional_enriched.csv')
    features=prepare(context,allowed_review_statuses=('pending',))
    features.to_csv(ROOT/'data/processed/context_v2/features_v3_pending.csv',index=False)
    features.to_csv(OUT/'features_pending.csv',index=False)
    new.to_csv(OUT/'new_measurements_pending.csv',index=False)
    new[new.hold_reason.isna()].to_csv(OUT/'new_provisional.csv',index=False)
    new[new.hold_reason.notna()].to_csv(OUT/'new_held.csv',index=False)
    status=dict(date='2026-10-16',previous_records=189,new_reported_records=30,
        new_density_values_with_explicit_units=15,new_unresolved_unit_records=15,
        new_provisional_candidates=7,new_held=23,total_records=len(whole),total_papers=int(whole.paper_id.nunique()),
        normalized_target_present=int(whole.icorr_A_cm2.notna().sum()),
        provisional_candidates=len(provisional),held=len(held),human_verified=0,
        primary_current_csv_updated=True,primary_current_csv_records=len(whole),
        target_300_shortfall_records=max(0,300-len(whole)),
        target_300_shortfall_nonmissing_density=max(0,300-int(whole.icorr_A_cm2.notna().sum())),
        notes='219 source-reported collection records, NOT 219 validated icorr values. AH36 15 normalized targets deliberately empty.',
        sources=[dict(doi=doi,records=len(g),held=int(g.hold_reason.notna().sum())) for doi,g in new.groupby('doi')],
        merged_sha256=hashlib.sha256((ROOT/'data/processed/pilot100/llm_pending_all.csv').read_bytes()).hexdigest())
    (OUT/'status.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
    print(json.dumps(status,indent=2))


if __name__=='__main__':
    import sys
    report() if '--report' in sys.argv else main()
