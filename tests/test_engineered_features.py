import tempfile
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
from ree_research.cli import demo
from ree_research.schema import prepare, FEATURE_PROFILES
from ree_research.benchmark import selected_features


class EngineeredFeatureTests(unittest.TestCase):
    def raw(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'demo.csv';demo(p)
            return pd.read_csv(p)

    def test_descriptors_do_not_use_target_or_fill_missing_composition(self):
        raw=self.raw();raw['Mo']=np.nan
        first=prepare(raw)
        raw['icorr_A_cm2']*=1000
        second=prepare(raw)
        columns=sum(FEATURE_PROFILES['corrosion'],[])
        pd.testing.assert_frame_equal(first[columns],second[columns])
        self.assertTrue(first.Cr_Mo_sum_wtpct.isna().all())
        self.assertTrue(first.RE_log1p_x_Mo.isna().all())

    def test_percentage_basis_is_not_guessed_or_converted_to_molarity(self):
        raw=self.raw();raw['chloride_mol_L']=np.nan
        raw.loc[:2,'electrolyte_condition_cat']=['NaCl_3.5wtpct','NaCl_3.5pct','NaCl_0.1mol_L']
        frame=prepare(raw)
        self.assertAlmostEqual(frame.loc[0,'nacl_reported_log1p_wtpct'],np.log1p(3.5))
        self.assertTrue(frame.loc[1:2,'nacl_reported_log1p_wtpct'].isna().all())
        self.assertTrue(frame.chloride_log1p_mol_L.isna().all())

    def test_constant_and_single_paper_features_excluded_on_training_only(self):
        raw=self.raw();raw['pH']=np.nan
        raw.loc[raw.paper_id.eq('synthetic-0'),'pH']=np.arange(8)
        frame=prepare(raw)
        cols=selected_features(frame,'corrosion',.01)[0]
        self.assertNotIn('pH',cols)
        self.assertNotIn('exposure_log1p_h',cols)
        with self.assertRaises(ValueError):
            raw['temperature_C']=-273.15;prepare(raw)
