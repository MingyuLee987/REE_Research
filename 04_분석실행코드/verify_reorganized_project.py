"""Verify and finalize navigation after the folder reorganization."""
from pathlib import Path
import re,json,sys,py_compile,hashlib
import pandas as pd
import joblib,numpy as np

root=Path(__file__).resolve().parents[1]
guide=(root/'02_연구설명과논문작성/프로젝트_폴더_안내.md').read_text(encoding='utf8')
def root_link(match):
    target=match.group(1)
    if target.startswith('../'):target=target[3:]
    elif not target.startswith(('http:','https:','#')):target='02_연구설명과논문작성/'+target
    return ']('+target+')'
(root/'README.md').write_text(re.sub(r'\]\(([^)]+)\)',root_link,guide),encoding='utf8')
archive=root/'02_연구설명과논문작성/이전_프로젝트_안내.md'
old=archive.read_text(encoding='utf8')
archive.write_text(re.sub(r'\]\(([^)]+)\)',lambda x:']('+('../'+x.group(1)
    if x.group(1).startswith(('02_연구설명과논문작성/','01_논문원문과데이터/','03_분석결과와실험계획/')) else x.group(1))+')',old),encoding='utf8')
mapping=json.loads((root/'04_분석실행코드/research_folder_map.json').read_text(encoding='utf8'))
for src,dst in mapping.items():assert not (root/src).exists() and (root/dst).is_dir()
for f in (root/'04_분석실행코드').glob('*.py'):py_compile.compile(str(f),doraise=True)
sys.path.insert(0,str(root/'04_분석실행코드'))
import optimize_preparation_ml as m
import exclude_chinese_language as e
import casting_target_al as c
import update_ce_experimental_al as u
assert m.OUT.is_dir() and e.OUT.is_dir() and c.OUT.is_dir() and u.OUT.is_dir()
frame=pd.read_csv(e.OUT/'development_enriched_no_chinese.csv')
bundle=joblib.load(e.OUT/'selected_model.joblib')
assert np.isfinite(m.predict_saved(bundle,frame)).all()
filtered=pd.read_csv(e.OUT/'llm_pending_all_no_chinese.csv')
assert len(filtered)==228 and filtered.doi.nunique()==33
pointer=json.loads((root/'01_논문원문과데이터/processed/pilot100/current_analysis_dataset.json').read_text(encoding='utf8'))
assert (root/pointer['filtered_master']).is_file() and (root/pointer['filtered_eligible']).is_file()
r=json.loads((e.OUT/'report.json').read_text(encoding='utf8'))
current_hash=hashlib.sha256((root/'01_논문원문과데이터/processed/pilot100/llm_pending_all.csv').read_bytes()).hexdigest()
relocation=json.loads((root/'03_분석결과와실험계획/최상위폴더_이동기록.json').read_text(encoding='utf8'))
changes=[x for x in relocation['updated_files'] if x['file'].endswith('pilot100\\llm_pending_all.csv') or x['file'].endswith('pilot100/llm_pending_all.csv')]
assert current_hash==r['original_sha256'] or any(x['before_sha256']==r['original_sha256'] and x['after_sha256']==current_hash for x in changes)
guides=[root/p for p in ['README.md','02_연구설명과논문작성/프로젝트_폴더_안내.md','02_연구설명과논문작성/README.md',
 '04_분석실행코드/README.md','03_분석결과와실험계획/README.md','03_분석결과와실험계획/01_현재분석_중국어논문제외/README.md',
 '03_분석결과와실험계획/02_실험계획_Ce첨가/README.md','03_분석결과와실험계획/90_이전분석기록/README.md',
 '01_논문원문과데이터/README.md','01_논문원문과데이터/raw/README.md','01_논문원문과데이터/processed/README.md']]
errors=[]
for doc in guides:
    for target in re.findall(r'\]\(([^)]+)\)',doc.read_text(encoding='utf8')):
        if not target.startswith(('http:','https:','#')) and not (doc.parent/target).exists():
            errors.append((str(doc),target))
assert not errors,errors
result=dict(moved_folders=len(mapping),python_compile='passed',model_reload='passed',
            master_unchanged=True,current_dataset_records=len(filtered),guide_links='passed')
(root/'03_분석결과와실험계획/폴더구성_검증.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(result))
