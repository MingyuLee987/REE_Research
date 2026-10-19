"""Bounded extended search; fixed historical English test scored after selection.

No test-driven split, target fabrication, or threshold-achievement guarantee.
"""
from pathlib import Path
import json,sys,warnings,time
import numpy as np
import pandas as pd
import joblib
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler,OneHotEncoder,SplineTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import GroupKFold
from sklearn.metrics import r2_score,mean_absolute_error
from sklearn.linear_model import Ridge,BayesianRidge
from sklearn.svm import SVR
from sklearn.kernel_ridge import KernelRidge
from sklearn.ensemble import ExtraTreesRegressor,RandomForestRegressor,VotingRegressor
from catboost import CatBoostRegressor
import optimize_preparation_ml as old
from evaluate_current_holdout import OLD_TEST

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'03_분석결과와실험계획/01_현재분석_중국어논문제외'
OUT=BASE/'추가모델탐색_R2목표'
CHEM=['Cr','Ni','Mo','Cu','RE_log1p_ppm']
ENV=['temperature_C','nacl_wt_pct','exposure_log1p_h','chloride_mol_L','scan_rate_mV_s']
DERIVED=['Cr_Mo_product','Cr_Ni_product','Ni_Mo_product','RE_Cr_product','RE_Ni_product']
PROFILES={'compact_composition':(CHEM,['RE_element_cat']),
 'composition_nonlinear':(CHEM+DERIVED,['RE_element_cat']),
 'composition_environment':(CHEM+DERIVED+ENV+['reported_acid_tag','reported_alkali_tag','reported_seawater_tag'],['RE_element_cat']),
 'composition_preparation_environment':(old.COMP+DERIVED+ENV+old.PREP,['RE_element_cat','heat_treatment_group','cooling_medium'])}

def augment(d):
    d=d.copy()
    for a,b,c in [('Cr','Mo','Cr_Mo_product'),('Cr','Ni','Cr_Ni_product'),('Ni','Mo','Ni_Mo_product'),
                   ('RE_log1p_ppm','Cr','RE_Cr_product'),('RE_log1p_ppm','Ni','RE_Ni_product')]:d[c]=d[a]*d[b]
    text=d.electrolyte_condition_cat.fillna('').str.lower()
    for name,pattern in [('acid','h2so4|hcl'),('alkali','naoh|koh'),('seawater','seawater')]:
        # Text tags describe explicit reporting, never inferred pH/concentration.
        d['reported_'+name+'_tag']=text.str.contains(pattern,regex=True).astype(float).where(text.ne(''),np.nan)
    for num,cat in PROFILES.values():
        for c in num+cat:
            if c not in d:d[c]=np.nan
    return d

def encode(train,test,profile):
    num,cat=PROFILES[profile]
    num=[c for c in num if train[c].notna().mean()>=.2 and train[c].dropna().nunique()>1
        and old.family(train[train[c].notna()]).nunique()>=2]
    cat=[c for c in cat if train[c].notna().any()]
    prep=ColumnTransformer([
      ('num',make_pipeline(SimpleImputer(strategy='median',add_indicator=True),StandardScaler()),num),
      ('cat',make_pipeline(SimpleImputer(strategy='constant',fill_value='not_reported'),
                          OneHotEncoder(handle_unknown='ignore',sparse_output=False)),cat)])
    return prep.fit_transform(train),prep.transform(test),prep

