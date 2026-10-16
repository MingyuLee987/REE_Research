"""Refresh current collection summary while preserving historical model runs."""
from pathlib import Path
import re
import json

ROOT = Path(__file__).resolve().parents[1]
status=json.loads((ROOT/'data/processed/pilot100/current_status.json').read_text())
nw=json.loads((ROOT/'data/processed/nature_wiley/summary.json').read_text())
SUMMARY = f'''
> **최신 추가 수집 (2026-10-15): 전체 {status['extracted_papers']}편·{status['extracted_rows']}개 실험 데이터 포인트.** 임시 분석 후보 {status['provisional_rows']}개, 검토 보류 {status['held_rows']}개입니다. 모두 `pending`이며 사람 검증 완료는 0개입니다.
>
> 이번에는 Elsevier 3편에서 12개, Springer 원문에서 4개를 추가했습니다. Elsevier 원문 API는 여전히 403이며 출판사 검색 결과의 표를 전사한 값은 전부 보류했습니다. Springer Nature·Wiley 부분집합은 {nw['studies']}편·{nw['data_points']}개(임시 후보 {nw['provisional_data_points']}개)입니다. 아래 모델 성능은 이전 실행 이력이며 이번에 재학습하지 않았습니다.

'''
round_path=ROOT/'data/processed/round300/status.json'
if round_path.exists():
    round_status=json.loads(round_path.read_text())
    SUMMARY=f'''
> **최신 수집: 전체 {status['extracted_papers']}편·{status['extracted_rows']}개 실험 데이터 포인트.** 임시 후보 {status['provisional_rows']}개, 보류 {status['held_rows']}개이며 모두 사람 검토 전인 `pending`입니다.
>
> API 추가 검색과 원문 확보로 기존 167개에서 {round_status['new_data_points']}개를 추가했습니다. 목표 300개까지는 {round_status['shortfall']}개 부족합니다. Elsevier 그림의 전류 표기 60개는 단위·전극 면적·조건 대응 미확정으로 합치지 않았습니다. Springer Nature·Wiley 부분집합은 {nw['studies']}편·{nw['data_points']}개입니다. 기존 모델 성능은 이전 데이터의 실행 이력입니다.

'''
latest_path=ROOT/'data/processed/add30_20261016/status.json'
if latest_path.exists():
    latest=json.loads(latest_path.read_text())
    SUMMARY=f'''
> **최신 수집 (2026-10-16): 전체 {latest['total_papers']}편·{latest['total_records']}개 실험 보고값.** 임시 후보 {latest['provisional_candidates']}개, 보류 {latest['held']}개이며 사람 검증 완료는 0개입니다.
>
> 기존 189개에 보고값 30개를 추가했습니다. 이번 추가분 중 15개는 단위 규모가 미확정이라 `icorr_A_cm2`를 비웠습니다. 전체 중 이 칸에 값이 있는 기록은 {latest['normalized_target_present']}개입니다. 219개 모두를 유효한 i_corr 데이터로 세면 안 됩니다. 새 모델 평가는 실행하지 않았고 아래 수치는 과거 이력입니다.

'''
for name in ['docs/status.md', 'docs/pilot100.md']:
    path = ROOT / name
    text = path.read_text(encoding='utf-8-sig')
    text = re.sub(r'\n> \*\*최신(?: 추가)? 수집.*?\[추가 논문·단위·재현 방법\]\([^\n]+\)\n\n',
                  '\n', text, count=1, flags=re.S)
    first, rest = text.split('\n', 1)
    prefix = 'docs/' if name == 'README.md' else ''
    document='add30_20261016.md' if latest_path.exists() else ('collection_300.md' if round_path.exists() else 'elsevier_expansion.md')
    link = f'[추가 논문·단위·재현 방법]({prefix}{document})\n\n'
    path.write_text(first + '\n' + SUMMARY + link + rest, encoding='utf-8')
