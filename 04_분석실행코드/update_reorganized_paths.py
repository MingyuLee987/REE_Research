"""Update textual references after the purpose-based output-folder move.

Only code, documentation and the analysis pointer are updated. Measurement
tables, source files, models and historical result JSON are left byte-for-byte.
"""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
mapping=json.loads((ROOT/'04_분석실행코드/research_folder_map.json').read_text(encoding='utf8'))
files=[ROOT/'README.md',ROOT/'01_논문원문과데이터/processed/pilot100/current_analysis_dataset.json']
for base in ['02_연구설명과논문작성','04_분석실행코드','05_프로그램공통기능/ree_research','06_프로그램검사']:
    files.extend(p for p in (ROOT/base).rglob('*') if p.suffix in {'.md','.py'} and p.name!=Path(__file__).name)
changed=[]
for path in files:
    if not path.is_file():continue
    old=path.read_text(encoding='utf8');new=old
    for src,dst in sorted(mapping.items(),key=lambda x:-len(x[0])):
        new=new.replace(src,dst).replace(src.replace('/','\\'),dst.replace('/','\\'))
    if new!=old:
        path.write_text(new,encoding='utf8');changed.append(str(path.relative_to(ROOT)))
(ROOT/'03_분석결과와실험계획/폴더이동_기록.json').write_text(json.dumps(dict(date='2026-10-19',moves=mapping,
    updated_text_files=changed,historical_artifacts='Original recorded paths inside historical CSV/JSON remain provenance, not live output locations.'),ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(dict(updated_files=len(changed)),ensure_ascii=False))