def estimator(name,params):
    if name=='ridge':return Ridge(**params)
    if name=='spline_ridge':return make_pipeline(SplineTransformer(n_knots=3,degree=2,extrapolation='constant'),Ridge(**params))
    if name=='svr':return SVR(epsilon=.15,**params)
    if name=='kernel_ridge':return KernelRidge(kernel='rbf',**params)
    if name=='extra_trees':return ExtraTreesRegressor(n_estimators=180,min_samples_leaf=3,max_features=.8,n_jobs=2,random_state=42)
    if name=='random_forest':return RandomForestRegressor(n_estimators=180,min_samples_leaf=3,max_features=.8,n_jobs=2,random_state=42)
    if name=='ensemble':return VotingRegressor([('ridge',Ridge(alpha=100)),('svr',SVR(C=1,gamma=.01,epsilon=.15)),
        ('trees',ExtraTreesRegressor(n_estimators=140,min_samples_leaf=5,max_features=.8,n_jobs=2,random_state=42))])
    return CatBoostRegressor(iterations=400,learning_rate=.03,loss_function='RMSE',thread_count=2,
        random_seed=42,verbose=False,allow_writing_files=False,**params)

def configurations():
    choices=[('ridge',dict(alpha=a)) for a in [1,10,30,100,300,1000]]
    choices += [('spline_ridge',dict(alpha=a)) for a in [10,100,1000]]
    choices += [('svr',dict(C=c,gamma=g)) for c,g in [(1,.001),(1,.01),(10,.001),(10,.01),(1,.1),(10,.1)]]
    choices += [('kernel_ridge',dict(alpha=a,gamma=g)) for a,g in [(1,.001),(10,.001),(1,.01),(10,.01)]]
    choices += [('catboost',dict(depth=d,l2_leaf_reg=l2)) for d,l2 in [(2,10),(3,10),(4,30)]]
    choices += [(name,{}) for name in ['extra_trees','random_forest','ensemble']]
    result=[dict(profile=p,model=name,params=params,weight=w) for p in PROFILES
        for name,params in choices for w in ['uniform','family_equal']]
    # Keep the previous full-composition baseline; new features must beat it.
    result += [dict(profile='previous_composition_baseline',model='prior_ridge',
        params=dict(alpha=100),weight=w) for w in ['uniform','family_equal']]
    return result

def predict(train,test,cfg,encoded=None,keep=False):
    if cfg['model']=='prior_ridge':
        legacy=dict(profile='composition',model='ridge',params=cfg['params'],weight=cfg['weight'])
        pp,fit,meta=old.fit_predict(train,test,legacy,keep=True)
        lo=float(train.target.min());hi=float(train.target.max());pp=np.clip(pp,lo,hi)
        return (pp,dict(model=fit,legacy_preprocessing=meta,bounds=[lo,hi],configuration=cfg)) if keep else pp
    z,zt,pre=encoded if encoded is not None else encode(train,test,cfg['profile'])
    fit=estimator(cfg['model'],cfg['params']);w=old.weight(train,cfg['weight'])
    if cfg['model']=='spline_ridge':fit.fit(z,train.target,ridge__sample_weight=w)
    else:fit.fit(z,train.target,sample_weight=w)
    # Conservative empirical prediction bounds; fitted solely on current training labels.
    lo=float(train.target.min());hi=float(train.target.max())
    pred=np.clip(fit.predict(zt),lo,hi)
    return (pred,dict(model=fit,preprocessor=pre,bounds=[lo,hi],configuration=cfg)) if keep else pred

def predict_saved(bundle,frame):
    frame=augment(frame)
    if 'legacy_preprocessing' in bundle:
        pred=old.predict_saved(dict(model=bundle['model'],preprocessing=bundle['legacy_preprocessing'],
            configuration=dict(model='ridge')),frame)
    else:pred=bundle['model'].predict(bundle['preprocessor'].transform(frame))
    return np.clip(pred,*bundle['bounds'])

def search(d,configs,k=4):
    folds=list(GroupKFold(k).split(d,groups=old.family(d)))
    enc={(p,i):encode(d.iloc[tr],d.iloc[va],p) for p in PROFILES for i,(tr,va) in enumerate(folds)}
    scores=[];preds=[];start=time.time()
    for j,cfg in enumerate(configs):
        pred=np.zeros(len(d))
        for i,(tr,va) in enumerate(folds):pred[va]=predict(d.iloc[tr],d.iloc[va],cfg,enc.get((cfg['profile'],i)))
        scores.append(dict(**cfg,**old.score(d,pred)));preds.append(pred)
        if (j+1)%50==0:print(json.dumps(dict(done=j+1,total=len(configs),seconds=round(time.time()-start))),flush=True)
    win=min(range(len(scores)),key=lambda i:scores[i]['rmse'])
    return scores,preds,win

