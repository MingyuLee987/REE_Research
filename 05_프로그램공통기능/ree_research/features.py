"""Deterministic input-only descriptors; never infer unreported measurements."""
import re
import numpy as np
import pandas as pd

ENGINEERED_NUMERIC = ['temperature_inverse_1000K', 'chloride_log1p_mol_L',
    'scan_rate_log1p_mV_s', 'heat_treatment_log1p_h', 'Cr_Mo_sum_wtpct',
    'RE_log1p_x_Cr', 'RE_log1p_x_Mo', 'nacl_reported_log1p_wtpct']
ENGINEERED_CATEGORICAL = ['electrolyte_group', 'matrix_group', 'heat_treatment_group']


def _text(value):
    return '' if pd.isna(value) else str(value).strip().lower()


def electrolyte_group(value):
    text=_text(value)
    if not text:return np.nan
    if 'conflict' in text:return np.nan
    if 'soil' in text:return 'soil_simulant'
    if 'seawater' in text:return 'alkaline_seawater' if 'naoh' in text or 'alkaline' in text else 'seawater'
    if 'nahso3' in text:return 'bisulfite_solution'
    if 'nacl' in text:
        return 'mixed_chloride_solution' if '+' in text or 'cacl2' in text else 'NaCl_solution'
    return 'other_reported_medium'


def matrix_group(value):
    text=_text(value)
    if not text:return np.nan
    phases=[name for token,name in [('austenit','austenitic'),('martensit','martensitic'),
            ('ferrit','ferritic'),('bainit','bainitic'),('pearlit','pearlitic')] if token in text]
    if 'duplex' in text:return 'duplex'
    if len(phases)>1:return 'mixed_phase'
    return phases[0] if phases else 'other_reported_matrix'


def heat_treatment_group(value):
    text=_text(value)
    if not text:return np.nan
    if 'solution' in text:return 'solution_treated'
    if 'temper' in text:return 'tempered'
    if 'quench' in text:return 'quenched'
    if 'anneal' in text:return 'annealed'
    if 'hot_roll' in text:return 'hot_rolled'
    if 'untreated' in text:return 'untreated'
    return 'other_reported_process'


def engineer(df):
    """Called after schema validation; transformations propagate missing values."""
    result=df.copy()
    result['temperature_inverse_1000K']=1000/(result.temperature_C+273.15)
    result['chloride_log1p_mol_L']=np.log1p(result.chloride_mol_L)
    result['scan_rate_log1p_mV_s']=np.log1p(result.scan_rate_mV_s)
    result['heat_treatment_log1p_h']=np.log1p(result.heat_treatment_duration_h)
    result['Cr_Mo_sum_wtpct']=result.Cr+result.Mo
    result['RE_log1p_x_Cr']=result.RE_log1p_ppm*result.Cr
    result['RE_log1p_x_Mo']=result.RE_log1p_ppm*result.Mo
    # Accept only an explicitly labeled weight percentage, never bare '%' or g/L.
    def reported_nacl(value):
        match=re.search(r'(?:^|\+)NaCl_([0-9]+(?:\.[0-9]+)?)wtpct(?:$|\+)',str(value))
        return float(match.group(1)) if match else np.nan
    concentration=result.nacl_wt_pct.combine_first(result.electrolyte_condition_cat.map(reported_nacl))
    if ((concentration.dropna()<0)|(concentration.dropna()>100)).any():
        raise ValueError('Invalid reported NaCl weight percentage')
    result['nacl_reported_log1p_wtpct']=np.log1p(concentration)
    result['electrolyte_group']=result.electrolyte_condition_cat.map(electrolyte_group)
    result['matrix_group']=result.matrix_family_reported.map(matrix_group)
    result['heat_treatment_group']=result.heat_treatment_cat.map(heat_treatment_group)
    return result
