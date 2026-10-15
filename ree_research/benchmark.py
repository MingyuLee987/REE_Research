import json
import hashlib
import platform
from importlib.metadata import version
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import Ridge
from sklearn.svm import SVR
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, Matern
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from .schema import NUMERIC, CATEGORICAL, FEATURES, ALL_FEATURES, FEATURE_PROFILES, prepare


def selected_features(train, profile='core', min_coverage=0.8):
    if profile not in FEATURE_PROFILES or not 0 < min_coverage <= 1:
        raise ValueError('Invalid feature profile or coverage threshold')
    numeric, categorical = FEATURE_PROFILES[profile]
    # Coverage is estimated solely from currently labeled training rows.
    numeric = [c for c in numeric if train[c].notna().mean() >= min_coverage and train[c].notna().any()]
    categorical = [c for c in categorical if train[c].notna().mean() >= min_coverage and train[c].notna().any()]
    if profile == 'corrosion':
        # Constant fields cannot distinguish training samples. A descriptor seen
        # in only one paper is too weakly supported for this mixed-literature pilot.
        def supported(column):
            present=train[column].notna()
            return train.loc[present,column].nunique()>1 and (
                'paper_id' not in train or train.loc[present,'paper_id'].nunique()>=2)
        numeric=[c for c in numeric if supported(c)]
        categorical=[c for c in categorical if supported(c)]
    if not numeric and not categorical:
        raise ValueError('No sufficiently reported input features in labeled training data')
    return numeric, categorical


def transformer(numeric=NUMERIC, categorical=CATEGORICAL):
    return ColumnTransformer([
        ('numeric', make_pipeline(SimpleImputer(strategy='median', add_indicator=True), StandardScaler()), numeric),
        ('category', make_pipeline(SimpleImputer(strategy='constant', fill_value='unknown'),
                                  OneHotEncoder(handle_unknown='ignore', sparse_output=False)), categorical),
    ])


def model(name, seed):
    if name == 'ridge':
        return Ridge(alpha=1)
    if name == 'svr':
        return SVR(C=10, epsilon=0.1)
    return GaussianProcessRegressor(kernel=ConstantKernel(1, constant_value_bounds='fixed') *
                                    Matern(length_scale=3, length_scale_bounds='fixed', nu=2.5),
                                    alpha=0.05, normalize_y=True, optimizer=None, random_state=seed)


def predictions(name, train, test, pool, seed, committee, profile='core', min_coverage=0.8):
    prep = transformer(*selected_features(train, profile, min_coverage))
    x = prep.fit_transform(train)
    xt = prep.transform(test)
    xp = prep.transform(pool) if len(pool) else None
    y = train.target.to_numpy()
    fitted = model(name, seed).fit(x, y)
    pred = fitted.predict(xt)
    if xp is None:
        return pred, np.array([])
    if name == 'gpr':
        return pred, fitted.predict(xp, return_std=True)[1]
    rng = np.random.default_rng(seed)
    estimates = []
    for _ in range(committee):
        idx = rng.integers(0, len(train), len(train))
        estimates.append(model(name, seed).fit(x[idx], y[idx]).predict(xp))
    return pred, np.std(estimates, axis=0)


