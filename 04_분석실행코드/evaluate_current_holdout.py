"""Predeclared new-paper holdout; select algorithms on family-grouped CV only."""
import hashlib
import json
from pathlib import Path
import time
import warnings

import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.model_selection import GroupKFold, ParameterGrid
from sklearn.pipeline import Pipeline
from ree_research.schema import ALL_FEATURES, prepare
from ree_research.model_selection import CoverageTransformer
from ree_research.benchmark import model

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'03_분석결과와실험계획/90_이전분석기록/04_이전_테스트평가'
TEST=['10.11973/fsyfh-202403006','10.13228/j.boyuan.issn0449-749x.20220781','10.20057/j.1003-8620.2024-00280']
OLD_TEST=['10.3390/met15010085','10.1155/2018/4071352']
LA=['10.1038/s41529-025-00682-8','10.1002/adem.202402545','10.1007/s10853-025-11514-0']


def regressor(name,params):
    if name=='random_forest':return RandomForestRegressor(n_estimators=150,random_state=42,n_jobs=1,**params)
    if name=='extra_trees':return ExtraTreesRegressor(n_estimators=150,random_state=42,n_jobs=1,**params)
    return model(name,42).set_params(**params)


def scores(y,pred,papers):
    return dict(r2=float(r2_score(y,pred)),mae=float(mean_absolute_error(y,pred)),
                rmse=float(np.sqrt(mean_squared_error(y,pred))),
                paper_macro_mae=float(pd.DataFrame({'paper':np.asarray(papers),'error':np.abs(np.asarray(y)-pred)}).groupby('paper').error.mean().mean()))


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    path=ROOT/'01_논문원문과데이터/processed/pilot100/provisional_for_model.csv'
    raw=pd.read_csv(path)
    master=pd.read_csv(ROOT/'01_논문원문과데이터/processed/pilot100/llm_pending_all.csv')
    # Use current master features, preserving the pre-existing eligibility list.
    data=prepare(master[master.record_id.isin(raw.record_id)].copy(),('pending',))
    assert len(data)==151 and data.icorr_A_cm2.notna().all()
    assert data.hold_reason.fillna('').eq('').all()
    train=data[~data.doi.isin(TEST+OLD_TEST)].sort_values('record_id').reset_index(drop=True)
    test=data[data.doi.isin(TEST)].sort_values('record_id').reset_index(drop=True)
    assert len(train)==135 and len(test)==9 and test.doi.nunique()==3
    assert not set(train.doi)&set(test.doi)
    groups=train.paper_id.where(~train.paper_id.isin(LA),'shared_La_SASS_material_series')
    splits=list(GroupKFold(4).split(train,groups=groups))
    grids={'ridge':{'alpha':[.1,1,10,100]},
           'svr':{'C':[1,10,100],'gamma':['scale',.01,.1],'epsilon':[.05,.2]},
           'gpr':{'alpha':[.01,.1,.5],'kernel__k2__length_scale':[1,3,10]},
           'random_forest':{'min_samples_leaf':[1,3,5],'max_features':[.7,1.]},
           'extra_trees':{'min_samples_leaf':[1,3,5],'max_features':[.7,1.]}}
    protocol=dict(input_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                  feature_input_sha256=hashlib.sha256((ROOT/'01_논문원문과데이터/processed/pilot100/llm_pending_all.csv').read_bytes()).hexdigest(),
                  target='log10(icorr_A_cm2)',train_records=len(train),train_papers=train.doi.nunique(),
                  development_family_groups=groups.nunique(),test_records=len(test),test_papers=TEST,
                  historical_test_papers_excluded=OLD_TEST,related_La_papers_grouped=LA,
                  selection='Minimum out-of-fold paper-macro MAE; tie-break pooled OOF RMSE. No test-driven selection.',
                  profiles=[['corrosion',.5],['phase_corrosion',.5],['ml80',.2]],parameter_grids=grids,
                  seed=42,cv_folds=4,human_verified=False,
                  holdout_status='Three added papers absent from recorded previous modeling sets; descriptive values were already visible. Not a blinded external validation.',
                  train_record_ids=train.record_id.tolist(),test_record_ids=test.record_id.tolist())
    (OUT/'protocol.json').write_text(json.dumps(protocol,indent=2),encoding='utf8')
    results=[];best=None;best_key=(float('inf'),float('inf'));best_oof=None
    start=time.time()
    for profile,coverage in protocol['profiles']:
        for name,grid in grids.items():
            for params in ParameterGrid(grid):
                pred=np.empty(len(train));fold_fields=[]
                for tr,va in splits:
                    pipe=Pipeline([('features',CoverageTransformer(profile,coverage)),('regressor',regressor(name,params))])
                    with warnings.catch_warnings():
                        warnings.filterwarnings('ignore',message='Found unknown categories')
                        pipe.fit(train.iloc[tr][ALL_FEATURES],train.iloc[tr].target)
                        pred[va]=pipe.predict(train.iloc[va][ALL_FEATURES])
                    pre=pipe.named_steps['features'];fold_fields.append(pre.numeric_+pre.categorical_)
                metrics=scores(train.target,pred,train.doi)
                row=dict(profile=profile,coverage=coverage,model=name,params=params,**metrics)
                results.append(row)
                key=(metrics['paper_macro_mae'],metrics['rmse'])
                if key<best_key:best_key=key;best=row;best_oof=pred.copy()
            print(json.dumps(dict(done_profile=profile,done_model=name,candidates=len(results),elapsed_s=round(time.time()-start))),flush=True)
    ranking=pd.DataFrame(results).sort_values(['paper_macro_mae','rmse'])
    ranking.assign(params=ranking.params.map(json.dumps)).to_csv(OUT/'cv_results.csv',index=False)
    assert best is not None
    # Freeze the selected configuration before using held-out targets for scoring.
    (OUT/'selected_configuration_before_test.json').write_text(json.dumps(best,indent=2),encoding='utf8')
    pipe=Pipeline([('features',CoverageTransformer(best['profile'],best['coverage'])),('regressor',regressor(best['model'],best['params']))])
    pipe.fit(train[ALL_FEATURES],train.target)
    pred=pipe.predict(test[ALL_FEATURES])
    metrics=scores(test.target,pred,test.doi)
    dummy=DummyRegressor(strategy='mean').fit(np.zeros((len(train),1)),train.target)
    base=dummy.predict(np.zeros((len(test),1)))
    frame=pd.DataFrame(dict(record_id=test.record_id,doi=test.doi,sample_id=test.sample_id,
                            actual_log10_A_cm2=test.target,predicted_log10_A_cm2=pred,
                            actual_A_cm2=test.icorr_A_cm2,predicted_A_cm2=10**pred))
    frame['abs_log10_error']=np.abs(frame.actual_log10_A_cm2-frame.predicted_log10_A_cm2)
    frame.to_csv(OUT/'test_predictions.csv',index=False)
    pd.DataFrame(dict(record_id=train.record_id,doi=train.doi,actual_log10_A_cm2=train.target,
                      oof_predicted_log10_A_cm2=best_oof)).to_csv(OUT/'selected_development_oof.csv',index=False)
    per_paper={doi:scores(d.actual_log10_A_cm2,d.predicted_log10_A_cm2.to_numpy(),d.doi) for doi,d in frame.groupby('doi')}
    pre=pipe.named_steps['features']
    report=dict(status='provisional_pending_not_final_external_validation',**protocol,
                selected_configuration=best,test_metrics=metrics,baseline_test_metrics=scores(test.target,base,test.doi),
                test_per_paper=per_paper,
                test_metrics_original_A_cm2=dict(r2=float(r2_score(test.icorr_A_cm2,10**pred)),
                    mae_A_cm2=float(mean_absolute_error(test.icorr_A_cm2,10**pred)),
                    rmse_A_cm2=float(np.sqrt(mean_squared_error(test.icorr_A_cm2,10**pred)))),
                selected_features=pre.numeric_+pre.categorical_,
                test_target_min=float(test.target.min()),test_target_max=float(test.target.max()),
                approximate_typical_error_factor=float(10**metrics['mae']),
                candidate_count=len(results),elapsed_s=time.time()-start,
                caveat='Best only among declared algorithms, grids and profiles. Small 3-paper holdout; no graph or held records used. Related material reuse beyond known groups needs human review. R2 applies to log10 target, not raw current density.')
    (OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    joblib.dump(pipe,OUT/'selected_model.joblib')
    fig,ax=plt.subplots(figsize=(6,5),layout='constrained')
    for i,(doi,d) in enumerate(frame.groupby('doi')):
        ax.scatter(d.actual_log10_A_cm2,d.predicted_log10_A_cm2,label=f'Test paper {i+1} (n={len(d)})',s=55)
    lim=[min(frame.actual_log10_A_cm2.min(),frame.predicted_log10_A_cm2.min())-.15,
         max(frame.actual_log10_A_cm2.max(),frame.predicted_log10_A_cm2.max())+.15]
    ax.plot(lim,lim,'k--',lw=1);ax.set_xlim(lim);ax.set_ylim(lim)
    ax.set(xlabel='Observed log10(i_corr [A/cm2])',ylabel='Predicted log10(i_corr [A/cm2])',
           title=f"{best['model']} | 3-paper holdout R2 = {metrics['r2']:.3f}\nPending-source exploratory result")
    ax.legend();fig.savefig(OUT/'test_predictions.png',dpi=180);plt.close(fig)
    print(json.dumps(dict(selected=best,test=metrics,baseline=report['baseline_test_metrics']),indent=2),flush=True)


if __name__=='__main__':main()
