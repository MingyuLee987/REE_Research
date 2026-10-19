"""Package existing paper evidence and editable missing-value checklists; no API calls."""
import hashlib
import argparse
import json
from pathlib import Path
import re
import shutil
import pandas as pd
from ree_research.schema import CORROSION_RAW_FEATURES, ADDITIONAL_COMPOSITION
from ree_research.phase_features import PHASE_RAW_CATEGORICAL, PHASE_FRACTIONS

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'01_논문원문과데이터/processed/pilot100/llm_pending_all.csv'
OUT=ROOT/'01_논문원문과데이터/processed/paper_review'


def resolve(value):
    path=Path(str(value))
    return path if path.is_absolute() else ROOT/path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,default=SOURCE)
    parser.add_argument('--output',type=Path,default=OUT)
    args=parser.parse_args()
    output=args.output
    frame=pd.read_csv(args.input)
    fields=list(dict.fromkeys(CORROSION_RAW_FEATURES+ADDITIONAL_COMPOSITION+
        ['RE_ppm']+PHASE_RAW_CATEGORICAL+PHASE_FRACTIONS+['icorr_A_cm2']))
    output.mkdir(parents=True,exist_ok=True)
    index=[];all_missing=[]
    for doi,group in frame.groupby('doi',sort=True):
        slug=re.sub(r'[^A-Za-z0-9._-]+','_',doi)[:100]
        folder=output/slug
        folder.mkdir(exist_ok=True)
        group.to_csv(folder/'measurements_snapshot.csv',index=False,encoding='utf-8-sig')
        edit=folder/'measurements_to_review.csv'
        # A rerun never overwrites the user's manual changes.
        if not edit.exists():group.to_csv(edit,index=False,encoding='utf-8-sig')
        candidates=set()
        for column in ['source_file','composition_source_file','source_image_file']:
            if column in group:
                for value in group[column].dropna():
                    path=resolve(value)
                    if path.is_file():candidates.add(path)
                    if path.parent.is_dir() and path.parent.is_relative_to(ROOT/'01_논문원문과데이터/raw'):
                        for p in path.parent.iterdir():
                            if p.is_file() and (p.name in ['blocks.json','metadata.json'] or
                                p.suffix.lower() in ['.pdf','.xml','.html','.png','.jpg','.jpeg']):candidates.add(p)
        title=doi;manifest=[];pdf_count=0
        for number,path in enumerate(sorted(candidates,key=str),1):
            destination=folder/'sources'/f'{number:02d}_{path.name}'
            destination.parent.mkdir(exist_ok=True)
            if not destination.exists():shutil.copy2(path,destination)
            digest=hashlib.sha256(path.read_bytes()).hexdigest()
            manifest.append(dict(original=str(path.relative_to(ROOT)),copy=str(destination.relative_to(folder)),sha256=digest))
            if path.suffix.lower()=='.pdf':pdf_count+=1
            if path.name=='metadata.json':
                meta=json.loads(path.read_text(encoding='utf-8-sig'))
                if meta.get('title') and meta['title']!=doi:title=meta['title']
        missing=[]
        for _,row in group.iterrows():
            for field in fields:
                if pd.isna(row.get(field)) or (isinstance(row.get(field),str) and not row[field].strip()):
                    missing.append(dict(record_id=row.record_id,sample_id=row.get('sample_id'),doi=doi,
                        field=field,new_value='',reported_unit='',source_page_table='',evidence_quote='',
                        review_decision='',reviewer_notes=''))
        pd.DataFrame(missing).to_csv(folder/'missing_cells_snapshot.csv',index=False,encoding='utf-8-sig')
        checklist=folder/'missing_values_to_review.csv'
        if not checklist.exists():pd.DataFrame(missing).to_csv(checklist,index=False,encoding='utf-8-sig')
        all_missing.extend(missing)
        held=int(group.hold_reason.notna().sum())
        status='local_pdf_available' if pdf_count else 'excerpt_or_other_source_only_check_manifest'
        info=dict(doi=doi,title=title,records=len(group),held_records=held,missing_raw_cells=len(missing),
            source_status=status,pdf_files=pdf_count,files=manifest)
        (folder/'source_manifest.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
        text=f'''# {title}

- DOI: https://doi.org/{doi}
- 실험 보고값: {len(group)}개 / 보류: {held}개
- 원문 상태: {status} / 로컬 PDF: {pdf_count}개
- 확인할 원시 입력·타깃 결측 셀: {len(missing)}개

## 검토 순서

1. `sources/`에서 원문 PDF 또는 HTML/XML과 표 이미지를 확인합니다. PDF가 없으면 DOI 링크에서 원문을 확보하세요. 발췌문만 있는 자료를 전문으로 간주하지 않습니다.
2. `missing_values_to_review.csv`에 값·단위·페이지/표·근거 문구를 기록합니다. 원문에 없으면 `review_decision`에 `not_reported`, 조건상 적용되지 않으면 `not_applicable`, 확인한 값은 `reported`로 표시하세요.
3. 필요하면 `measurements_to_review.csv`에서 같은 record_id의 원시 값을 수정하세요. 결측 목록은 기록용이며 아직 자동 병합되지 않습니다.
4. 원문 검토 후 통합본에 병합하고 파생 피처를 다시 계산해야 합니다. 직접 수정한 값이 기존 학습 파일에 자동 반영되지는 않습니다.

미보고 조성을 0으로 채우거나 강종명으로 추정하지 마세요. 조성은 wt.%, RE는 질량 ppm, i_corr는 A/cm²이며 원래 단위와 배율을 함께 기록하세요. 상 정보는 부식 시험 전 모재 기준입니다. 상분율은 보고된 경우에만 채웁니다. 보류 사유와 review_status는 검토 근거 없이 해제하지 마세요.

`measurements_snapshot.csv`와 `missing_cells_snapshot.csv`는 현재 통합본의 스냅샷입니다. 수정용 파일은 스크립트를 재실행해도 덮어쓰지 않습니다. 원본 통합본은 그대로 보존됩니다. 출처 경로·해시는 `source_manifest.json`에 있습니다.
'''
        (folder/'README.md').write_text(text,encoding='utf-8')
        index.append(dict(doi=doi,title=title,records=len(group),held_records=held,
            missing_raw_cells=len(missing),pdf_files=pdf_count,source_status=status,folder=slug))
    pd.DataFrame(index).to_csv(output/'paper_index.csv',index=False,encoding='utf-8-sig')
    pd.DataFrame(all_missing).to_csv(output/'all_missing_cells_snapshot.csv',index=False,encoding='utf-8-sig')
    lines=['# 논문별 원문·결측치 검토 폴더','',
        f'총 {len(index)}편 / 실험 보고값 {len(frame)}개. 원문은 기존 로컬 파일을 복사했으며 새 다운로드는 수행하지 않았습니다.',
        '', '논문별 README → sources 원문 → missing_values_to_review.csv 순으로 확인하세요. 결측 셀 수는 여러 필드의 합계이며 실험 데이터 개수가 아닙니다.',
        '', '수정용 파일은 재실행 시 보존됩니다. 상위 CSV 스냅샷과 원문 사본은 원본 통합본을 변경하지 않습니다.',
        '', '| 논문 DOI | 보고값 | 보류 | PDF 파일 | 폴더 |','| --- | ---: | ---: | ---: | --- |']
    for item in index:
        lines.append(f"| {item['doi']} | {item['records']} | {item['held_records']} | {item['pdf_files']} | [열기]({item['folder']}/README.md) |")
    (output/'README.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    assert sum(x['records'] for x in index)==len(frame)
    print(json.dumps(dict(papers=len(index),records=len(frame),papers_with_pdf=sum(x['pdf_files']>0 for x in index),output=str(output)),ensure_ascii=True))


if __name__=='__main__':main()
