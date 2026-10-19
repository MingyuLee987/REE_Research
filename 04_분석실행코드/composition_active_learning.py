"""Composition-query retrospective AL, with target-blind acquisition and paired seeds."""
import hashlib
import json
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.model_selection import GroupKFold, ParameterGrid
from sklearn.pipeline import Pipeline

from ree_research.schema import COMPOSITION,ADDITIONAL_COMPOSITION,ALL_FEATURES,FEATURE_PROFILES,prepare
from ree_research.benchmark import model
from ree_research.model_selection import CoverageTransformer
from evaluate_current_holdout import TEST,OLD_TEST,LA

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'03_분석결과와실험계획/90_이전분석기록/02_조성별_AL_모의실험'
CHEM=COMPOSITION+ADDITIONAL_COMPOSITION+['RE_ppm','RE_element_cat']
NUM=COMPOSITION+ADDITIONAL_COMPOSITION+['RE_log1p_ppm']
CAT=['RE_element_cat']
CONTEXT=['temperature_C','pH','chloride_mol_L','nacl_wt_pct','exposure_log1p_h',
         'scan_rate_mV_s','ocp_stabilization_min','heat_treatment_temperature_C','heat_treatment_duration_h']
CONTEXT_CAT=['electrolyte_group','matrix_group','heat_treatment_group','reference_electrode_cat','icorr_method_cat']
SEEDS=[11,22,33,44,55]
AL_GRID=[('ridge',{'alpha':a}) for a in [1,10,100]]+[
    ('svr',{'C':c,'gamma':.01,'epsilon':.2}) for c in [1,10]]+[
    ('gpr',{'alpha':.1,'kernel__k2__length_scale':3})]


def select_labeled(profile,labeled,cache):
    key=(profile,tuple(sorted(labeled.query_key.unique())))
    if key in cache:return cache[key]
    families=labeled.doi.where(~labeled.doi.isin(LA),'shared_La_SASS_material_series')
    assert families.nunique()>=2
    splits=list(GroupKFold(min(3,families.nunique())).split(labeled,groups=families))
    best=None;best_key=(np.inf,np.inf)
    for name,params in AL_GRID:
        pred=np.empty(len(labeled))
        for tr,va in splits:
            fit=pipeline(profile,name,params).fit(labeled.iloc[tr][ALL_FEATURES],labeled.iloc[tr].target)
            pred[va]=fit.predict(labeled.iloc[va][ALL_FEATURES])
        s=metric(labeled.target,pred,labeled.doi)
        if (s['paper_macro_mae'],s['rmse'])<best_key:
            best_key=(s['paper_macro_mae'],s['rmse']);best=dict(profile=profile,model=name,params=params,**s)
    cache[key]=best
    return best


def register():
    FEATURE_PROFILES['composition_only']=(NUM,CAT)
    FEATURE_PROFILES['composition_context']=(NUM+CONTEXT,CAT+CONTEXT_CAT)


def reg(name,params):
    if name=='extra_trees':return ExtraTreesRegressor(n_estimators=150,random_state=42,n_jobs=1,**params)
    if name=='random_forest':return RandomForestRegressor(n_estimators=150,random_state=42,n_jobs=1,**params)
    return model(name,42).set_params(**params)


def pipeline(profile,name,params):
    return Pipeline([('features',CoverageTransformer(profile,.2)),('regressor',reg(name,params))])


def key_row(row):
    # Missing reports remain a distinct token, never zero. This is a reported-
    # composition signature, not proof of identical true compositions.
    parts=[]
    for c in CHEM:
        v=row[c]
        if pd.isna(v):parts.append(None)
        elif c=='RE_element_cat':parts.append('+'.join(sorted(str(v).split('+'))))
        else:parts.append(float(v))
    return hashlib.sha256(json.dumps(parts).encode()).hexdigest()[:16]


def metric(y,pred,papers):
    return dict(r2=float(r2_score(y,pred)),mae=float(mean_absolute_error(y,pred)),
                rmse=float(np.sqrt(mean_squared_error(y,pred))),
                paper_macro_mae=float(pd.DataFrame({'p':np.asarray(papers),'e':np.abs(np.asarray(y)-pred)}).groupby('p').e.mean().mean()))


