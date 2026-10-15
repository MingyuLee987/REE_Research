"""Refresh current collection summary while preserving historical model runs."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = '''
> **최신 추가 수집 (2026-10-15): 13편·112행.** Springer Nature OA API로 확보한 새 논문에서 60행을 추가했습니다. 기존 보류 7행을 제외한 임시 분석 후보는 **105행**, 모두 `pending`입니다. 사람 검증 완료는 0행입니다. 이번 60행은 조성 5종 × 온도 3종 × 노출 시간 4종이며, 한 논문의 그림에 인쇄된 수치입니다. 원문 이미지 전사와 Sol 재독 대조를 구분해 보존했습니다.
>
> 아래 33행/26행 모델 결과와 19행 개발 CV는 **추가 수집 이전 실행 기록**입니다. 이번 105행으로 모델을 재학습하거나 새 R²를 계산하지 않았습니다. 단일 논문 60행을 서로 다른 학습·테스트 분할로 나누면 안 됩니다.

'''
for name in ['README.md', 'docs/status.md', 'docs/pilot100.md']:
    path = ROOT / name
    text = path.read_text(encoding='utf-8-sig')
    text = re.sub(r'\n> \*\*최신 추가 수집 \(2026-10-15\).*?\[추가 논문·단위·재현 방법\]\([^\n]+\)\n\n',
                  '\n', text, count=1, flags=re.S)
    first, rest = text.split('\n', 1)
    prefix = 'docs/' if name == 'README.md' else ''
    link = f'[추가 논문·단위·재현 방법]({prefix}springer_collection.md)\n\n'
    path.write_text(first + '\n' + SUMMARY + link + rest, encoding='utf-8')