def benchmark(path, output, seeds, initial=20, batch=5, budget=50, committee=8, profile='core', min_coverage=0.8):
    if profile not in FEATURE_PROFILES or not 0 < min_coverage <= 1:
        raise ValueError('Use a supported feature profile and 0 < min_coverage <= 1')
    if initial < 3 or batch < 1 or budget < initial or committee < 2:
        raise ValueError('Require initial>=3, batch>=1, budget>=initial, committee>=2')
    df = prepare(pd.read_csv(path))
    if df.paper_id.nunique() < 5:
        raise ValueError('At least five independent papers required for a smoke benchmark')
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    df[ALL_FEATURES].isna().mean().rename('missing_fraction').to_csv(out / 'missingness.csv')
    results, splits, queries = [], [], []
    for seed in seeds:
        train_idx, test_idx = next(GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=seed).split(df, groups=df.paper_id))
        available, test = df.iloc[train_idx].reset_index(drop=True), df.iloc[test_idx]
        if initial >= len(available) or len(test) < 2:
            raise ValueError('Not enough rows after grouped split; reduce initial or acquire more papers')
        start = np.random.default_rng(seed).choice(len(available), initial, replace=False).tolist()
        splits.append({'seed': seed, 'test_papers': sorted(test.paper_id.astype(str).unique().tolist()),
                       'initial_record_ids': available.iloc[start].record_id.tolist()})
        for name in ['ridge', 'svr', 'gpr']:
            for strategy in ['random', 'uncertainty']:
                chosen = start.copy()
                rng = np.random.default_rng(seed + 10000)
                while True:
                    remaining = sorted(set(range(len(available))) - set(chosen))
                    numeric, categorical = selected_features(available.iloc[chosen], profile, min_coverage)
                    pred, uncertainty = predictions(name, available.iloc[chosen], test, available.iloc[remaining], seed, committee, profile, min_coverage)
                    results.append({'seed': seed, 'model': name, 'strategy': strategy, 'n_labeled': len(chosen),
                                    'selected_features': '|'.join(numeric + categorical),
                                    'mae': mean_absolute_error(test.target, pred),
                                    'rmse': float(np.sqrt(mean_squared_error(test.target, pred))),
                                    'r2': r2_score(test.target, pred)})
                    count = min(batch, budget - len(chosen), len(remaining))
                    if count <= 0:
                        break
                    # Selection sees only feature-derived uncertainty; pool targets are never used.
                    order = rng.permutation(len(remaining)) if strategy == 'random' else np.argsort(-uncertainty, kind='stable')
                    selected = [remaining[i] for i in order[:count]]
                    queries.append({'seed': seed, 'model': name, 'strategy': strategy, 'after_n': len(chosen),
                                    'record_ids': available.iloc[selected].record_id.tolist()})
                    chosen.extend(selected)
    scores = pd.DataFrame(results)
    scores.to_csv(out / 'learning_curves.csv', index=False)
    summary = scores.groupby(['model', 'strategy', 'n_labeled'])[['mae', 'rmse', 'r2']].agg(['mean', 'std'])
    summary.to_csv(out / 'summary.csv')
    manifest = {'input': str(Path(path).resolve()), 'seeds': seeds, 'initial': initial, 'batch': batch,
                'budget': budget, 'committee': committee, 'splits': splits, 'queries': queries,
                'protocol': 'Fixed hyperparameters; preprocessing fitted only on labeled rows; no test-driven selection.'}
    manifest['input_sha256'] = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    manifest['feature_profile'] = profile
    manifest['min_labeled_coverage'] = min_coverage
    manifest['versions'] = {'python': platform.python_version(), **{p: version(p) for p in ['numpy', 'pandas', 'scikit-learn']}}
    (out / 'run.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    fig, axes = plt.subplots(1, 3, figsize=(13, 4), sharey=True)
    for ax, name in zip(axes, ['ridge', 'svr', 'gpr']):
        for strategy in ['random', 'uncertainty']:
            grouped = scores[(scores.model == name) & (scores.strategy == strategy)].groupby('n_labeled').mae
            mean, std = grouped.mean(), grouped.std().fillna(0)
            ax.plot(mean.index, mean, label=strategy)
            ax.fill_between(mean.index, mean - std, mean + std, alpha=0.15)
        ax.set(title=name, xlabel='Labeled measurements')
        ax.legend()
    axes[0].set_ylabel('Test MAE (log10 A/cm2)')
    fig.suptitle('Retrospective AL — synthetic demo' if 'demo' in Path(path).name else 'Retrospective AL')
    fig.tight_layout()
    fig.savefig(out / 'learning_curves.png', dpi=160)
    plt.close(fig)
    return scores