def acquire(fit,X_pool,query_keys,rng,batch,labeled,selected_config):
    """No pool targets, test features, or test targets are passed here."""
    pre=fit.named_steps['features'];z=pre.transform(X_pool);zl=pre.transform(labeled[ALL_FEATURES])
    r=fit.named_steps['regressor']
    if selected_config['model']=='gpr':unc=r.predict(z,return_std=True)[1]
    elif hasattr(r,'estimators_'):unc=np.std([t.predict(z) for t in r.estimators_],axis=0)
    else:
        estimates=[];keys=labeled.query_key.unique()
        for _ in range(8):
            sampled=rng.choice(keys,size=len(keys),replace=True)
            idx=np.concatenate([np.flatnonzero(labeled.query_key.to_numpy()==k) for k in sampled])
            estimates.append(reg(selected_config['model'],selected_config['params']).fit(zl[idx],labeled.target.to_numpy()[idx]).predict(z))
        unc=np.std(estimates,axis=0)
    # Greedy batches combine model disagreement and feature-space novelty.
    # Group averaging prevents bundles with more conditions from gaining a sum advantage.
    candidates=list(dict.fromkeys(query_keys));chosen=[];scores_log=[];reference=zl.copy()
    for _ in range(min(batch,len(candidates))):
        dist=np.sqrt(np.min(np.sum((z[:,None,:]-reference[None,:,:])**2,axis=2),axis=1))
        values=[]
        for k in candidates:
            mask=np.asarray(query_keys)==k
            values.append((k,float(np.mean(unc[mask])),float(np.mean(dist[mask]))))
        u=np.array([v[1] for v in values]);d=np.array([v[2] for v in values])
        us=(u-u.min())/(np.ptp(u)+1e-12);ds=(d-d.min())/(np.ptp(d)+1e-12)
        score=.5*us+.5*ds;ix=int(np.argmax(score));k=values[ix][0]
        chosen.append(k);scores_log.append(dict(query_key=k,uncertainty=values[ix][1],novelty=values[ix][2]))
        reference=np.vstack([reference,z[np.asarray(query_keys)==k]]);candidates.remove(k)
    return chosen,scores_log


