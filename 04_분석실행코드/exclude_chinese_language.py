"""Chinese-language source exclusion; preserve original measurements and test boundary."""
from pathlib import Path
import json,hashlib,warnings
import numpy as np
import pandas as pd
import joblib
from pypdf import PdfReader
import pymupdf
from bs4 import BeautifulSoup
from sklearn.model_selection import GroupKFold
import optimize_preparation_ml as ml
from evaluate_current_holdout import OLD_TEST,TEST

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'03_분석결과와실험계획/01_현재분석_중국어논문제외'
EXCLUDED=[
 '10.16490/j.cnki.issn.1001-3660.2020.08.025',
 '10.13228/j.boyuan.issn1006-9356.20240777',
 '10.19947/j.issn.1001-7208.2024.09.05',
 '10.13228/j.boyuan.issn1006-9356.20250594',
 '10.11902/1005.4537.2024.043',
 '10.20057/j.1003-8620.2024-00280',
 '10.11900/0412.1961.2022.00359',
 '10.11973/fsyfh-202403006',
 '10.13228/j.boyuan.issn0449-749x.20220781',
 '10.12442/j.issn.1002-185x.20200627',
 '10.3969/j.issn.1674-165x.2024.02.015']

def main():
    OUT.mkdir(exist_ok=True)
    master=ROOT/'01_논문원문과데이터/processed/pilot100/llm_pending_all.csv';raw=pd.read_csv(master)
    eligible=pd.read_csv(ROOT/'01_논문원문과데이터/processed/pilot100/provisional_for_model.csv')
    source=ROOT/'03_분석결과와실험계획/90_이전분석기록/01_조성_제조방법_모델비교/enriched_eligible.csv'
    prepared=pd.read_csv(source)
    audit=[]
    for doi,g in raw.groupby('doi'):
        path=Path(g.source_file.iloc[0]);evidence='';cjk_count=None
        if doi in EXCLUDED:
            if path.suffix.lower()=='.pdf':
                try:
                    reader=PdfReader(path);evidence='\n'.join((p.extract_text() or '') for p in reader.pages[:3])
                except Exception:
                    doc=pymupdf.open(path);evidence='\n'.join(doc[i].get_text() for i in range(min(3,len(doc))))
            else:evidence=BeautifulSoup(path.read_bytes(),'html.parser').get_text(' ',strip=True)
            cjk_count=sum('\u4e00'<=c<='\u9fff' for c in evidence)
            visually_verified={'10.13228/j.boyuan.issn1006-9356.20240777',
                '10.13228/j.boyuan.issn1006-9356.20250594'}
            assert cjk_count>30 or doi in visually_verified,f'Cannot verify Chinese source language: {doi}'
        audit.append(dict(doi=doi,action='exclude' if doi in EXCLUDED else 'retain',
            criterion='Chinese-language article body; not author affiliation or publisher country',
            total_records=len(g),eligible_records=int(eligible.doi.eq(doi).sum()),
            source_file=str(path),source_CJK_count_first_3_pages=cjk_count,
            language_evidence_method=('visual_first_and_second_page_review' if doi in [
                '10.13228/j.boyuan.issn1006-9356.20240777','10.13228/j.boyuan.issn1006-9356.20250594']
                else 'source_text_body_check' if doi in EXCLUDED else 'existing_English_source_record'),
            source_excerpt=evidence[:1200] if doi in EXCLUDED else '',
            evidence_scope='PDF first 3 pages or HTML article body' if doi in EXCLUDED else 'Existing English-language source records retained'))
    pd.DataFrame(audit).to_csv(OUT/'paper_language_decisions.csv',index=False)
    retained=raw[~raw.doi.isin(EXCLUDED)].copy();removed=raw[raw.doi.isin(EXCLUDED)].copy()
    retained.to_csv(OUT/'llm_pending_all_no_chinese.csv',index=False)
    removed.to_csv(OUT/'excluded_chinese_records.csv',index=False)
    filtered=eligible[~eligible.doi.isin(EXCLUDED)].copy()
    filtered.to_csv(OUT/'provisional_for_model_no_chinese.csv',index=False)
    data=prepared[~prepared.doi.isin(EXCLUDED+OLD_TEST)].sort_values('record_id').reset_index(drop=True)
    assert not data.doi.isin(TEST+EXCLUDED+OLD_TEST).any()
    data.to_csv(OUT/'development_enriched_no_chinese.csv',index=False)
    configs=[dict(profile=p,model=name,params=params,weight=w) for p in ml.PROFILES
        for name,params in ml.models() for w in ['uniform','family_equal']]
    protocol=dict(exclusion_basis='Chinese-language body, not nationality/affiliation',excluded_dois=EXCLUDED,
        original_sha256=hashlib.sha256(master.read_bytes()).hexdigest(),
        excluded_records=len(removed),remaining_papers=retained.doi.nunique(),remaining_records=len(retained),
        eligible_papers=filtered.doi.nunique(),eligible_records=len(filtered),
        development_papers=data.doi.nunique(),development_records=len(data),development_families=ml.family(data).nunique(),
        historical_test_dois_still_excluded=OLD_TEST,previous_test_dois=TEST,
        current_fixed_test_records=0,test_R2=None,
        test_status='All previous test papers were removed by the language criterion. No replacement test chosen after observing outcomes.',
        target='log10(icorr_A_cm2)',configurations=len(configs),
        validation='Family-grouped 4-fold selection; 3x3 nested CV repeats full search',
        input_overlay_source=str(source),source_overlay_sha256=hashlib.sha256(source.read_bytes()).hexdigest())
    (OUT/'protocol.json').write_text(json.dumps(protocol,indent=2),encoding='utf8')
    results,preds,idx=ml.search(data,configs);selected=results[idx]
    pd.DataFrame(results).assign(params=lambda d:d.params.map(json.dumps)).to_csv(OUT/'cv_results.csv',index=False)
    (OUT/'selected_configuration.json').write_text(json.dumps(selected,indent=2),encoding='utf8')
    nested=np.zeros(len(data));choices=[]
    for fold,(tr,va) in enumerate(GroupKFold(3).split(data,groups=ml.family(data))):
        inner,_,win=ml.search(data.iloc[tr],configs,folds=3)
        nested[va]=ml.fit_predict(data.iloc[tr],data.iloc[va],inner[win])
        choices.append(dict(fold=fold,configuration=inner[win],validation_record_ids=data.iloc[va].record_id.tolist()))
        print('outer_complete',fold,flush=True)
    _,fit,meta=ml.fit_predict(data,data,selected,keep=True)
    joblib.dump(dict(model=fit,preprocessing=meta,configuration=selected),OUT/'selected_model.joblib')
    pd.DataFrame(dict(record_id=data.record_id,doi=data.doi,target=data.target,
        selected_oof=preds[idx],nested_oof=nested)).to_csv(OUT/'development_predictions.csv',index=False)
    report=dict(**protocol,selected=selected,nested_development=ml.score(data,nested),outer_choices=choices,
        profile_winners=[min([r for r in results if r['profile']==p],key=lambda r:(r['family_macro_rmse'],r['rmse'])) for p in ml.PROFILES])
    (OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    assert len(retained)==228 and retained.doi.nunique()==33
    assert len(data)==112 and not set(retained.record_id)&set(removed.record_id)
    assert hashlib.sha256(master.read_bytes()).hexdigest()==protocol['original_sha256']
    print(json.dumps(dict(counts=protocol,selected=selected,nested=report['nested_development']),indent=2),flush=True)

if __name__=='__main__':
    with warnings.catch_warnings():warnings.simplefilter('ignore');main()
