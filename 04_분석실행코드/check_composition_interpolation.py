"""Secondary diagnostic: unseen reported compositions within known domains.

This is not external-paper validation and cannot establish the user's unmeasured
POSEIDON600 performance. No identical reported-composition bundle crosses folds.
"""
from pathlib import Path
import json,warnings
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold
import seek_r2_target as run
from composition_active_learning import key_row

OUT=run.OUT
AGING=['RE_wt_pct','RE_wt_pct_squared','REwt_x_exposure','REwt_x_temperature',
       'temperature_x_exposure','exposure_log_squared']
run.PROFILES['dose_aging']=(run.CHEM+run.DERIVED+run.ENV+AGING,['RE_element_cat'])
run.PROFILES['dose_aging_preparation']=(run.old.COMP+run.ENV+run.old.PREP+AGING,
    ['RE_element_cat','heat_treatment_group','cooling_medium'])
CONFIGS=[dict(profile=p,model=name,params=params,weight='family_equal')
 for p in ['compact_composition','composition_preparation_environment','dose_aging','dose_aging_preparation']
 for name,params in [('ridge',dict(alpha=100)),('svr',dict(C=10,gamma=.01)),
                     ('spline_ridge',dict(alpha=10)),('catboost',dict(depth=3,l2_leaf_reg=10))]]
CONFIGS += [dict(profile=p,model='ridge',params=dict(alpha=a),weight='family_equal')
    for p in ['dose_aging','dose_aging_preparation'] for a in [1,10,30,300,1000]]

def search(d,k):
    splits=list(GroupKFold(k).split(d,groups=d.composition_key))
    cache={(p,i):run.encode(d.iloc[tr],d.iloc[va],p) for p in run.PROFILES for i,(tr,va) in enumerate(splits)}
    results=[];preds=[]
    for cfg in CONFIGS:
        pred=np.zeros(len(d))
        for i,(tr,va) in enumerate(splits):
            assert not set(d.iloc[tr].composition_key)&set(d.iloc[va].composition_key)
            pred[va]=run.predict(d.iloc[tr],d.iloc[va],cfg,cache[(cfg['profile'],i)])
        results.append(dict(**cfg,**run.old.score(d,pred)));preds.append(pred)
    idx=min(range(len(results)),key=lambda i:results[i]['rmse'])
    return results,preds,idx

def main():
    d=run.augment(pd.read_csv(run.BASE/'development_enriched_no_chinese.csv')).sort_values('record_id').reset_index(drop=True)
    d['RE_wt_pct']=d.RE_ppm/10000
    d['RE_wt_pct_squared']=d.RE_wt_pct**2
    d['REwt_x_exposure']=d.RE_wt_pct*d.exposure_log1p_h
    d['REwt_x_temperature']=d.RE_wt_pct*d.temperature_C
    d['temperature_x_exposure']=d.temperature_C*d.exposure_log1p_h
    d['exposure_log_squared']=d.exposure_log1p_h**2
    d['composition_key']=d.apply(key_row,axis=1)
    results,preds,idx=search(d,4);nested=np.zeros(len(d));folds=[]
    for fold,(tr,va) in enumerate(GroupKFold(3).split(d,groups=d.composition_key)):
        inner,_,win=search(d.iloc[tr],3)
        nested[va]=run.predict(d.iloc[tr],d.iloc[va],inner[win])
        folds.append(dict(fold=fold,selected=inner[win],validation_ids=d.iloc[va].record_id.tolist()))
    report=dict(validation_scope='SECONDARY: unseen reported compositions within existing literature domains. Studies may appear in both train and validation. Not unseen-paper or user-alloy test performance.',
        adaptation_notice='Exploratory second pass after initial development composition CV R2=0.473. Neither this CV nor prior observed paper tests are fresh external validation. The historical test was not used for these feature choices or model tuning.',
        records=len(d),composition_bundles=d.composition_key.nunique(),candidates=len(CONFIGS),
        selected=results[idx],nested_composition_cv=run.old.score(d,nested),folds=folds,
        independent_test_R2=None,user_alloy_R2=None)
    result_path=OUT/'secondary_composition_validation.json'
    initial=OUT/'secondary_composition_validation_initial.json'
    if result_path.exists() and not initial.exists():initial.write_bytes(result_path.read_bytes())
    result_path.write_text(json.dumps(report,indent=2),encoding='utf8')
    pd.DataFrame(dict(record_id=d.record_id,doi=d.doi,composition_key=d.composition_key,target=d.target,
        selected_oof=preds[idx],nested_composition_oof=nested)).to_csv(OUT/'secondary_composition_predictions.csv',index=False)
    print(json.dumps(dict(selected=results[idx],nested=report['nested_composition_cv'],compositions=d.composition_key.nunique()),indent=2))

if __name__=='__main__':
    with warnings.catch_warnings():warnings.simplefilter('ignore');main()