def main():
    OUT.mkdir(exist_ok=True)
    train=augment(pd.read_csv(BASE/'development_enriched_no_chinese.csv')).sort_values('record_id').reset_index(drop=True)
    english_ids=pd.read_csv(BASE/'provisional_for_model_no_chinese.csv').record_id
    source=ROOT/'03_분석결과와실험계획/90_이전분석기록/01_조성_제조방법_모델비교/enriched_eligible.csv'
    test=augment(pd.read_csv(source).query('doi in @OLD_TEST')).sort_values('record_id').reset_index(drop=True)
    assert len(train)==112 and len(test)==7 and test.record_id.isin(english_ids).all()
    assert not set(old.family(train))&set(old.family(test))
    configs=configurations()
    protocol=dict(target='log10(icorr_A_cm2)',target_threshold=.5,configurations=len(configs),
        train_records=len(train),train_dois=train.doi.unique().tolist(),
        test_records=len(test),test_dois=OLD_TEST,
        test_basis='Pre-existing historical test boundary retained; previously observed labels, exploratory, not fresh external validation',
        selection='Minimum pooled development 4-fold family-grouped OOF RMSE, equivalent to maximum pooled OOF R2',
        nested='3 outer family folds; complete candidate search repeated in 3 inner family folds',
        prediction_bounds='Clip to training-fold min/max log target, never validation/test bounds',
        profiles=PROFILES,new_experimental_labels=0,
        all_Chinese_language_papers_excluded=True)
    (OUT/'protocol.json').write_text(json.dumps(protocol,indent=2),encoding='utf8')
    scores,preds,win=search(train,configs);selected=scores[win]
    pd.DataFrame(scores).assign(params=lambda d:d.params.map(json.dumps)).to_csv(OUT/'development_cv.csv',index=False)
    (OUT/'selected_before_test.json').write_text(json.dumps(selected,indent=2),encoding='utf8')
    nested=np.zeros(len(train));choices=[]
    for fold,(tr,va) in enumerate(GroupKFold(3).split(train,groups=old.family(train))):
        inner,_,idx=search(train.iloc[tr],configs,k=3)
        nested[va]=predict(train.iloc[tr],train.iloc[va],inner[idx]);choices.append(dict(fold=fold,selected=inner[idx]))
        print('nested_complete',fold,flush=True)
    pp,bundle=predict(train,test,selected,keep=True)
    joblib.dump(bundle,OUT/'selected_model.joblib')
    pd.DataFrame(dict(record_id=test.record_id,doi=test.doi,target_log10=test.target,pred_log10=pp,
        actual_A_cm2=test.icorr_A_cm2,pred_A_cm2=10**pp)).to_csv(OUT/'historical_test_predictions.csv',index=False)
    pd.DataFrame(dict(record_id=train.record_id,doi=train.doi,target=train.target,selected_oof=preds[win],nested_oof=nested)).to_csv(OUT/'development_predictions.csv',index=False)
    report=dict(**protocol,selected=selected,nested_development=old.score(train,nested),
        historical_test=old.score(test,pp),raw_unit_historical_test_R2=float(r2_score(test.icorr_A_cm2,10**pp)),
        nested_above_threshold=bool(r2_score(train.target,nested)>.5),
        historical_test_above_threshold=bool(r2_score(test.target,pp)>.5),outer_choices=choices)
    (OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print(json.dumps(dict(selected=selected,nested=report['nested_development'],historical_test=report['historical_test']),indent=2),flush=True)

if __name__=='__main__':
    with warnings.catch_warnings():warnings.simplefilter('ignore');main()
