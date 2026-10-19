"""Target-composition weighted development CV and prospective, unlabeled AL queue.

Read-only source workbook extraction is in workbook_cells.json. No experiment
labels are generated. Existing test targets are used only after CV selection.
"""
from pathlib import Path
import json, hashlib, warnings
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold
from composition_active_learning import register, pipeline, metric, NUM
from evaluate_current_holdout import TEST, OLD_TEST, LA
from ree_research.schema import prepare, ALL_FEATURES

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'03_분석결과와실험계획/02_실험계획_Ce첨가'
BASE={'C':.04,'Si':.7,'Mn':.5,'Cu':.3,'Cr':1.3,'Nb':.07,
      'N':.004,'Ti':.03,'Ni':.1,'P':.01}
DIST=['C','Si','Mn','Cu','Cr','Ni']
SCALE=np.array([.1,.5,1.,.5,2.,1.])

def weights(frame, kind):
    w=np.ones(len(frame))
    if kind!='uniform':
        w=1/frame.doi.map(frame.doi.value_counts()).to_numpy()
    if kind=='paper_equal_target_local':
        z=(frame[DIST].to_numpy(float)-np.array([BASE[c] for c in DIST]))/SCALE
        distance=np.nanmean(z*z,axis=1)
        w*=.1+np.exp(-.5*distance)
    return w/w.mean()

