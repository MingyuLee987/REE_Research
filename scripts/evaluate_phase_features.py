"""Paired development ablation, grouping known shared material series across papers."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor
from sklearn.model_selection import GroupKFold
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.pipeline import Pipeline
from ree_research.schema import ALL_FEATURES,prepare
from ree_research.model_selection import CoverageTransformer
from ree_research.benchmark import model

ROOT=Path(__file__).resolve().parents[1]
HISTORICAL_TEST=['10.3390/met15010085','10.1155/2018/4071352']
RELATED_LA=['10.1038/s41529-025-00682-8','10.1002/adem.202402545','10.1007/s10853-025-11514-0']


def main():
    folder=ROOT/'data/processed/phase_v4'
    old=prepare(pd.read_csv(folder/'baseline_context.csv'),('pending',))
    new=prepare(pd.read_csv(folder/'features_pending.csv'),('pending',))
    ids=old.loc[~old.paper_id.isin(HISTORICAL_TEST),'record_id'].sort_values().tolist()
    old=old.set_index('record_id').loc[ids].reset_index()
    new=new.set_index('record_id').loc[ids].reset_index()
    np.testing.assert_array_equal(old.target,new.target)
    np.testing.assert_array_equal(old.paper_id,new.paper_id)
    groups=new.paper_id.where(~new.paper_id.isin(RELATED_LA),'shared_La_SASS_material_series')
    splits=list(GroupKFold(4).split(new,groups=groups))
    out=ROOT/'outputs/phase_v4';out.mkdir(parents=True,exist_ok=True)
    scores=[];features=[];predictions=[]
    for label,data,profile in [('before_reread',old,'corrosion'),('reread_composition',new,'corrosion'),
                               ('reread_phase',new,'phase_corrosion')]:
        for name in ['ridge','svr','gpr','random_forest','extra_trees']:
            predicted=np.empty(len(data))
            for fold,(tr,va) in enumerate(splits):
                if name=='random_forest':regressor=RandomForestRegressor(n_estimators=250,min_samples_leaf=3,max_features=.7,random_state=42,n_jobs=1)
                elif name=='extra_trees':regressor=ExtraTreesRegressor(n_estimators=250,min_samples_leaf=3,max_features=.7,random_state=42,n_jobs=1)
                else:regressor=model(name,42)
                fitted=Pipeline([('features',CoverageTransformer(profile,.5)),('regressor',regressor)])
                fitted.fit(data.iloc[tr][ALL_FEATURES],data.iloc[tr].target)
                predicted[va]=fitted.predict(data.iloc[va][ALL_FEATURES])
                pre=fitted.named_steps['features']
                features.append(dict(configuration=label,model=name,fold=fold,features=pre.numeric_+pre.categorical_,
                    validation_papers=data.iloc[va].paper_id.unique().tolist()))
            error=np.abs(data.target-predicted)
            macro=pd.DataFrame(dict(paper=data.paper_id,error=error)).groupby('paper').error.mean().mean()
            scores.append(dict(configuration=label,profile=profile,model=name,paper_macro_mae=float(macro),
                pooled_oof_mae=float(mean_absolute_error(data.target,predicted)),
                pooled_oof_rmse=float(np.sqrt(mean_squared_error(data.target,predicted))),
                pooled_oof_r2=float(r2_score(data.target,predicted))))
            predictions.extend(dict(record_id=rid,paper_id=doi,configuration=label,model=name,
                actual_log10_icorr=float(y),predicted_log10_icorr=float(p)) for rid,doi,y,p in
                zip(data.record_id,data.paper_id,data.target,predicted))
    scores=pd.DataFrame(scores).sort_values('paper_macro_mae');scores.to_csv(out/'comparison.csv',index=False)
    pd.DataFrame(predictions).to_csv(out/'development_oof_predictions.csv',index=False)
    (out/'fold_features.json').write_text(json.dumps(features,indent=2),encoding='utf-8')
    phase_best=scores[scores.configuration.eq('reread_phase')].iloc[0].to_dict()
    before_best=scores[scores.configuration.eq('before_reread')].iloc[0].to_dict()
    report=dict(status='exploratory_pending_development_only',development_records=len(new),
        development_papers=int(new.paper_id.nunique()),development_groups=int(groups.nunique()),
        historical_test_papers_excluded=HISTORICAL_TEST,known_shared_material_family=RELATED_LA,
        split='GroupKFold(4), identical records and family-grouped splits for all configurations',
        hyperparameters='Fixed; no test-set tuning or favorable seed selection',
        selected_configuration=scores.iloc[0].to_dict(),best_before_reread=before_best,best_phase=phase_best,
        phase_paper_macro_mae_change_pct=100*(phase_best['paper_macro_mae']/before_best['paper_macro_mae']-1),
        human_verified=False,final_generalization_score=False,
        caveat='Known related La series grouped together; other cross-paper material reuse still requires review. CV used for choosing features/models, not a final independent test.')
    (out/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(scores.to_string(index=False));print(json.dumps(report,indent=2))


if __name__=='__main__':main()
