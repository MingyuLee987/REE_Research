"""Finalize navigation and the local package search path after moving top-level directories."""
from pathlib import Path
import sysconfig,re,json
ROOT=Path(__file__).resolve().parents[1]
# Existing editable installation was locked by Windows; a standard .pth entry
# makes the relocated package discoverable without deleting environment files.
site=Path(sysconfig.get_path('purelib'))
(site/'ree_research_project_path.pth').write_text(str(ROOT/'05_프로그램공통기능')+'\n',encoding='utf8')
guide=(ROOT/'02_연구설명과논문작성/프로젝트_폴더_안내.md').read_text(encoding='utf8')
def link(m):
    target=m.group(1)
    if target.startswith('../'):target=target[3:]
    elif not target.startswith(('http:','https:','#')):target='02_연구설명과논문작성/'+target
    return ']('+target+')'
(ROOT/'README.md').write_text(re.sub(r'\]\(([^)]+)\)',link,guide),encoding='utf8')
for base in ['02_연구설명과논문작성','04_분석실행코드']:
    for p in (ROOT/base).glob('*.md'):
        s=p.read_text(encoding='utf8');t=s.replace('-s tests','-s 06_프로그램검사')
        if t!=s:p.write_text(t,encoding='utf8')
print(json.dumps(dict(package_search_path_configured=True,root_guide_updated=True)))
