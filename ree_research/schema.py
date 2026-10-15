import numpy as np
import pandas as pd

COMPOSITION = ['C', 'Si', 'Mn', 'P', 'S', 'Cr', 'Ni', 'Mo', 'Cu']
NUMERIC = COMPOSITION + ['RE_log1p_ppm', 'temperature_C', 'pH']
CATEGORICAL = ['RE_element_cat', 'electrolyte_condition_cat']
FEATURES = NUMERIC + CATEGORICAL
OPTIONAL_NUMERIC = ['high_Cr_indicator', 'chloride_mol_L', 'exposure_h', 'scan_rate_mV_s', 'ocp_stabilization_min']
OPTIONAL_CATEGORICAL = ['gas_condition', 'matrix_family_reported']
ALL_FEATURES = FEATURES + OPTIONAL_NUMERIC + OPTIONAL_CATEGORICAL
PROVENANCE = ['record_id', 'paper_id', 'doi', 'source_locator', 'evidence_quote', 'review_status']
RAW = ['RE_ppm', 'icorr_A_cm2']


def prepare(frame):
    """Validate reviewed measurements; derive target without imputing labels."""
    df = frame.copy()
    required = PROVENANCE + ['icorr_A_cm2']
    missing = sorted(set(required) - set(df.columns))
    if missing:
        raise ValueError(f'Missing columns: {missing}')
    # Missing reports remain missing; absence is never interpreted as zero addition.
    for column in ALL_FEATURES + RAW:
        if column not in df:
            df[column] = np.nan
    for column in ['record_id', 'paper_id', 'source_locator', 'evidence_quote']:
        if df[column].isna().any() or df[column].astype(str).str.strip().eq('').any():
            raise ValueError(f'{column} must be provided for every measurement')
    if df.record_id.duplicated().any():
        raise ValueError('record_id must be unique')
    if not df.review_status.eq('verified').all():
        raise ValueError('Only manually verified measurements may enter training')
    for column in COMPOSITION + RAW + ['temperature_C', 'pH'] + [c for c in OPTIONAL_NUMERIC if c != 'high_Cr_indicator']:
        df[column] = pd.to_numeric(df[column], errors='raise')
        if np.isinf(df[column].dropna()).any():
            raise ValueError(f'Non-finite {column}')
    if df.icorr_A_cm2.isna().any() or (df.icorr_A_cm2 <= 0).any():
        raise ValueError('icorr_A_cm2 must be measured, finite, and positive')
    if ((df[COMPOSITION] < 0) | (df[COMPOSITION] > 100)).any().any():
        raise ValueError('Composition must be wt.% between 0 and 100')
    if (df[COMPOSITION].sum(axis=1) > 100.01).any():
        raise ValueError('Reported composition sum exceeds 100 wt.%')
    nonnegative = ['RE_ppm', 'chloride_mol_L', 'exposure_h', 'scan_rate_mV_s', 'ocp_stabilization_min']
    if (df[nonnegative] < 0).any().any():
        raise ValueError('Negative concentration/time/rate')
    if (df.temperature_C < -273.15).any():
        raise ValueError('Temperature below absolute zero')
    df['RE_log1p_ppm'] = np.log1p(df.RE_ppm)
    # Protocol definition, not a fitted threshold: >=10.5 wt.% Cr.
    df['high_Cr_indicator'] = np.where(df.Cr.isna(), np.nan, (df.Cr >= 10.5).astype(float))
    df['target'] = np.log10(df.icorr_A_cm2)
    for column in CATEGORICAL + OPTIONAL_CATEGORICAL:
        df[column] = df[column].replace(r'^\s*$', np.nan, regex=True)
    return df
