"""Printed Figure 5 values, not graph-coordinate estimates; all remain pending."""
import hashlib
import json
from pathlib import Path
import pandas as pd
from ree_research.schema import prepare

ROOT=Path(__file__).resolve().parents[1]
DOI='10.1002/adem.202402545'
SOURCE=ROOT/'data/raw/round300/sources/wiley_adem.202402545'


def main():
    compositions=[
        dict(Cr=19.84,Mo=5.98,Ni=18.12,RE_ppm=0,Cu=.79,N=.19,P=.0042,S=.0033),
        dict(Cr=19.93,Mo=6.05,Ni=18.04,RE_ppm=4900,Cu=.81,N=.21,P=.0039,S=.0028),
        dict(Cr=19.97,Mo=5.97,Ni=18.16,RE_ppm=9800,Cu=.79,N=.19,P=.0041,S=.0034),
        dict(Cr=20.13,Mo=6.02,Ni=17.97,RE_ppm=14800,Cu=.81,N=.21,P=.0037,S=.0029),
        dict(Cr=20.26,Mo=5.93,Ni=18.15,RE_ppm=19800,Cu=.79,N=.19,P=.0028,S=.0024),
    ]
    rows=[]
    for days,panel,values in [(0,'5e',[3.582e-7,3.765e-7,1.931e-7,3.031e-7,5.179e-7]),
                              (16,'5f',[1.177e-6,6.668e-6,1.274e-6,2.336e-6,6.429e-7])]:
        for label,c,value in zip(['0La','0.5La','1.0La','1.5La','2.0La'],compositions,values):
            sample=f'{label}_{days}d'
            rows.append(dict(c,record_id=hashlib.sha256((DOI+sample).encode()).hexdigest()[:20],
                paper_id=DOI,doi=DOI,sample_id=sample,icorr_A_cm2=value,
                original_icorr_value=value,original_icorr_unit='A/cm2',
                RE_element_cat='none' if label=='0La' else 'La',
                electrolyte_condition_cat='natural_seawater_unfiltered',electrolyte_family_cat='seawater',
                exposure_h=days*24,reference_electrode_cat='SCE',icorr_method_cat='Tafel_polarization',
                heat_treatment_cat='homogenization_annealed_high_temperature_treated',
                source_locator='page:9;Figure '+panel+';'+label,
                evidence_quote=f'Figure {panel}; {label}; printed current density {value:.4g} A cm^-2',
                composition_locator='page:3;Table 1;'+label,condition_locator='page:3;section 2.6;Figure 5 caption',
                source_file=str(SOURCE/'article.pdf'),source_url='https://doi.org/'+DOI,
                source_sha256=hashlib.sha256((SOURCE/'article.pdf').read_bytes()).hexdigest(),
                source_image_file=str(SOURCE/'figure5_tafel_detail.png'),
                extraction_method='agent_visual_printed_annotation_transcription',
                evidence_match='printed_annotation_visual_transcription_not_exact_text_match',
                retrieval_provider='wiley_tdm_pdf',review_status='pending',review_flag='needs_independent_source_review',
                notes='Figure 5 printed labels 1-5 mapped using arrows/legend to 0/0.5/1.0/1.5/2.0La. Preserve printed exponents; no coordinate digitization. Actual La from Table 1. No numeric bath temperature, pH or scan rate inferred. Same reported material-composition series as prior La studies; group related studies together in future validation. No independent human review.'))
    frame=pd.DataFrame(rows);prepare(frame,allowed_review_statuses=('pending',))
    out=ROOT/'data/processed/extractions/r300_wiley_adem.202402545';out.mkdir(exist_ok=True)
    # Preserve the original zero text-extraction manifest; do not overwrite API responses.
    if (out/'run.json').exists() and not (out/'text_extraction_run.json').exists():
        (out/'text_extraction_run.json').write_bytes((out/'run.json').read_bytes())
    frame.to_csv(out/'pending_measurements.csv',index=False)
    (out/'run.json').write_text(json.dumps(dict(rows=10,method='agent_visual_printed_annotation_transcription',
        source=str(SOURCE),usage={},human_verified=False),indent=2),encoding='utf-8')
    print('10 Wiley printed-annotation points; pending independent source review')


if __name__=='__main__':main()
