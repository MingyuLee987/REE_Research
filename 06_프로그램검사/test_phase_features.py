import unittest
import numpy as np
import pandas as pd
from ree_research.schema import prepare, FEATURE_PROFILES
from ree_research.benchmark import selected_features


class PhaseFeatures(unittest.TestCase):
    def sample(self):
        return dict(record_id='r1',paper_id='p1',doi='10.1/a',source_locator='Table 1',
            evidence_quote='Example validation fixture',review_status='pending',icorr_A_cm2=1e-6,
            Cr=18,Mo=2,Si=.4,Nb=.1,Ni=8,C=.02,Mn=1,N=.1,Cu=.5,RE_ppm=100,
            matrix_phase_reported='austenite',electrolyte_condition_cat='NaCl_3.5wtpct')

    def test_missing_nb_does_not_become_zero_or_estimated_phase(self):
        row=self.sample();row.pop('Nb');row.pop('matrix_phase_reported')
        f=prepare(pd.DataFrame([row]),('pending',))
        self.assertTrue(np.isnan(f.loc[0,'schaeffler_Cr_eq_wtpct']))
        self.assertTrue(np.isnan(f.loc[0,'wrc1992_Cr_eq_wtpct']))
        self.assertTrue(np.isnan(f.loc[0,'matrix_austenitic_x_Ni']))
        self.assertTrue(f['austenite_fraction_reported_pct'].isna().all())

    def test_reference_composition_equations_and_reported_phase_interaction(self):
        f=prepare(pd.DataFrame([self.sample()]),('pending',))
        for field,value in [('schaeffler_Cr_eq_wtpct',20.65),('schaeffler_Ni_eq_wtpct',9.1),
                            ('wrc1992_Cr_eq_wtpct',20.07),('wrc1992_Ni_eq_wtpct',10.825)]:
            self.assertAlmostEqual(f.loc[0,field],value)
        self.assertEqual(f.loc[0,'matrix_austenitic_x_Ni'],8)
        self.assertTrue(np.isnan(f.loc[0,'austenite_fraction_reported_pct']))

    def test_invalid_phase_percent_rejected(self):
        row=self.sample();row['ferrite_fraction_reported_pct']=110
        with self.assertRaises(ValueError):prepare(pd.DataFrame([row]),('pending',))

    def test_phase_profile_excludes_single_paper_and_constant_features(self):
        rows=[dict(self.sample(),record_id='r'+str(i),Cr=18+i) for i in range(3)]
        f=prepare(pd.DataFrame(rows),('pending',))
        with self.assertRaises(ValueError):selected_features(f,'phase_corrosion',.5)
        self.assertEqual(sum(map(len,FEATURE_PROFILES['phase_corrosion'])),46)


if __name__=='__main__':unittest.main()
