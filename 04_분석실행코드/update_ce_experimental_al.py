"""Update Ce-only AL using real measurements; never use predicted labels.

Fill experimental_results_pending.csv and rerun this script. Model selection
uses development compositions only. The original file is never modified.
"""
from pathlib import Path
import json, warnings
import numpy as np
import pandas as pd
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, Matern
from sklearn.model_selection import GroupKFold
from sklearn.metrics import r2_score, mean_absolute_error

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'03_분석결과와실험계획/02_실험계획_Ce첨가'

def learner(length):
    return GaussianProcessRegressor(kernel=ConstantKernel(1,constant_value_bounds='fixed')*
        Matern(length_scale=length,length_scale_bounds='fixed',nu=2.5),
        alpha=.01,normalize_y=True,optimizer=None,random_state=42)

def x(frame):
    return np.log1p(frame.measured_Ce_ppm.to_numpy(float)).reshape(-1,1)/np.log1p(300)

def main():
    frame=pd.read_csv(OUT/'experimental_results_pending.csv')
    measured=frame[pd.to_numeric(frame.icorr_A_cm2,errors='raise').notna()].copy()
    report=dict(status='awaiting_real_measurements',new_measured_records=len(measured),
        experimental_test_R2=None,claim='No measured targets are fabricated or inferred from literature predictions.')
    if not len(measured):
        (OUT/'experimental_feedback_status.json').write_text(json.dumps(report,indent=2),encoding='utf8')
        print(json.dumps(report));return
    required=['measured_Ce_ppm','protocol_id','melt_id','evidence_file','measurement_status','role',
              'temperature_C','electrolyte_description','scan_rate_mV_s','reference_electrode','surface_preparation']
    assert measured[required].notna().all().all(), 'Measured rows require actual Ce, fixed protocol, melt ID, evidence and role.'
    for field in ['protocol_id','melt_id','evidence_file','electrolyte_description','reference_electrode','surface_preparation']:
        assert measured[field].astype(str).str.strip().ne('').all(),field
    assert measured.actual_process_confirmed.astype(str).str.lower().isin(['true','1']).all()
    assert measured.measurement_status.eq('measured').all()
    assert measured.role.isin(['development','test']).all()
    assert measured.protocol_id.nunique()==1, 'One fixed corrosion/manufacturing protocol per local model.'
    assert np.isfinite(measured.icorr_A_cm2).all() and measured.icorr_A_cm2.gt(0).all()
    assert np.isfinite(measured.measured_Ce_ppm).all() and measured.measured_Ce_ppm.ge(0).all()
    assert measured.measured_La_ppm.fillna(0).eq(0).all(),'Ce-only model cannot mix La-treated specimens.'
    train=measured[measured.role.eq('development')].copy()
    test=measured[measured.role.eq('test')].copy()
    assert not set(train.melt_id)&set(test.melt_id),'Do not split one melt between development and test.'
    assert not set(train.candidate_id)&set(test.candidate_id),'Test Ce levels must be excluded from development.'
    assert train.groupby('melt_id').candidate_id.nunique().le(1).all()
    if train.candidate_id.nunique()<4:
        report.update(status='need_at_least_4_measured_development_Ce_levels',development_levels=train.candidate_id.nunique())
        (OUT/'experimental_feedback_status.json').write_text(json.dumps(report,indent=2),encoding='utf8')
        print(json.dumps(report));return
    # Aggregate coupon repeats inside a melt; never count them as independent melts.
    train['log_target']=np.log10(train.icorr_A_cm2)
    melts=train.groupby(['candidate_id','melt_id'],as_index=False).agg(
        measured_Ce_ppm=('measured_Ce_ppm','mean'),target=('log_target','mean'))
    splits=list(GroupKFold(min(4,melts.candidate_id.nunique())).split(melts,groups=melts.candidate_id))
    configs=[];best=None
    for length in [.3,1.,3.]:
        pred=np.zeros(len(melts))
        for tr,va in splits:
            fit=learner(length).fit(x(melts.iloc[tr]),melts.iloc[tr].target)
            pred[va]=fit.predict(x(melts.iloc[va]))
        result=dict(length_scale=length,development_grouped_oof_R2=float(r2_score(melts.target,pred)),
            development_grouped_oof_MAE=float(mean_absolute_error(melts.target,pred)))
        configs.append(result)
        if best is None or result['development_grouped_oof_MAE']<best['development_grouped_oof_MAE']:best=result
    (OUT/'experimental_selected_before_test.json').write_text(json.dumps(best,indent=2),encoding='utf8')
    fit=learner(best['length_scale']).fit(x(melts),melts.target)
    pool=pd.read_csv(OUT/'candidate_queue.csv')
    reserved_test_ids=frame.loc[frame.role.eq('test'),'candidate_id'].tolist()
    pool=pool[~pool.candidate_id.isin(train.candidate_id.tolist()+reserved_test_ids)].copy()
    # The unmeasured pool uses targets as design coordinates, not measured inputs or labels.
    if len(pool):
        coord=np.log1p(pool.RE_ppm.to_numpy(float)).reshape(-1,1)/np.log1p(300)
        pred,std=fit.predict(coord,return_std=True)
        pool['local_predicted_log10_icorr']=pred;pool['local_predictive_sd_log10']=std
        pool.sort_values('local_predictive_sd_log10',ascending=False).to_csv(OUT/'next_Ce_query_after_measurements.csv',index=False)
    report.update(status='updated_using_real_experiments',development_melts=len(melts),
        development_levels=train.candidate_id.nunique(),selected=best,cv_candidates=configs,
        score_note='OOF score used for model selection is not independent test performance. Predictions are conditional on the fixed protocol.')
    if test.candidate_id.nunique()>=3:
        test['log_target']=np.log10(test.icorr_A_cm2)
        t=test.groupby(['candidate_id','melt_id'],as_index=False).agg(
            measured_Ce_ppm=('measured_Ce_ppm','mean'),target=('log_target','mean'))
        tp=fit.predict(x(t))
        report.update(experimental_test_R2=float(r2_score(t.target,tp)),test_melts=len(t),
            test_warning='Small reserved test set; roles and levels must have been fixed before observing outcomes. Do not tune on this score.')
    (OUT/'experimental_feedback_status.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    with warnings.catch_warnings():
        warnings.simplefilter('ignore');main()
