import unittest
import numpy as np
import pandas as pd
from scripts.normalize_dataset_units import normalize


class UnitTests(unittest.TestCase):
    def test_preserves_source_and_unresolved_target(self):
        source=pd.DataFrame(dict(original_icorr_value=[np.nan,2.4],
            original_icorr_unit=[np.nan,'A/cm2 (printed; scale unresolved)'],
            icorr_value=[8.,np.nan],icorr_unit=['uA/cm2',np.nan],
            icorr_A_cm2=[8e-6,np.nan],hold_reason=[np.nan,'uncertain_scale']))
        result=normalize(source)
        self.assertEqual(result.loc[0,'original_icorr_value'],8.)
        self.assertEqual(result.loc[0,'original_icorr_unit'],'uA/cm2')
        self.assertEqual(result.loc[0,'icorr_value'],8e-6)
        self.assertEqual(result.loc[0,'icorr_unit'],'A/cm2')
        self.assertTrue(pd.isna(result.loc[1,'icorr_value']))
        self.assertTrue(pd.isna(result.loc[1,'unit_conversion_factor_to_A_cm2']))
        self.assertEqual(result.loc[1,'original_icorr_value'],2.4)

    def test_rejects_wrong_scale(self):
        source=pd.DataFrame(dict(original_icorr_value=[1.],original_icorr_unit=['mA/cm2'],
            icorr_value=[1.],icorr_unit=['mA/cm2'],icorr_A_cm2=[1e-6],hold_reason=[np.nan]))
        with self.assertRaises(ValueError):normalize(source)
