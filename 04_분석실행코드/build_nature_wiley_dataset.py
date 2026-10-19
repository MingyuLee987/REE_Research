"""Export confirmed publisher studies without using DOI prefix as publisher proof."""
import json
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
# Individually identified publisher pages; publishers can change, so use an explicit registry.
PUBLISHERS={
 '10.1002/adem.202402545':'Wiley',
 '10.1007/s42243-025-01553-x':'Springer Nature',
 '10.1038/s41598-024-67799-9':'Springer Nature',
 '10.1038/s41529-025-00682-8':'Springer Nature',
 '10.1007/s10853-025-11514-0':'Springer Nature',
 '10.1007/s11663-025-03817-z':'Springer Nature',
 '10.1007/s11663-026-04267-x':'Springer Nature',
 '10.1155/2018/4071352':'Wiley',
 '10.1002/maco.201911150':'Wiley',
 '10.1002/maco.202213672':'Wiley',
}


def main():
    frame=pd.read_csv(ROOT/'01_논문원문과데이터/processed/pilot100/llm_pending_all.csv')
    selected=frame[frame.paper_id.isin(PUBLISHERS)].copy()
    selected['publisher']=selected.paper_id.map(PUBLISHERS)
    selected['publisher_page']=selected.paper_id.map(lambda doi:
        'https://onlinelibrary.wiley.com/doi/'+doi if PUBLISHERS[doi]=='Wiley'
        else 'https://doi.org/'+doi)
    assert selected.record_id.is_unique and selected.icorr_A_cm2.gt(0).all()
    assert selected.review_status.eq('pending').all()
    ready=selected[selected.hold_reason.fillna('').eq('')].copy()
    out=ROOT/'01_논문원문과데이터/processed/nature_wiley'
    out.mkdir(parents=True,exist_ok=True)
    selected.to_csv(out/'measurements_pending.csv',index=False)
    ready.to_csv(out/'provisional_for_model.csv',index=False)
    selected[~selected.record_id.isin(ready.record_id)].to_csv(out/'held_for_review.csv',index=False)
    groups=[{'doi':doi,'publisher':PUBLISHERS[doi],'data_points':len(group),
             'provisional_data_points':int(group.hold_reason.fillna('').eq('').sum())}
            for doi,group in selected.groupby('paper_id')]
    summary={'target':'at least 100 total data points from Springer Nature and Wiley, including previously collected',
             'data_points':len(selected),'studies':selected.paper_id.nunique(),
             'provisional_data_points':len(ready),'held_data_points':len(selected)-len(ready),
             'human_verified_data_points':0,
             'publisher_counts':selected.publisher.value_counts().to_dict(),
             'studies_detail':groups,'full_collection_data_points':len(frame),
             'full_collection_added_since_112_point_baseline':len(frame)-112,
             'target_met_for_collected_points':len(selected)>=100,
             'target_met_for_verified_points':False}
    (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
