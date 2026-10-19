"""Composition/preparation ablation, grouped model selection and reused test.

Source-grounded overlays never change the master CSV or invent responses.
"""
from pathlib import Path
import json, hashlib, warnings, time
import numpy as np
import pandas as pd
import joblib
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler,OneHotEncoder
from sklearn.linear_model import Ridge
from sklearn.svm import SVR
from sklearn.kernel_ridge import KernelRidge
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern,ConstantKernel
from sklearn.ensemble import ExtraTreesRegressor,HistGradientBoostingRegressor
from sklearn.model_selection import GroupKFold
from sklearn.metrics import r2_score,mean_absolute_error
from catboost import CatBoostRegressor
from ree_research.schema import prepare,COMPOSITION,ADDITIONAL_COMPOSITION
from evaluate_current_holdout import TEST,OLD_TEST,LA

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'03_분석결과와실험계획/90_이전분석기록/01_조성_제조방법_모델비교'
COMP=COMPOSITION+ADDITIONAL_COMPOSITION+['RE_log1p_ppm']
PREP=['heat_treatment_temperature_C','heat_treatment_duration_h','surface_finish_grit',
      'rolling_start_C','rolling_finish_low_C','rolling_finish_high_C','plate_thickness_mm',
      'homogenization_C','homogenization_h','coiling_C','final_anneal_C','final_anneal_h',
      'austenitizing_C','austenitizing_h','tempering_C','tempering_h']
PCAT=['heat_treatment_group','cooling_medium','forming_route','surface_preparation_cat','surface_state_cat']
ENV=['temperature_C','pH','chloride_mol_L','nacl_wt_pct','exposure_log1p_h',
     'scan_rate_mV_s','ocp_stabilization_min']
ECAT=['electrolyte_group','pre_exposure_protocol_cat','reference_electrode_cat']
PROFILES={'composition':(COMP,['RE_element_cat']),
 'composition_preparation':(COMP+PREP,['RE_element_cat']+PCAT),
 'composition_preparation_environment':(COMP+PREP+ENV,['RE_element_cat']+PCAT+ECAT),
 'with_reported_microstructure':(COMP+PREP+ENV,['RE_element_cat']+PCAT+ECAT+['matrix_phase_group','secondary_phase_group'])}

def family(d):return d.doi.where(~d.doi.isin(LA),'shared_La_SASS_material_series')
def weight(d,kind):
    w=np.ones(len(d)) if kind=='uniform' else 1/family(d).map(family(d).value_counts()).to_numpy()
    return w/w.mean()

