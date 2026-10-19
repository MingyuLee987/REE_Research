"""Descriptive audit and within-study contrasts; no causal or pooled meta-analysis."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'03_분석결과와실험계획/90_이전분석기록/05_문헌데이터_해석'


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    master=pd.read_csv(ROOT/'01_논문원문과데이터/processed/pilot100/llm_pending_all.csv')
    provisional=pd.read_csv(ROOT/'01_논문원문과데이터/processed/pilot100/provisional_for_model.csv')
    new=pd.read_csv(ROOT/'01_논문원문과데이터/processed/expand50/new_observations.csv')
    y=master.icorr_A_cm2.dropna()
    counts=provisional.groupby('doi').size().sort_values(ascending=False)
    coverage={c:dict(observed=int(provisional[c].notna().sum()),total=len(provisional),
                     missing_pct=float(provisional[c].isna().mean()*100))
              for c in ['RE_ppm','C','Cr','Ni','Mo','pH','temperature_C','exposure_h','matrix_phase_reported']}
    contrasts=[]
    for doi in ['10.16490/j.cnki.issn.1001-3660.2020.08.025','10.3390/ma17184467',
                '10.3390/ma18010069','10.3390/ma19122685','10.3390/met15010085']:
        d=master[master.doi.eq(doi)]
        base=d[d.RE_ppm.eq(0)]
        assert len(base)==1
        ref=base.iloc[0]
        for _,r in d[d.RE_ppm.gt(0)].iterrows():
            ratio=r.icorr_A_cm2/ref.icorr_A_cm2
            contrasts.append(dict(doi=doi,control_sample=ref.sample_id,sample=r.sample_id,
                                  RE_ppm=float(r.RE_ppm),control_A_cm2=float(ref.icorr_A_cm2),
                                  treated_A_cm2=float(r.icorr_A_cm2),ratio=float(ratio),
                                  reduction_pct=float(100*(1-ratio)),
                                  caution='Illustrative within-study sample contrast; other chemistry may vary; no causal estimate or significance test.'))
    g=new[new.value_origin.eq('graph_estimate')].sort_values('temperature_C')
    ratio=float(g.iloc[-1].icorr_A_cm2/g.iloc[0].icorr_A_cm2)
    bounds=[float(g.iloc[-1].graph_lower_A_cm2/g.iloc[0].graph_upper_A_cm2),
            float(g.iloc[-1].graph_upper_A_cm2/g.iloc[0].graph_lower_A_cm2)]
    summary=dict(total_papers=int(master.doi.nunique()),total_records=len(master),
                 normalized_targets=len(y),unresolved_targets=int(master.icorr_A_cm2.isna().sum()),
                 provisional_records=len(provisional),provisional_papers=int(provisional.doi.nunique()),
                 held_records=len(master)-len(provisional),pending_records=int(master.review_status.eq('pending').sum()),
                 normalized_target_min=float(y.min()),normalized_target_median=float(y.median()),
                 normalized_target_max=float(y.max()),log10_target_span=float(np.log10(y.max()/y.min())),
                 largest_provisional_paper=str(counts.index[0]),largest_paper_records=int(counts.iloc[0]),
                 largest_paper_fraction=float(counts.iloc[0]/len(provisional)),
                 row_weight_concentration_effective_papers=float(1/np.square(counts/len(provisional)).sum()),
                 feature_coverage=coverage,illustrative_within_study_contrasts=contrasts,
                 graph_temperature_ratio_70_over_30=ratio,graph_reading_only_ratio_bounds=bounds,
                 interpretation_scope='Descriptive pending-data audit. No new ML fit, causal estimate, pooled RE effect, statistical CI or significance test.')
    (OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
    fig,axs=plt.subplots(1,3,figsize=(13,4),layout='constrained')
    axs[0].bar(['With normalized\ntarget','Unit unresolved'],[len(y),master.icorr_A_cm2.isna().sum()],color=['#287b8e','#bd8b46'])
    axs[0].set_ylabel('Records');axs[0].set_title('283 pending records / 44 papers')
    for i,v in enumerate([len(y),master.icorr_A_cm2.isna().sum()]):axs[0].text(i,v+3,str(v),ha='center')
    c=pd.DataFrame(contrasts);d=c[c.doi.eq('10.16490/j.cnki.issn.1001-3660.2020.08.025')]
    axs[1].plot([0]+d.RE_ppm.tolist(),[1]+d.ratio.tolist(),'o-',color='#287b8e')
    axs[1].set_xlabel('Reported RE content (mass ppm)');axs[1].set_ylabel('i_corr / within-study control')
    axs[1].set_title('A572: lower current, non-monotonic dose trend')
    for _,r in d.iterrows():axs[1].annotate(f'{r.ratio:.2f}',(r.RE_ppm,r.ratio),xytext=(0,8),textcoords='offset points',ha='center')
    vals=g.icorr_A_cm2.to_numpy()*1e6
    err=np.vstack([vals-g.graph_lower_A_cm2.to_numpy()*1e6,g.graph_upper_A_cm2.to_numpy()*1e6-vals])
    axs[2].errorbar(g.temperature_C,vals,yerr=err,fmt='o-',capsize=4,color='#bd6646')
    axs[2].set_xlabel('Temperature (C)');axs[2].set_ylabel('Estimated i_corr (microA/cm2)')
    axs[2].set_title('Same alloy at different temperatures\nError bars: graph reading tolerance')
    for ax in axs:ax.spines[['top','right']].set_visible(False)
    fig.savefig(OUT/'interpretation.png',dpi=180)
    plt.close(fig)
    assert len(y)==251 and len(master)==283 and len(contrasts)==13
    assert all(c['ratio']>0 for c in contrasts)
    print(json.dumps({k:v for k,v in summary.items() if k not in ['feature_coverage','illustrative_within_study_contrasts']},indent=2))
    print(json.dumps(contrasts,ensure_ascii=True,indent=2))


if __name__=='__main__':main()
