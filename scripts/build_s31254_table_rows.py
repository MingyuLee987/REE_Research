"""Conservative transcription of Table IV; collapse repeated zero-time controls."""
import hashlib
import json
from pathlib import Path
import pandas as pd
from ree_research.schema import prepare

ROOT=Path(__file__).resolve().parents[1]
DOI='10.1007/s11663-025-03817-z'
SOURCE=ROOT/'data/raw/springer_round2/s11663-025-03817-z'


def main():
    rows=[]
    compositions={
        'S0':dict(C=.0189,Si=.3209,S=.0084,Cr=20.01,Ni=18.18,Mo=6.28,Al=.0652,N=.20,RE_ppm=0,RE_element_cat='none'),
        'S2':dict(C=.0191,Si=.3234,S=.0049,Cr=19.86,Ni=18.09,Mo=6.24,Al=.0194,N=.20,RE_ppm=95,RE_element_cat='Ce'),
    }
    groups=[(1150,'S2',[3.479,2.592,1.739,1.291,.992]),
            (1180,'S0',[8.552,6.963,4.516,1.563,3.178]),
            (1180,'S2',[3.479,2.912,2.136,1.563,2.275]),
            (1200,'S2',[3.479,1.101,1.291,2.001,3.082])]
    for temperature,sample,values in groups:
        for minutes,value in zip([0,10,30,60,120],values):
            # The exact same untreated S2 values are repeated in all three groups.
            if sample=='S2' and minutes==0 and temperature!=1150:
                continue
            identifier=f'{sample}_untreated' if minutes==0 else f'{sample}_{temperature}C_{minutes}min'
            note='Table IV transcription; original scale 1e-7 A/cm2. Duplicate zero-time S2 control across three temperature headings retained once. Temperature_C is corrosion bath, not solution-annealing temperature. No independent human review.'
            if sample=='S2':
                note+=' CONFLICT: table caption says S0 and S4 but row labels and body identify S2; sample attribution requires human confirmation.'
            row=compositions[sample] | dict(
                record_id=hashlib.sha256((DOI+identifier).encode()).hexdigest()[:20],
                paper_id=DOI,doi=DOI,sample_id=identifier,icorr_A_cm2=value*1e-7,
                original_icorr_value=value,original_icorr_unit='1e-7 A/cm2',
                temperature_C=25,electrolyte_condition_cat='NaCl_10wtpct',nacl_wt_pct=10,
                heat_treatment_temperature_C=temperature if minutes else None,
                heat_treatment_duration_h=minutes/60,
                heat_treatment_cat='solution_treated' if minutes else 'untreated_control',
                reference_electrode_cat='SCE',icorr_method_cat='potentiodynamic_polarization',
                source_locator=f'page:15;Table IV;{sample};{temperature}C;{minutes}min',
                composition_locator='page:3;Table I;'+sample,condition_locator='page:2;page:3',
                evidence_quote=f'Table IV: {sample}; {temperature} C; {minutes} min; Icorr x 10^-7 (A cm^-2): {value:.3f}',
                source_file=str(SOURCE/'article.pdf'),source_url='https://doi.org/'+DOI,
                retrieval_provider='springer_publisher_pdf',
                extraction_method='agent_visual_table_transcription',
                evidence_match='visual_pdf_table_not_automatic_text_match',
                review_status='pending',review_flag='source_conflict' if sample=='S2' else 'needs_source_review',
                notes=note)
            rows.append(row)
    frame=pd.DataFrame(rows)
    assert len(frame)==18
    prepare(frame,allowed_review_statuses=('pending',))
    out=ROOT/'data/processed/extractions/springer_s11663-025-03817-z'
    out.mkdir(parents=True,exist_ok=True)
    frame.to_csv(out/'pending_measurements.csv',index=False)
    (out/'run.json').write_text(json.dumps({'source':str(SOURCE),'rows':18,
        'method':'agent_visual_table_transcription','usage':{},
        'pdf_sha256':hashlib.sha256((SOURCE/'article.pdf').read_bytes()).hexdigest()},indent=2),encoding='utf-8')
    (out/'deduplication.json').write_text(json.dumps({'reported_table_entries':20,
        'unique_conditions_retained':18,'collapsed':'S2 untreated value 3.479e-7 repeated under 1150/1180/1200 C',
        'source_caption_conflict':'caption S4 versus rows/body S2','human_verified':False},indent=2),encoding='utf-8')
    print('18 pending data points; 2 repeated controls collapsed; 13 S2 points held for attribution review')


if __name__=='__main__':main()
