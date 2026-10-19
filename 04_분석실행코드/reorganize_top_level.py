"""One-time text-reference migration after the authorized top-level folder moves."""
from pathlib import Path
import re,json,hashlib

ROOT=Path(__file__).resolve().parents[1]
MAP={'data':'01_논문원문과데이터','docs':'02_연구설명과논문작성',
     'outputs':'03_분석결과와실험계획','scripts':'04_분석실행코드',
     'tests':'06_프로그램검사'}
manifest=[]
files=[ROOT/'README.md']
for folder in list(MAP.values())+['05_프로그램공통기능']:
    files.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and p.suffix.lower() in {'.py','.md','.json','.csv','.txt','.toml'}
        and '__pycache__' not in p.parts and '.egg-info' not in str(p)
        and not (folder==MAP['data'] and 'raw' in p.relative_to(ROOT/folder).parts))
for path in files:
    if path.name in {'reorganize_top_level.py'}:continue
    try:old=path.read_text(encoding='utf-8-sig')
    except (UnicodeError,OSError):continue
    new=old
    for src,dst in MAP.items():
        # Folder component only; never change words such as metadata or CSV fields named data.
        new=re.sub(r'(?<![\w])'+re.escape(src)+r'(?=[/\\])',dst,new)
        if path.suffix=='.py':
            new=re.sub(r'((?:ROOT|root|Path\(|/)\s*/?\s*)([\x27\x22])'+src+r'\2',
                lambda m:m.group(1)+m.group(2)+dst+m.group(2),new)
    if path.suffix=='.py' and '05_프로그램공통기능' in str(path):
        new=new.replace('Path(__file__).resolve().parents[1]','Path(__file__).resolve().parents[2]')
    if new!=old:
        before=hashlib.sha256(path.read_bytes()).hexdigest()
        path.write_text(new,encoding='utf8')
        manifest.append(dict(file=str(path.relative_to(ROOT)),before_sha256=before,
            after_sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
(ROOT/'03_분석결과와실험계획/최상위폴더_이동기록.json').write_text(json.dumps(dict(
    date='2026-10-19',folders=MAP,package='05_프로그램공통기능/ree_research',
    note='Raw sources and model binaries preserved. Text path references updated; numerical measurements not changed.',
    updated_files=manifest),ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(dict(updated_text_files=len(manifest))))