def enrich(data):
    d=data.copy();audit=[]
    def put(doi,values,locator,quote):
        mask=d.doi.eq(doi)
        for field,value in values.items():
            d.loc[mask,field]=value
            audit.append(dict(doi=doi,field=field,value=value,locator=locator,evidence_quote=quote,
                affected_records=d.loc[mask,'record_id'].tolist(),source_file=d.loc[mask,'source_file'].iloc[0]))
    put('10.3390/ma17184467',dict(forming_route='forged_hot_rolled',homogenization_C=1200,
        homogenization_h=1,rolling_start_C=1200,rolling_finish_low_C=860,rolling_finish_high_C=860,
        plate_thickness_mm=7,coiling_C=550,cooling_medium='water'), 'XML p:8',
        'homogenization preservation at 1200 C for 1 h; three passes from 1200 C to 1000 C, and three passes from 1000 C to 860 C. After water cooling, the plate was coiled at 550 C.')
    put('10.3390/ma19122685',dict(forming_route='hot_rolled',homogenization_C=1200,homogenization_h=2,
        rolling_start_C=1000,rolling_finish_low_C=880,rolling_finish_high_C=880,plate_thickness_mm=14,
        cooling_medium='water_then_air'),'XML p:5',
        'heated to 1200 C and held for 2 h; initial rolling temperature approximately 1000 C; finish rolling approximately 880 C; rapidly cooled to around 440 C; finally air-cooled')
    put('10.1038/s41598-024-67799-9',dict(forming_route='forged',plate_thickness_mm=20),'XML p:10',
        'After deoxidation of steel with aluminum, the metal was forged to a thickness of 20 mm and cooled to room temperature.')
    put('10.3390/ma14123254',dict(forming_route='forged'),'XML p:6',
        'open die forging on a hydraulic press in a temperature range of 1200-900 C')
    put('10.20964/2019.03.31',dict(forming_route='forged_hot_cold_rolled',rolling_start_C=1150,
        plate_thickness_mm=1,final_anneal_C=1000,final_anneal_h=1/60,
        surface_finish_grit=2000,surface_preparation_cat='ground_SiC'),'PDF page:3 section 2',
        'forged and then hot rolled at 1150 C; cold rolled to 1 mm; recrystallization annealed at 1000 C for 1 min; polished with SiC paper to 2000 grit')
    put('10.3390/ma18010069',dict(surface_finish_grit=2000,surface_preparation_cat='ground_and_polished'),
        'XML p:8','working face was ground to 2000 mesh with sandpaper. After polishing, it was washed and dried.')
    put('10.11973/fsyfh-202403006',dict(surface_finish_grit=2000,surface_preparation_cat='ground_SiC'),
        'PDF page:3 section 1.2.2','electrochemical working electrode; SiC paper progressively to 2000 grit')
    put('10.20057/j.1003-8620.2024-00280',dict(forming_route='hot_rolled',homogenization_C=1050,
        homogenization_h=40/60,rolling_start_C=1050,rolling_finish_low_C=950,rolling_finish_high_C=990,
        cooling_medium='air',surface_preparation_cat='ground_and_polished'),
        'PDF page:2 Table 1 and experimental section','holding 1050 C 40 min; start rolling 1050 C; finish rolling 950-990 C; air cooling; electrochemical specimens ground and polished')
    # Record-level thermal stages: never merge austenitizing and tempering values.
    for doi,temp,hours,quench_medium,temper_temp,temper_hours,temper_medium,locator,quote in [
      ('10.3390/met15090935',1080,.5,'oil',580,2,'air','PDF pages:2-3 section 2',
       'oil quenching after heating at 1080 C for 30 min; air cooling after maintaining at 580 C for 2 h; Q/QT and YQ/YQT'),
      ('10.3390/ma14123254',900,20/60,'water',600,1,'water','XML Table 2 and p:7',
       'Normalizing annealing 900 C 20 min Air; Quenching 900 C 20 min Water; Tempering 600 C 60 min Water')]:
        mask=d.doi.eq(doi)
        for idx in d.index[mask]:
            name=str(d.at[idx,'sample_id']);tempered=('QT' in name or 'tempering' in name)
            normalizing='normalizing' in name
            values=dict(austenitizing_C=temp,austenitizing_h=hours,
                cooling_medium='air' if normalizing else quench_medium,
                heat_treatment_group='normalized' if normalizing else 'tempered' if tempered else 'quenched')
            if tempered:values.update(tempering_C=temper_temp,tempering_h=temper_hours,
                cooling_medium=quench_medium+'_then_'+temper_medium)
            for field,value in values.items():
                d.loc[idx,field]=value
                audit.append(dict(doi=doi,field=field,value=value,locator=locator,evidence_quote=quote,
                    affected_records=[d.at[idx,'record_id']],source_file=d.at[idx,'source_file']))
    for c in set(sum([v[0]+v[1] for v in PROFILES.values()],[])):
        if c not in d:d[c]=np.nan
    d['RE_element_cat']=d.RE_element_cat.map(lambda x:'+'.join(sorted(str(x).split('+'))) if pd.notna(x) else x)
    (OUT/'preparation_overlay_evidence.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False),encoding='utf8')
    d.to_csv(OUT/'enriched_eligible.csv',index=False)
    return d

def columns(d,profile):
    num,cat=PROFILES[profile]
    # Rare fields are allowed at >=2 independent families; no source identifiers.
    def valid(c):return d[c].notna().any() and family(d.loc[d[c].notna()]).nunique()>=2 and d[c].dropna().nunique()>1
    return [c for c in num if valid(c)],[c for c in cat if valid(c)]

def encode(train,other,profile):
    num,cat=columns(train,profile);train=train.copy();other=other.copy();categories={}
    for c in cat:
        # Each retained category needs >=2 training families; reduce source fingerprinting.
        counts=train.assign(_f=family(train)).groupby(c)._f.nunique()
        allowed=counts[counts>=2].index.tolist();categories[c]=allowed
        for f in [train,other]:
            f[c]=f[c].where(f[c].isna()|f[c].isin(allowed),'other_reported').fillna('not_reported').astype(str)
    prep=ColumnTransformer([
      ('numeric',make_pipeline(SimpleImputer(strategy='median',add_indicator=True),StandardScaler()),num),
      ('category',OneHotEncoder(handle_unknown='ignore',sparse_output=False),cat)])
    z=prep.fit_transform(train);zo=prep.transform(other)
    native=train[num+cat].copy();nativeo=other[num+cat].copy()
    return z,zo,native,nativeo,dict(numeric=num,categorical=cat,categories=categories,preprocessor=prep)

def models():
    result=[]
    for a in [.1,1,10,100,1000]:result.append(('ridge',dict(alpha=a)))
    for c,g in [(1,.01),(10,.01),(100,.01),(1,.1),(10,.1),(10,'scale')]:result.append(('svr',dict(C=c,gamma=g,epsilon=.1)))
    for a,g in [(1,.01),(10,.01),(1,.1),(10,.1)]:result.append(('kernel_ridge',dict(alpha=a,gamma=g)))
    for a,l in [(.05,1),(.1,3),(.5,3),(.5,10)]:result.append(('gpr',dict(alpha=a,length_scale=l)))
    for leaf in [2,5]:result.append(('extra_trees',dict(min_samples_leaf=leaf)))
    for depth,l2 in [(2,10),(3,10),(4,30)]:result.append(('catboost',dict(depth=depth,l2_leaf_reg=l2)))
    for leaf in [5,15]:result.append(('hist_gradient',dict(min_samples_leaf=leaf)))
    return result

def estimator(name,params):
    if name=='ridge':return Ridge(**params)
    if name=='svr':return SVR(**params)
    if name=='kernel_ridge':return KernelRidge(kernel='rbf',**params)
    if name=='gpr':return GaussianProcessRegressor(kernel=ConstantKernel(1,constant_value_bounds='fixed')*
        Matern(length_scale=params['length_scale'],length_scale_bounds='fixed',nu=2.5),alpha=params['alpha'],normalize_y=True,optimizer=None)
    if name=='extra_trees':return ExtraTreesRegressor(n_estimators=160,random_state=42,n_jobs=2,**params)
    if name=='hist_gradient':return HistGradientBoostingRegressor(max_iter=160,l2_regularization=10,random_state=42,**params)
    return CatBoostRegressor(iterations=240,learning_rate=.04,loss_function='RMSE',random_seed=42,
        thread_count=2,verbose=False,allow_writing_files=False,one_hot_max_size=30,**params)

def fit_predict(train,other,config,encoded=None,keep=False):
    name=config['model'];encoded=encoded or encode(train,other,config['profile'])
    z,zo,native,nativeo,meta=encoded;fit=estimator(name,config['params']);w=weight(train,config['weight'])
    if name=='catboost':fit.fit(native,train.target,cat_features=meta['categorical'],sample_weight=w);pred=fit.predict(nativeo)
    elif name=='gpr':
        # GPR has no sample_weight; emulate confidence weighting via observation alpha.
        fit.set_params(alpha=config['params']['alpha']/w);fit.fit(z,train.target);pred=fit.predict(zo)
    else:fit.fit(z,train.target,sample_weight=w);pred=fit.predict(zo)
    return (pred,fit,meta) if keep else pred

def predict_saved(bundle,prepared_frame):
    """Predict from prepared/engineered features using the saved training mappings."""
    meta=bundle['preprocessing'];frame=prepared_frame.copy()
    for col in meta['numeric']+meta['categorical']:
        if col not in frame:frame[col]=np.nan
    for col in meta['categorical']:
        frame[col]=frame[col].where(frame[col].isna()|frame[col].isin(meta['categories'][col]),'other_reported').fillna('not_reported').astype(str)
    if bundle['configuration']['model']=='catboost':
        return bundle['model'].predict(frame[meta['numeric']+meta['categorical']])
    return bundle['model'].predict(meta['preprocessor'].transform(frame))

def score(d,pred):
    err=d.target.to_numpy()-pred
    paper_mse=pd.DataFrame(dict(g=family(d),e=err**2)).groupby('g').e.mean()
    return dict(r2=float(r2_score(d.target,pred)),mae=float(mean_absolute_error(d.target,pred)),
        rmse=float(np.sqrt(np.mean(err**2))),family_macro_rmse=float(np.sqrt(paper_mse.mean())))

def search(d,configs,folds=4):
    splits=list(GroupKFold(min(folds,family(d).nunique())).split(d,groups=family(d)))
    cache={(profile,i):encode(d.iloc[tr],d.iloc[va],profile) for profile in PROFILES for i,(tr,va) in enumerate(splits)}
    results=[];predictions=[];start=time.time()
    for j,config in enumerate(configs):
        pred=np.zeros(len(d))
        for i,(tr,va) in enumerate(splits):pred[va]=fit_predict(d.iloc[tr],d.iloc[va],config,cache[(config['profile'],i)])
        results.append(dict(**config,**score(d,pred)));predictions.append(pred)
        if (j+1)%28==0:print(json.dumps(dict(completed=j+1,total=len(configs),seconds=round(time.time()-start))),flush=True)
    idx=min(range(len(results)),key=lambda i:(results[i]['family_macro_rmse'],results[i]['rmse']))
    return results,predictions,idx

def main():
    OUT.mkdir(exist_ok=True);master=ROOT/'01_논문원문과데이터/processed/pilot100/llm_pending_all.csv'
    ids=pd.read_csv(ROOT/'01_논문원문과데이터/processed/pilot100/provisional_for_model.csv').record_id
    raw=pd.read_csv(master);data=enrich(prepare(raw[raw.record_id.isin(ids)],('pending',)))
    train=data[~data.doi.isin(TEST+OLD_TEST)].sort_values('record_id').reset_index(drop=True)
    test=data[data.doi.isin(TEST)].sort_values('record_id').reset_index(drop=True)
    configs=[dict(profile=p,model=name,params=params,weight=w) for p in PROFILES
        for name,params in models() for w in ['uniform','family_equal']]
    protocol=dict(master_sha256=hashlib.sha256(master.read_bytes()).hexdigest(),train_rows=len(train),test_rows=len(test),
        train_dois=train.doi.unique().tolist(),test_dois=TEST,old_test_excluded=OLD_TEST,
        selection='Minimum development OOF family-macro RMSE, pooled RMSE tie break; no test-driven selection',
        profiles=PROFILES,configurations=len(configs),new_experimental_labels=0,
        target='log10(icorr_A_cm2)',test_status='Previously observed exploratory test, not independent external validation',
        nested_status='Full search independently repeated in each outer fold; nested prediction estimates entire selection procedure',
        dependency_catboost=__import__('catboost').__version__)
    (OUT/'protocol.json').write_text(json.dumps(protocol,indent=2),encoding='utf8')
    coverage=[]
    for profile,(num,cat) in PROFILES.items():
        for col in num+cat:coverage.append(dict(profile=profile,feature=col,records=int(train[col].notna().sum()),families=family(train[train[col].notna()]).nunique()))
    pd.DataFrame(coverage).to_csv(OUT/'feature_coverage.csv',index=False)
    results,preds,idx=search(train,configs);selected=results[idx]
    pd.DataFrame(results).assign(params=lambda d:d.params.map(json.dumps)).to_csv(OUT/'cv_results.csv',index=False)
    (OUT/'selected_before_test.json').write_text(json.dumps(selected,indent=2),encoding='utf8')
    # Honest audit: rerun the whole search inside each outer split, not just selected config.
    nested=np.zeros(len(train));outerchoices=[]
    for fold,(tr,va) in enumerate(GroupKFold(3).split(train,groups=family(train))):
        inner,_,winner=search(train.iloc[tr],configs,folds=3);config=inner[winner]
        nested[va]=fit_predict(train.iloc[tr],train.iloc[va],config)
        outerchoices.append(dict(fold=fold,selected=config));print('nested_outer_complete',fold,flush=True)
    pd.DataFrame(dict(record_id=train.record_id,doi=train.doi,target=train.target,nested_pred=nested,
        selected_non_nested_oof=preds[idx])).to_csv(OUT/'development_predictions.csv',index=False)
    testpred,fit,meta=fit_predict(train,test,selected,keep=True)
    joblib.dump(dict(model=fit,preprocessing=meta,configuration=selected),OUT/'selected_model.joblib')
    prediction=pd.DataFrame(dict(record_id=test.record_id,doi=test.doi,sample_id=test.sample_id,
        actual_log10_A_cm2=test.target,predicted_log10_A_cm2=testpred,
        actual_A_cm2=test.icorr_A_cm2,predicted_A_cm2=10**testpred))
    prediction.to_csv(OUT/'test_predictions.csv',index=False)
    ablation=[]
    for profile in PROFILES:
        candidates=[r for r in results if r['profile']==profile]
        best=min(candidates,key=lambda r:(r['family_macro_rmse'],r['rmse']))
        pp=fit_predict(train,test,best)
        ablation.append(dict(profile=profile,configuration=best,reused_test=score(test,pp)))
    report=dict(**protocol,selected=selected,selected_reused_test=score(test,testpred),
        raw_unit_test_R2=float(r2_score(test.icorr_A_cm2,10**testpred)),nested_development=score(train,nested),
        outer_choices=outerchoices,feature_ablation=ablation,used_numeric=meta['numeric'],used_categorical=meta['categorical'],
        per_test_paper={doi:score(g,testpred[g.index]) for doi,g in test.groupby('doi')})
    (OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print(json.dumps(dict(selected=selected,test=report['selected_reused_test'],nested=report['nested_development'],ablation=ablation),indent=2),flush=True)

if __name__=='__main__':
    with warnings.catch_warnings():warnings.simplefilter('ignore');main()
