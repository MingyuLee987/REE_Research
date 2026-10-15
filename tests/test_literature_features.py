import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, Mock
import numpy as np
import pandas as pd
from ree_research.cli import demo
from ree_research.schema import prepare, ALL_FEATURES, FEATURE_PROFILES
from ree_research.benchmark import selected_features
from ree_research.context import enrich, CONTEXT_NUMERIC, CONTEXT_CATEGORICAL


class LiteratureFeatureTests(unittest.TestCase):
    def test_physical_fields_and_missing_exposure(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'demo.csv'; demo(p)
            raw=pd.read_csv(p).drop(columns=['exposure_h'])
            frame=prepare(raw)
            self.assertTrue(frame.exposure_log1p_h.isna().all())
            raw['grain_size_um']=-1
            with self.assertRaises(ValueError):prepare(raw)

    def test_literature_profile_is_opt_in_and_has_no_outcome_columns(self):
        self.assertEqual(len(ALL_FEATURES),44)
        self.assertTrue(set(['icorr_A_cm2','target','paper_id','evidence_quote','notes','Rct','Ecorr']).isdisjoint(ALL_FEATURES))
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'demo.csv'; demo(p)
            frame=prepare(pd.read_csv(p))
            frame['grain_size_um']=10
            self.assertNotIn('grain_size_um',selected_features(frame,'core')[0])
            self.assertIn('grain_size_um',selected_features(frame,'literature')[0])

    @patch('ree_research.context.requests.post')
    @patch.dict('os.environ',{'OPENAI_API_KEY':'test-key'})
    def test_context_keeps_target_pending_and_rejects_unsupported_value(self,post):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);source=root/'source';source.mkdir()
            (source/'blocks.json').write_text(json.dumps([{'locator':'p:1','text':'NaCl concentration 3.5 wt.%','xml':None}]))
            data=root/'input.csv'
            pd.DataFrame([{'record_id':'r1','paper_id':'10.1000/test','sample_id':'s1','icorr_A_cm2':1e-5,'review_status':'pending'}]).to_csv(data,index=False)
            row={f:None for f in CONTEXT_NUMERIC+CONTEXT_CATEGORICAL}
            row.update(record_id='r1',nacl_wt_pct=3.5,evidence=[{'fields':['nacl_wt_pct'],'locator':'p:1','quote':'NaCl concentration 3.5 wt.%'}])
            def response():
                return {'status':'completed','output':[{'content':[{'type':'output_text','text':json.dumps({'rows':[row]})}]}]}
            post.return_value=Mock(status_code=200)
            post.return_value.json.side_effect=lambda:response()
            out=root/'ok'
            enrich(data,source,out)
            saved=pd.read_csv(out/'enriched_pending.csv')
            self.assertEqual(saved.loc[0,'review_status'],'pending')
            self.assertEqual(saved.loc[0,'icorr_A_cm2'],1e-5)
            row['grain_size_um']=9
            with self.assertRaisesRegex(ValueError,'Missing field evidence'):
                enrich(data,source,root/'bad')
            self.assertFalse((root/'bad'/'enriched_pending.csv').exists())