def main():
    register(); OUT.mkdir(exist_ok=True)
    master=ROOT/'01_논문원문과데이터/processed/pilot100/llm_pending_all.csv'
    ids=pd.read_csv(ROOT/'01_논문원문과데이터/processed/pilot100/provisional_for_model.csv').record_id
    raw=pd.read_csv(master); data=prepare(raw[raw.record_id.isin(ids)],('pending',))
    data['RE_element_cat']=data.RE_element_cat.map(lambda x:'+'.join(sorted(str(x).split('+'))) if pd.notna(x) else x)
    train=data[~data.doi.isin(TEST+OLD_TEST)].sort_values('record_id').reset_index(drop=True)
    test=data[data.doi.isin(TEST)].sort_values('record_id').reset_index(drop=True)
    groups=train.doi.where(~train.doi.isin(LA),'shared_La_SASS_material_series')
    folds=list(GroupKFold(4).split(train,groups=groups))
    configs=[(name,params,weight) for weight in ['uniform','paper_equal','paper_equal_target_local']
             for name,params in [('ridge',{'alpha':a}) for a in [1,10,100]]+
             [('svr',{'C':c,'gamma':.01,'epsilon':.2}) for c in [1,10]]]
    protocol=dict(base_nominal_wt_pct=BASE,nominal_Fe_balance_wt_pct=100-sum(BASE.values()),
        input_sha256=hashlib.sha256(master.read_bytes()).hexdigest(),
        target='log10(icorr_A_cm2)',selection='4-fold known-family grouped OOF paper-macro MAE, RMSE tie break',
        weight_selection='weights recomputed inside each training fold; no held-out labels used',
        distance_columns=DIST,distance_scales=SCALE.tolist(),
        candidate_status='User selected Ce only and tentatively plans 300 ppm addition. Provisional 0-300 ppm comparison grid; upper bound and corrosion conditions remain unconfirmed. Charge-basis and retained Ce must be distinguished.',
        mixed_RE='Not ranked: existing model represents total RE and category, not separate Ce/La fractions',
        candidate_conditions='User plan: hot roll approximately 1000 C to 3 mm, air cool; 900 C 15 min under Ar, water quench. Corrosion solution/temperature unspecified. Composition-only model does not model this process.',
        fabrication_plan=dict(melt_mass_g=600,Ce_purity_fraction=.999,
            reported_ingot_dimensions_mm=[150,100,180],ingot_dimensions_status='Inconsistent with 600 g steel; verify before manufacturing',
            specimen_dimensions_mm=[30,10,3],phase_status='Bainite is intended, not experimentally confirmed'),
        test_status='Previously observed exploratory test, 3 papers/9 records; not independent validation',
        available_new_experimental_labels=0)
    (OUT/'protocol.json').write_text(json.dumps(protocol,indent=2),encoding='utf8')
    results=[]; best=None; bestkey=(np.inf,np.inf); bestpred=None
    for name,params,kind in configs:
        pred=np.zeros(len(train))
        for tr,va in folds:
            fit=pipeline('composition_only',name,params)
            fit.fit(train.iloc[tr][ALL_FEATURES],train.iloc[tr].target,
                    regressor__sample_weight=weights(train.iloc[tr],kind))
            pred[va]=fit.predict(train.iloc[va][ALL_FEATURES])
        row=dict(model=name,params=params,weights=kind,**metric(train.target,pred,train.doi))
        results.append(row); key=(row['paper_macro_mae'],row['rmse'])
        if key<bestkey:best=row;bestkey=key;bestpred=pred.copy()
    pd.DataFrame(results).assign(params=lambda x:x.params.map(json.dumps)).to_csv(OUT/'development_cv.csv',index=False)
    (OUT/'selected_before_test.json').write_text(json.dumps(best,indent=2),encoding='utf8')
    fit=pipeline('composition_only',best['model'],best['params'])
    fit.fit(train[ALL_FEATURES],train.target,regressor__sample_weight=weights(train,best['weights']))
    testpred=fit.predict(test[ALL_FEATURES]); testscore=metric(test.target,testpred,test.doi)
    reference=pipeline('composition_only','ridge',{'alpha':100}).fit(train[ALL_FEATURES],train.target)
    reference_score=metric(test.target,reference.predict(test[ALL_FEATURES]),test.doi)
    pd.DataFrame(dict(record_id=test.record_id,doi=test.doi,actual_log10_A_cm2=test.target,
        predicted_log10_A_cm2=testpred)).to_csv(OUT/'reused_test_predictions.csv',index=False)
    pd.DataFrame(dict(record_id=train.record_id,doi=train.doi,actual_log10_A_cm2=train.target,
        oof_predicted_log10_A_cm2=bestpred)).to_csv(OUT/'development_oof.csv',index=False)
    # Compare literature coverage using only composition, never response values.
    z=(train[DIST].to_numpy(float)-np.array([BASE[c] for c in DIST]))/SCALE
    near=train[['record_id','doi','sample_id']+DIST+['RE_element_cat','RE_ppm']].copy()
    near['compared_element_count']=np.isfinite(z).sum(axis=1)
    near['scaled_rms_distance']=np.sqrt(np.nanmean(z*z,axis=1))
    near.sort_values('scaled_rms_distance').to_csv(OUT/'nearest_literature.csv',index=False)
    candidates=[]
    for element,ppm in [('none',0)]+[('Ce',p) for p in [10,25,50,75,100,150,200,300]]:
        row={c:np.nan for c in train.columns};row.update(BASE)
        row.update(candidate_id=f'{element}_{ppm}ppm',RE_element_cat=element,RE_ppm=ppm,
            RE_log1p_ppm=np.log1p(ppm),Fe_nominal_wt_pct=100-sum(BASE.values())-ppm/10000,
            pure_RE_mass_600g_100pct_recovery_g=600*ppm/1e6,
            Ce_99p9_mass_600g_100pct_recovery_g=600*ppm/1e6/.999,
            Ce_99p9_mass_600g_50pct_recovery_g=600*ppm/1e6/.999/.5,
            status='unmeasured_provisional_requires_conditions_and_feasibility')
        candidates.append(row)
    pool=pd.DataFrame(candidates); pred=fit.predict(pool[ALL_FEATURES])
    rng=np.random.default_rng(20261019); estimates=[]; papers=groups.unique()
    for _ in range(40):
        sampled=rng.choice(papers,size=len(papers),replace=True)
        boot=pd.concat([train[groups.eq(p)] for p in sampled],ignore_index=True)
        learner=pipeline('composition_only',best['model'],best['params'])
        learner.fit(boot[ALL_FEATURES],boot.target,regressor__sample_weight=weights(boot,best['weights']))
        estimates.append(learner.predict(pool[ALL_FEATURES]))
    std=np.std(estimates,axis=0)
    # Initial baseline is mandatory; no current target-domain labeled sample exists.
    # Later greedy choices combine bootstrap disagreement and RE-design diversity.
    design=np.array([[np.log1p(x.RE_ppm)/np.log1p(300)] for x in pool.itertuples()])
    chosen=[0]; scores={0:None}
    while len(chosen)<5:
        remaining=[i for i in range(len(pool)) if i not in chosen]
        dist=np.sqrt(((design[remaining,None,:]-design[chosen][None,:,:])**2).sum(axis=2)).min(axis=1)
        u=std[remaining]; us=(u-u.min())/(np.ptp(u)+1e-12);ds=(dist-dist.min())/(np.ptp(dist)+1e-12)
        acquisition=.5*us+.5*ds; idx=int(np.argmax(acquisition)); added=remaining[idx]
        chosen.append(added);scores[added]=float(acquisition[idx])
    fields=['candidate_id']+list(BASE)+['RE_element_cat','RE_ppm','Fe_nominal_wt_pct',
        'pure_RE_mass_600g_100pct_recovery_g','Ce_99p9_mass_600g_100pct_recovery_g',
        'Ce_99p9_mass_600g_50pct_recovery_g','status']
    output=pool[fields].copy();output['heuristic_log10_icorr_A_cm2']=pred
    output['paper_bootstrap_sd_log10']=std
    output['provisional_batch_order']=[chosen.index(i)+1 if i in chosen else np.nan for i in range(len(pool))]
    output['sequential_acquisition_score']=[scores.get(i) for i in range(len(pool))]
    output.to_csv(OUT/'candidate_queue.csv',index=False)
    # Empty response columns, explicitly never passed to training.
    pending=[]
    for i in chosen:
        for replicate in [1,2,3]:
            row={k:pool.iloc[i][k] for k in fields}
            row.update(specimen_id=f'{pool.iloc[i].candidate_id}_r{replicate}',replicate=replicate,
                protocol_id='',melt_id='',role='development',measured_Ce_ppm=np.nan,
                measured_La_ppm=np.nan,icorr_A_cm2=np.nan,temperature_C=np.nan,
                nacl_wt_pct=np.nan,pH=np.nan,heat_treatment='900 C 15 min Ar, water quench (planned)',surface_preparation='',
                hot_rolling_temperature_C=1000,plate_thickness_mm=3,
                heat_treatment_temperature_C=900,heat_treatment_duration_min=15,
                electrolyte_description='',scan_rate_mV_s=np.nan,reference_electrode='',
                actual_process_confirmed=False,microstructure_confirmed='',
                evidence_file='',measurement_status='awaiting_real_experiment')
            pending.append(row)
    pending_path=OUT/'experimental_results_pending.csv'
    # This file becomes user-owned once real results are entered.
    if not pending_path.exists():
        pd.DataFrame(pending).to_csv(pending_path,index=False)
    coverage={e:dict(records=int(train.RE_element_cat.eq(e).sum()),
        low_Cr_records=int((train.RE_element_cat.eq(e)&train.Cr.lt(5)).sum())) for e in ['Ce','La','Ce+La','none']}
    report=dict(**protocol,selected=best,reused_test=testscore,unweighted_same_preprocessing_reused_test=reference_score,
        candidate_count=len(pool),provisional_batch=pool.iloc[chosen].candidate_id.tolist(),
        literature_RE_coverage=coverage,
        ignored_base_fields=[c for c in BASE if c not in fit.named_steps['features'].numeric_],
        new_target_domain_R2=None,
        AL_status='Prospective queue prepared; no new labels, therefore no new experimental AL update or R2 claim')
    (OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    assert len(output)==9 and len(pending)==15
    assert pd.DataFrame(pending).icorr_A_cm2.isna().all()
    assert np.allclose(pool.Fe_nominal_wt_pct+sum(BASE.values())+pool.RE_ppm/10000,100)
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    with warnings.catch_warnings():
        warnings.simplefilter('ignore');main()
