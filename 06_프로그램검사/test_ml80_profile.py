import unittest
import numpy as np
import pandas as pd
from ree_research.schema import ALL_FEATURES, FEATURE_PROFILES
from ree_research.benchmark import selected_features


class MissingnessThreshold(unittest.TestCase):
    def test_twenty_percent_boundary_and_paper_support(self):
        frame=pd.DataFrame({f:[np.nan]*10 for f in ALL_FEATURES})
        frame['paper_id']=['a','b']+['c']*8
        frame.loc[:1,'C']=[.1,.2]  # Exactly 80% missing, supported by two papers.
        frame.loc[0,'Si']=.2  # 90% missing, excluded.
        frame.loc[2:4,'Mn']=[1.,1.2,1.3]  # One paper only, excluded.
        num,cat=selected_features(frame,'ml80',.2)
        self.assertEqual(num,['C'])
        self.assertEqual(cat,[])

    def test_profile_is_unique_and_does_not_duplicate_raw_categories(self):
        num,cat=FEATURE_PROFILES['ml80']
        self.assertEqual(len(num+cat),len(set(num+cat)))
        self.assertNotIn('matrix_phase_reported',cat)
        self.assertIn('matrix_phase_group',cat)
