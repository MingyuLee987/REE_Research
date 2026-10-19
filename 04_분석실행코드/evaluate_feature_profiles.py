"""Development-only, paper-grouped feature ablation; no historical test reuse."""
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
from sklearn.pipeline import Pipeline
from ree_research.benchmark import model
from ree_research.model_selection import CoverageTransformer
from ree_research.schema import ALL_FEATURES, FEATURE_PROFILES, prepare

ROOT=Path(__file__).resolve().parents[1]
HISTORICAL_TEST=['10.3390/met15010085','10.1155/2018/4071352']


def main():
    path=ROOT/'01_논문원문과데이터/processed/context_v2/provisional_enriched.csv'
    full=prepare(pd.read_csv(path),allowed_review_statuses=('pending',))
    # Historical holdout stays excluded even though the collection has grown.
    dev=full[~full.paper_id.isin(HISTORICAL_TEST)].reset_index(drop=True)
    out=ROOT/'03_분석결과와실험계획/90_이전분석기록/07_입력변수_설계비교';out.mkdir(parents=True,exist_ok=True)
    full.to_csv(ROOT/'01_논문원문과데이터/processed/context_v2/features_v3_pending.csv',index=False)
    candidates=sorted(set(sum((a+b for a,b in FEATURE_PROFILES.values()),[])))
    audit=pd.DataFrame({'feature':candidates})
    audit['coverage_fraction']=audit.feature.map(full[candidates].notna().mean())
    audit['reported_papers']=audit.feature.map({c:full.loc[full[c].notna(),'paper_id'].nunique() for c in candidates})
    audit.to_csv(out/'feature_coverage.csv',index=False)
    results=[];predictions=[];selected=[]
    cv=GroupKFold(n_splits=4)
    splits=list(cv.split(dev,groups=dev.paper_id))
    for profile,coverage in [('core',.8),('core',.5),('literature',.5),('corrosion',.5)]:
        for name in ['ridge','svr','gpr']:
            pred=np.empty(len(dev));fold_maes=[]
            for fold,(tr,va) in enumerate(splits):
                pipeline=Pipeline([('features',CoverageTransformer(profile,coverage)),('regressor',model(name,42))])
                pipeline.fit(dev.iloc[tr][ALL_FEATURES],dev.iloc[tr].target)
                pred[va]=pipeline.predict(dev.iloc[va][ALL_FEATURES])
                fold_maes.append(mean_absolute_error(dev.iloc[va].target,pred[va]))
                prep=pipeline.named_steps['features']
                selected.append(dict(profile=profile,model=name,fold=fold,
                    min_train_coverage=coverage,
                    features=prep.numeric_+prep.categorical_,
                    validation_papers=dev.iloc[va].paper_id.unique().tolist()))
            error=abs(dev.target-pred)
            macro=float(pd.DataFrame({'paper':dev.paper_id,'error':error}).groupby('paper').error.mean().mean())
            result=dict(profile=profile,model=name,min_train_coverage=coverage,
                        pooled_oof_r2=r2_score(dev.target,pred),pooled_oof_mae=mean_absolute_error(dev.target,pred),
                        pooled_oof_rmse=float(np.sqrt(mean_squared_error(dev.target,pred))),
                        paper_macro_mae=macro,mean_fold_mae=float(np.mean(fold_maes)))
            results.append(result)
            predictions.extend(dict(record_id=r,paper_id=p,profile=profile,model=name,
                                    min_train_coverage=coverage,
                                    actual_log10_icorr=y,predicted_log10_icorr=float(v))
                               for r,p,y,v in zip(dev.record_id,dev.paper_id,dev.target,pred))
    scores=pd.DataFrame(results).sort_values('paper_macro_mae')
    scores.to_csv(out/'profile_comparison.csv',index=False)
    pd.DataFrame(predictions).to_csv(out/'development_oof_predictions.csv',index=False)
    (out/'fold_features.json').write_text(json.dumps(selected,indent=2),encoding='utf-8')
    report=dict(status='exploratory_pending_development_only',input_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                full_points=len(full),development_points=len(dev),development_papers=dev.paper_id.nunique(),
                excluded_historical_test_papers=HISTORICAL_TEST,split='GroupKFold(4), identical for every profile/model',
                fitting='Coverage, imputation and scaling fitted on each training fold only. Fixed model hyperparameters.',
                selection_metric='paper_macro_mae, each paper equal weight',
                warning='Development comparison used for feature selection; not a final generalization score. No human-verified data.',
                selected_configuration=scores.iloc[0].to_dict())
    (out/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(scores.to_string(index=False))


if __name__=='__main__':main()
