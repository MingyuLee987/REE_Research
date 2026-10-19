"""Standardize current-density columns, preserving original numbers and uncertainty."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from ree_research.schema import prepare

ROOT=Path(__file__).resolve().parents[1]
FACTORS={'A/cm2':1.,'uA/cm2':1e-6,'mA/cm2':1e-3,'1e-6 A/cm2':1e-6,
    '1e-7 A/cm2':1e-7,'10^-6 A/cm2':1e-6,
    '10^-5 A/cm2 (individual printed exponent)':1e-5}
UNITS={**{f:'wt.%' for f in ['C','Si','Mn','P','S','Cr','Ni','Mo','Cu','Al','N','Nb','Ti','V','W','Sb']},
    'RE_ppm':'mass ppm','temperature_C':'degC','heat_treatment_temperature_C':'degC',
    'exposure_h':'h','heat_treatment_duration_h':'h','ocp_stabilization_min':'min',
    'scan_rate_mV_s':'mV/s','nacl_wt_pct':'wt.% NaCl','chloride_mol_L':'mol/L chloride',
    'grain_size_um':'um','pH':'dimensionless', 'icorr_value':'A/cm2','icorr_unit':'unit label',
    'icorr_A_cm2':'A/cm2','target':'log10(icorr / [A/cm2])',
    'RE_log1p_ppm':'ln(1 + RE_ppm / [mass ppm])',
    **{f+'_fraction_reported_pct':'reported %; retain source area/volume basis' for f in
       ['austenite','ferrite','martensite','bainite','pearlite']}}


def normalize(frame):
    result=frame.copy()
    # Migrate legacy source numbers before replacing the generic display columns.
    result['original_icorr_value']=result.original_icorr_value.combine_first(result.icorr_value)
    result['original_icorr_unit']=result.original_icorr_unit.combine_first(result.icorr_unit)
    factor=result.original_icorr_unit.map(FACTORS)
    converted=pd.to_numeric(result.original_icorr_value,errors='raise')*factor
    known=result.icorr_A_cm2.notna()
    if (known & converted.isna()).any():raise ValueError('Existing target lacks a recognized explicit original unit')
    if not np.allclose(converted[known],result.loc[known,'icorr_A_cm2'],rtol=1e-7,atol=0):
        raise ValueError('Original number/unit disagrees with target; source review required')
    result['unit_conversion_factor_to_A_cm2']=factor.where(known)
    result['unit_check_status']=np.where(known,'original_pair_matches_A_cm2_pending_human_review',
        'unresolved_scale_no_conversion_DO_NOT_TRAIN')
    result['icorr_value']=result.icorr_A_cm2
    result['icorr_unit']=pd.Series(np.where(known,'A/cm2',None),index=result.index)
    # The target and every prior hold are preserved, including 15 uncertain printed scales.
    pd.testing.assert_series_equal(result.icorr_A_cm2,frame.icorr_A_cm2)
    pd.testing.assert_series_equal(result.hold_reason,frame.hold_reason)
    return result


def main():
    out=ROOT/'01_논문원문과데이터/processed/units_v1';out.mkdir(exist_ok=True)
    master=ROOT/'01_논문원문과데이터/processed/pilot100/llm_pending_all.csv'
    current=pd.read_csv(master)
    expansion=pd.read_csv(ROOT/'01_논문원문과데이터/processed/expand_20261016/llm_pending_all.csv')
    # Current manual edits take precedence; expansion only supplies previously absent IDs.
    frame=pd.concat([current,expansion[~expansion.record_id.isin(current.record_id)]],ignore_index=True)
    assert frame.record_id.is_unique
    backup=out/'before_unit_normalization.csv'
    if not backup.exists():frame.to_csv(backup,index=False)
    result=normalize(frame)
    result.to_csv(out/'llm_pending_all.csv',index=False)
    provisional=result[result.hold_reason.isna()|result.hold_reason.eq('')].copy()
    features=prepare(provisional,('pending',))
    held=result[~result.record_id.isin(provisional.record_id)]
    features.to_csv(out/'features_pending.csv',index=False)
    provisional.to_csv(out/'provisional_for_model.csv',index=False)
    held.to_csv(out/'held_for_review.csv',index=False)
    (out/'column_units.json').write_text(json.dumps(UNITS,ensure_ascii=False,indent=2),encoding='utf-8')
    report=dict(records=len(result),papers=int(result.paper_id.nunique()),
        explicitly_converted_and_checked=int(result.icorr_A_cm2.notna().sum()),
        unresolved_target_scale=int(result.icorr_A_cm2.isna().sum()),target_values_changed=0,
        generic_icorr_columns_standardized=True,human_verified=False,published_paths=[],locked_paths=[])
    paths={master:result,
        ROOT/'01_논문원문과데이터/processed/pilot100/provisional_for_model.csv':features,
        ROOT/'01_논문원문과데이터/processed/pilot100/held_for_review.csv':held,
        ROOT/'01_논문원문과데이터/processed/expand_20261016/llm_pending_all.csv':result}
    # Do not publish a split independently when its master is locked.
    try:
        result.to_csv(master,index=False)
        report['published_paths'].append(str(master.relative_to(ROOT)))
    except PermissionError:report['locked_paths'].append(str(master.relative_to(ROOT)))
    for path,data in paths.items():
        if path==master:continue
        if path.parent.name=='pilot100' and report['locked_paths']:continue
        try:data.to_csv(path,index=False);report['published_paths'].append(str(path.relative_to(ROOT)))
        except PermissionError:report['locked_paths'].append(str(path.relative_to(ROOT)))
    (out/'status.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