def main():
    register();OUT.mkdir(parents=True,exist_ok=True)
    master_path=ROOT/'01_논문원문과데이터/processed/pilot100/llm_pending_all.csv'
    m=pd.read_csv(master_path);ids=pd.read_csv(ROOT/'01_논문원문과데이터/processed/pilot100/provisional_for_model.csv').record_id
    data=prepare(m[m.record_id.isin(ids)].copy(),('pending',))
    data['query_key']=data.apply(key_row,axis=1)
    pool=data[~data.doi.isin(TEST+OLD_TEST)].sort_values('record_id').reset_index(drop=True)
    test=data[data.doi.isin(TEST)].sort_values('record_id').reset_index(drop=True)
    assert len(pool)==135 and len(test)==9
    # Remove identical reported-composition signatures from a query pool if they
    # occur in the test set. No target values enter this exclusion rule.
    shared=set(pool.query_key)&set(test.query_key)
    assert not shared,'Shared train/test reported compositions require explicit exclusion'
    groups=pool.doi.where(~pool.doi.isin(LA),'shared_La_SASS_material_series')
    splits=list(GroupKFold(4).split(pool,groups=groups))
    grids={'ridge':{'alpha':[.1,1,10,100]},
           'svr':{'C':[1,10,100],'gamma':['scale',.01,.1],'epsilon':[.1,.2]},
           'gpr':{'alpha':[.05,.5],'kernel__k2__length_scale':[1,3,10]},
           'random_forest':{'min_samples_leaf':[1,3],'max_features':[.7,1.]},
           'extra_trees':{'min_samples_leaf':[1,3],'max_features':[.7,1.]}}
    protocol=dict(input_sha256=hashlib.sha256(master_path.read_bytes()).hexdigest(),
                  pool_records=len(pool),pool_papers=pool.doi.nunique(),pool_reported_compositions=pool.query_key.nunique(),
                  test_papers=TEST,test_records=len(test),historical_test_excluded=OLD_TEST,
                  target='log10(icorr_A_cm2)',composition_key_columns=CHEM,
                  missing_composition_policy='Missing token, never zero; groups are reported signatures only.',
                  profiles=['composition_only','composition_context'],selection='Family-grouped OOF paper-macro MAE, tie-break RMSE',
                  grids=grids,seeds=SEEDS,initial_compositions=10,batch_compositions=5,
                  acquisition='0.5 normalized uncertainty + 0.5 normalized distance; greedy diverse batches; group mean aggregation',
                  AL_model_selection='At each round, select only using currently labeled bundles by up-to-3-fold family-grouped CV. Full-pool CV results are NOT used to configure the AL learner.',
                  AL_grid=AL_GRID,
                  initial='Uniform random 10 reported-composition signatures, identical for both strategies within seed',
                  query_cost='One reported-composition bundle reveals all available conditions for that composition; record cost varies and is reported.',
                  status='Retrospective simulation on pending literature labels; reused exploratory test, not prospective AL or final external validation',
                  pool_ids=pool.record_id.tolist(),test_ids=test.record_id.tolist())
    (OUT/'protocol.json').write_text(json.dumps(protocol,indent=2),encoding='utf8')
    pool[['record_id','doi','sample_id','query_key']+CHEM].to_csv(OUT/'query_bundles.csv',index=False)
    configs=[];selected={};oof=[]
    for profile in protocol['profiles']:
        best_key=(np.inf,np.inf)
        for name,grid in grids.items():
            for params in ParameterGrid(grid):
                pred=np.empty(len(pool))
                for tr,va in splits:
                    fit=pipeline(profile,name,params).fit(pool.iloc[tr][ALL_FEATURES],pool.iloc[tr].target)
                    pred[va]=fit.predict(pool.iloc[va][ALL_FEATURES])
                s=metric(pool.target,pred,pool.doi);config=dict(profile=profile,model=name,params=params,**s)
                configs.append(config)
                if (s['paper_macro_mae'],s['rmse'])<best_key:
                    best_key=(s['paper_macro_mae'],s['rmse']);selected[profile]=config
            print(json.dumps(dict(profile=profile,done_model=name,candidates=len(configs))),flush=True)
    pd.DataFrame(configs).assign(params=lambda d:d.params.map(json.dumps)).to_csv(OUT/'development_cv.csv',index=False)
    (OUT/'selected_before_al_test.json').write_text(json.dumps(selected,indent=2),encoding='utf8')
    curves=[];queries=[];full={};keys=np.array(sorted(pool.query_key.unique()));total=len(keys);cache={};round_configs=[]
    for profile,config in selected.items():
        full_fit=pipeline(profile,config['model'],config['params']).fit(pool[ALL_FEATURES],pool.target)
        full[profile]=metric(test.target,full_fit.predict(test[ALL_FEATURES]),test.doi)
        for seed in SEEDS:
            initial=np.random.default_rng(seed).choice(keys,size=10,replace=False).tolist()
            for strategy in ['random','uncertainty_diversity']:
                chosen=initial.copy();rng=np.random.default_rng(seed+10000)
                while True:
                    labeled=pool[pool.query_key.isin(chosen)].copy()
                    remaining=pool[~pool.query_key.isin(chosen)].copy()
                    round_config=select_labeled(profile,labeled,cache)
                    round_configs.append(dict(profile=profile,seed=seed,strategy=strategy,compositions=len(chosen),configuration=round_config))
                    fit=pipeline(profile,round_config['model'],round_config['params']).fit(labeled[ALL_FEATURES],labeled.target)
                    s=metric(test.target,fit.predict(test[ALL_FEATURES]),test.doi)
                    curves.append(dict(profile=profile,seed=seed,strategy=strategy,compositions=len(chosen),
                                       labeled_records=len(labeled),labeled_papers=labeled.doi.nunique(),**s))
                    if not len(remaining):break
                    batch=min(5,total-len(chosen))
                    if strategy=='random':
                        added=rng.choice(sorted(remaining.query_key.unique()),size=batch,replace=False).tolist();detail=[]
                    else:
                        added,detail=acquire(fit,remaining[ALL_FEATURES],remaining.query_key.to_numpy(),rng,batch,labeled,round_config)
                    assert not set(added)&set(chosen)
                    queries.append(dict(profile=profile,seed=seed,strategy=strategy,after_compositions=len(chosen),
                                        added_query_keys=added,acquisition_scores=detail,
                                        revealed_record_ids=remaining[remaining.query_key.isin(added)].record_id.tolist()))
                    chosen.extend(added)
                print(json.dumps(dict(al_profile=profile,seed=seed,strategy=strategy,completed=True)),flush=True)
    c=pd.DataFrame(curves);c.to_csv(OUT/'learning_curves.csv',index=False)
    summary=c.groupby(['profile','strategy','compositions']).agg(
        r2_mean=('r2','mean'),r2_sd=('r2','std'),mae_mean=('mae','mean'),
        paper_macro_mae_mean=('paper_macro_mae','mean'),labeled_records_mean=('labeled_records','mean'),
        labeled_records_min=('labeled_records','min'),labeled_records_max=('labeled_records','max')).reset_index()
    summary.to_csv(OUT/'learning_curve_summary.csv',index=False)
    paired=c.pivot(index=['profile','seed','compositions'],columns='strategy',values=['r2','mae','labeled_records']).reset_index()
    comparison=[]
    for (profile,budget),d in paired.groupby([('profile',''),('compositions','')]):
        if budget in [10,total]:continue
        delta=d[('r2','uncertainty_diversity')]-d[('r2','random')]
        comparison.append(dict(profile=profile,compositions=int(budget),mean_AL_minus_random_R2=float(delta.mean()),
                               seeds_AL_higher_R2=int((delta>0).sum()),seeds=len(delta)))
    (OUT/'queries.json').write_text(json.dumps(queries,indent=2),encoding='utf8')
    audit=[]
    for q in queries:
        for key in q['added_query_keys']:
            bundle=pool[pool.query_key.eq(key)];first=bundle.iloc[0]
            audit.append(dict(profile=q['profile'],seed=q['seed'],strategy=q['strategy'],
                              after_compositions=q['after_compositions'],query_key=key,
                              revealed_records=len(bundle),dois='|'.join(sorted(bundle.doi.unique())),
                              **{c:first[c] for c in CHEM}))
    pd.DataFrame(audit).to_csv(OUT/'queried_compositions.csv',index=False)
    (OUT/'round_model_choices.json').write_text(json.dumps(round_configs,indent=2),encoding='utf8')
    report=dict(**protocol,selected=selected,full_pool_test=full,paired_by_composition_budget=comparison,
                recommendation_status='No best seed or test-driven stopping budget selected. Curves are repeated diagnostics on an already observed test set.',
                uncertainty_note='Bootstrap/tree disagreement is a heuristic acquisition score, not a calibrated confidence interval.',
                limitation='Equal composition budgets do not guarantee equal numbers of exposed measurements. Future real AL requires experimental labels under fixed conditions.')
    (OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    fig,axs=plt.subplots(1,2,figsize=(11,4.5),layout='constrained')
    for ax,profile in zip(axs,protocol['profiles']):
        for strategy in ['random','uncertainty_diversity']:
            d=summary[(summary.profile==profile)&(summary.strategy==strategy)]
            ax.plot(d.compositions,d.r2_mean,'o-',label=strategy)
            ax.fill_between(d.compositions,d.r2_mean-d.r2_sd,d.r2_mean+d.r2_sd,alpha=.15)
        ax.axhline(0,color='gray',ls='--',lw=1);ax.set(title=profile,xlabel='Queried reported-composition bundles',ylabel='Reused test R2 (log10 target)');ax.legend(fontsize=8)
    fig.suptitle('Retrospective AL: mean +/- SD across 5 paired seeds; pending data',fontsize=11)
    fig.savefig(OUT/'learning_curves.png',dpi=170);plt.close(fig)
    assert len(c)==2*len(SEEDS)*2*10
    print(json.dumps(dict(selected=selected,full_pool_test=full,paired=comparison),indent=2),flush=True)


if __name__=='__main__':
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore',category=FutureWarning)
        warnings.filterwarnings('ignore',message='Skipping features without any observed values')
        main()
