"""Composition descriptors and reported-matrix interactions, not phase predictions.

Missing constituents propagate. Nb, C, N etc. are never assumed to be zero.
Schaeffler/WRC equations describe stainless weld constitution; no inferred phase
fractions or ferrite numbers are produced for this mixed bulk-alloy collection.
"""
import numpy as np
import pandas as pd
from .features import matrix_group

PHASE_FRACTIONS = ['austenite_fraction_reported_pct', 'ferrite_fraction_reported_pct',
    'martensite_fraction_reported_pct', 'bainite_fraction_reported_pct', 'pearlite_fraction_reported_pct']
PHASE_RAW_CATEGORICAL = ['matrix_phase_reported', 'secondary_metallic_phases_reported']
PHASE_DERIVED_NUMERIC = ['schaeffler_Cr_eq_wtpct', 'schaeffler_Ni_eq_wtpct',
    'wrc1992_Cr_eq_wtpct', 'wrc1992_Ni_eq_wtpct', 'schaeffler_balance_wtpct', 'C_N_sum_wtpct',
    'matrix_austenitic_x_Ni', 'matrix_austenitic_x_Cr', 'matrix_ferritic_x_Cr',
    'matrix_martensitic_x_C', 'matrix_mixed_x_RE_log1p']
PHASE_DERIVED_CATEGORICAL = ['matrix_phase_group', 'secondary_phase_group']


def secondary_group(value):
    if pd.isna(value) or not str(value).strip(): return np.nan
    text=str(value).lower()
    carbide=any(x in text for x in ['carbide','cementite','m23c6','m7c3','m3c','fe3c','nbc','tic','vc'])
    intermetallic=any(x in text for x in ['sigma','chi','laves','intermetallic','σ','χ'])
    if carbide and intermetallic:return 'carbide_and_intermetallic'
    if carbide:return 'carbide_reported'
    if intermetallic:return 'intermetallic_reported'
    return 'other_explicit_secondary_phase'


def engineer_phase(frame):
    result=frame.copy()
    for field in PHASE_FRACTIONS:
        if field not in result:result[field]=np.nan
    for field in PHASE_RAW_CATEGORICAL:
        if field not in result:result[field]=np.nan
    result['schaeffler_Cr_eq_wtpct']=result.Cr+result.Mo+1.5*result.Si+.5*result.Nb
    result['schaeffler_Ni_eq_wtpct']=result.Ni+30*result.C+.5*result.Mn
    result['wrc1992_Cr_eq_wtpct']=result.Cr+result.Mo+.7*result.Nb
    result['wrc1992_Ni_eq_wtpct']=result.Ni+35*result.C+20*result.N+.25*result.Cu
    result['schaeffler_balance_wtpct']=result.schaeffler_Cr_eq_wtpct-result.schaeffler_Ni_eq_wtpct
    result['C_N_sum_wtpct']=result.C+result.N
    # Author-reported matrix context has its own provenance; do not fall back to a grade lookup.
    result['matrix_phase_group']=result.matrix_phase_reported.map(matrix_group)
    result['secondary_phase_group']=result.secondary_metallic_phases_reported.map(secondary_group)
    phase=result.matrix_phase_group
    for name,column,group in [('matrix_austenitic_x_Ni','Ni','austenitic'),
        ('matrix_austenitic_x_Cr','Cr','austenitic'),('matrix_ferritic_x_Cr','Cr','ferritic'),
        ('matrix_martensitic_x_C','C','martensitic'),('matrix_mixed_x_RE_log1p','RE_log1p_ppm','mixed_phase')]:
        indicator=phase.eq(group).astype(float).where(phase.notna(),np.nan)
        result[name]=result[column]*indicator
    return result
