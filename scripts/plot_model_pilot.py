"""Plot saved results without fitting again or selecting a favorable split."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'outputs/pilot26_provisional'
    report=json.loads((out/'model_comparison.json').read_text(encoding='utf-8'))
    pred=pd.read_csv(out/'holdout_predictions.csv')
    fig, axes=plt.subplots(1,2,figsize=(11,4.5))
    cv=report['cv_results']
    axes[0].barh([r['model'] for r in cv],[r['cv_r2'] for r in cv],color='#547b9c')
    axes[0].axvline(0,color='black',linewidth=.7)
    axes[0].set(xlabel='Internal paper-grouped CV R2',title='Model selection (training papers only)')
    for paper, data in pred.groupby('paper_id'):
        axes[1].scatter(data.actual_log10_icorr,data.predicted_log10_icorr,label=paper,s=45)
    limits=[float(min(pred.actual_log10_icorr.min(),pred.predicted_log10_icorr.min()))-.2,
            float(max(pred.actual_log10_icorr.max(),pred.predicted_log10_icorr.max()))+.2]
    axes[1].plot(limits,limits,'--',color='gray')
    axes[1].set(xlim=limits,ylim=limits,xlabel='Measured log10(icorr [A/cm2])',ylabel='Predicted log10(icorr [A/cm2])',
                title=f"Untouched paper holdout: R2={report['test_r2']:.3f}")
    axes[1].legend(fontsize=7)
    fig.suptitle('Provisional data: 26 rows / 9 papers - NOT human verified')
    fig.tight_layout()
    fig.savefig(out/'model_comparison.png',dpi=160)
    plt.close(fig)
    pred['actual_icorr_A_cm2']=np.power(10.,pred.actual_log10_icorr)
    pred['predicted_icorr_A_cm2']=np.power(10.,pred.predicted_log10_icorr)
    pred.to_csv(out/'holdout_predictions_with_units.csv',index=False)


if __name__=='__main__':
    main()
