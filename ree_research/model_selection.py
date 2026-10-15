"""Choose settings by grouped internal CV, then evaluate one untouched paper holdout."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GroupShuffleSplit, GroupKFold, GridSearchCV
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from .schema import ALL_FEATURES, prepare
from .benchmark import selected_features, transformer, model


class CoverageTransformer(TransformerMixin, BaseEstimator):
    def __init__(self, profile='core', min_coverage=0.8):
        self.profile = profile
        self.min_coverage = min_coverage

    def fit(self, X, y=None):
        self.numeric_, self.categorical_ = selected_features(X, self.profile, self.min_coverage)
        self.preprocessor_ = transformer(self.numeric_, self.categorical_).fit(X)
        return self

    def transform(self, X):
        return self.preprocessor_.transform(X)


def compare(path, output, rows=100, seed=42, allow_synthetic=False, allow_provisional=False,
            profile='core', coverage_grid=None, development_only=False, exclude_papers=None):
    df = prepare(pd.read_csv(path), allowed_review_statuses=('verified', 'pending') if allow_provisional else ('verified',))
    if exclude_papers:
        df = df[~df.paper_id.isin(exclude_papers)].copy()
    synthetic = df.paper_id.astype(str).str.startswith('synthetic-').any()
    if synthetic and not allow_synthetic:
        raise ValueError('Synthetic input requires explicit --allow-synthetic; it cannot establish research R2')
    if len(df) < rows:
        raise ValueError(f'Need {rows} verified measurements; only {len(df)} available. No synthetic padding permitted.')
    # Stable choice without looking at target values; preserve every excluded ID.
    selected = df.sort_values('record_id', kind='stable').iloc[:rows].reset_index(drop=True)
    if not development_only and selected.paper_id.nunique() < 8:
        raise ValueError('Pilot requires at least eight independent papers for grouped CV/holdout')
    if development_only:
        if selected.paper_id.nunique() < 4:
            raise ValueError('At least four development papers required for grouped CV')
        train, test = selected, selected.iloc[:0]
    else:
        tr, te = next(GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=seed).split(selected, groups=selected.paper_id))
        train, test = selected.iloc[tr], selected.iloc[te]
    if not development_only and len(test) < 2:
        raise ValueError('At least two held-out measurements are required to calculate R2')
    cv = GroupKFold(n_splits=min(4, train.paper_id.nunique()))
    if any(len(validation) < 2 for _, validation in cv.split(train, groups=train.paper_id)):
        raise ValueError('Each internal validation fold needs at least two measurements for R2')
    candidates = {
        'ridge': (model('ridge', seed), {'regressor__alpha': [0.1, 1, 10, 100]}),
        'svr': (model('svr', seed), {'regressor__C': [1, 10, 100], 'regressor__gamma': ['scale', 0.01, 0.1], 'regressor__epsilon': [0.05, 0.2]}),
        'gpr': (model('gpr', seed), {'regressor__alpha': [0.01, 0.1, 0.5], 'regressor__kernel__k2__length_scale': [1, 3, 10]}),
        'random_forest': (RandomForestRegressor(n_estimators=200, random_state=seed, n_jobs=1), {'regressor__min_samples_leaf': [1, 3, 5], 'regressor__max_features': [0.7, 1.0]}),
        'extra_trees': (ExtraTreesRegressor(n_estimators=200, random_state=seed, n_jobs=1), {'regressor__min_samples_leaf': [1, 3, 5], 'regressor__max_features': [0.7, 1.0]}),
    }
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    scores, best_estimator, best_cv, winner = [], None, -np.inf, None
    for name, (regressor, grid) in candidates.items():
        pipeline = Pipeline([('features', CoverageTransformer(profile=profile)), ('regressor', regressor)])
        if coverage_grid:
            if not all(0 < value <= 1 for value in coverage_grid):
                raise ValueError('Coverage grid values must be in (0, 1]')
            grid = {**grid, 'features__min_coverage': coverage_grid}
        search = GridSearchCV(pipeline, grid, scoring={'r2': 'r2', 'mae': 'neg_mean_absolute_error'}, refit='r2',
                              cv=cv, n_jobs=1, error_score='raise')
        search.fit(train[ALL_FEATURES], train.target, groups=train.paper_id)
        index = search.best_index_
        scores.append({'model': name, 'cv_mae': -search.cv_results_['mean_test_mae'][index], 'cv_r2': search.best_score_,
                       'best_params': search.best_params_})
        if np.isfinite(search.best_score_) and search.best_score_ > best_cv:
            best_cv, best_estimator, winner = search.best_score_, search.best_estimator_, name
    if best_estimator is None:
        raise ValueError('No candidate produced a finite internal CV R2; acquire more independent data')
    # No repeated search for favorable test partitions or target-adjusting transformations.
    pred = best_estimator.predict(test[ALL_FEATURES]) if not development_only else None
    provisional = not selected.review_status.eq('verified').all()
    report = {'status': 'synthetic_smoke_only' if synthetic else ('provisional_not_human_verified' if provisional else 'completed'), 'rows': rows, 'seed': seed, 'selected_by': 'grouped CV R2', 'winner': winner,
              'train_papers': train.paper_id.unique().tolist(), 'test_papers': test.paper_id.unique().tolist(),
              'test_rows': len(test), 'test_r2': None if development_only else r2_score(test.target, pred),
              'test_mae': None if development_only else mean_absolute_error(test.target, pred), 'test_rmse': None if development_only else float(np.sqrt(mean_squared_error(test.target, pred))),
              'target_r2': 0.8, 'target_met': None if synthetic or provisional or development_only else bool(r2_score(test.target, pred) >= 0.8), 'cv_results': scores,
              'evaluation_mode': 'development_cv_only' if development_only else 'grouped_cv_plus_holdout',
              'excluded_papers': exclude_papers or [], 'feature_profile': profile, 'coverage_grid': coverage_grid or [0.8],
              'included_record_ids': selected.record_id.tolist(),
              'selected_features': best_estimator.named_steps['features'].numeric_ + best_estimator.named_steps['features'].categorical_}
    (out / 'model_comparison.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    if not development_only:
        pd.DataFrame({'record_id': test.record_id, 'paper_id': test.paper_id, 'actual_log10_icorr': test.target,
                      'predicted_log10_icorr': pred}).to_csv(out / 'holdout_predictions.csv', index=False)
    return report
