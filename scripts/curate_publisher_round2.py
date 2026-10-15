"""Preserve ambiguities and add previously missed printed weld annotations."""
import hashlib
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'data/processed/extractions/springer_s10853-025-11514-0'
    path=out/'pending_measurements.csv'
    archive=out/'llm_pending_before_visual_review.csv'
    if not archive.exists():
        archive.write_bytes(path.read_bytes())
    original=pd.read_csv(archive)
    rows=[]
    values=[2.588e-6,5.470e-6,3.990e-6,7.726e-6,1.462e-5]
    for index,source in enumerate(original.to_dict('records')):
        source['exposure_h']=288
        source['notes']=str(source.get('notes',''))+' CONFLICT/quality hold: measured weld composition unreported; Table 1 describes base alloy welded to Q235. Figure 9b identifies 12 days; 0La figure 3.664e-6 versus Table 4 3.644e-6; 0.5La text 1.005e-6 versus figure/table 1.055e-6. Independent human review needed.'
        source['review_flag']='source_conflict'
        rows.append(source)
        new=source.copy()
        new.update(sample_id=source['sample_id'].replace('Table4','Fig9a_0day'),
                   icorr_A_cm2=values[index],icorr_value=values[index],icorr_unit='A/cm2',
                   source_locator=f'page:16;Figure 9a;Tafel;nominal La {index*.5:g} wt.%',
                   original_source_locator='page:16',
                   evidence_quote=f'Figure 9a, 0 day, nominal La {index*.5:g} wt.%, Icorr {values[index]:.4g} A cm^-2',
                   exposure_h=0,extraction_method='agent_visual_printed_annotation_transcription',
                   evidence_match='printed_figure_annotation_not_curve_digitization',
                   notes='Printed Figure 9a annotation; 0-day condition, distinct from 12-day Table 4. CONFLICT/quality hold: Table 1 is base SASS composition; welded to Q235, local measured weld composition unreported. Independent human review needed.')
        new['extraction_model']=None
        new['record_id']=hashlib.sha256((source['paper_id']+new['sample_id']).encode()).hexdigest()[:20]
        rows.append(new)
    frame=pd.DataFrame(rows)
    assert len(frame)==10 and frame.record_id.nunique()==10
    frame.to_csv(path,index=False)
    import json
    run=json.loads((out/'run.json').read_text())
    run.update(rows=10,method='llm_tables_plus_agent_printed_annotation_transcription',
               visual_review_notes='5 Table 4 rows and 5 additional 0-day Fig9a annotations; all held for weld-composition ambiguity')
    (out/'run.json').write_text(json.dumps(run,indent=2),encoding='utf-8')
    print('10 unique weld conditions; all held for composition review; original 5-row extraction archived')


if __name__=='__main__':main()
