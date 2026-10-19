# 분석을 실행하는 코드

일반 사용자는 상위 README와 결과 폴더부터 확인하세요. 이 폴더는 분석 재현 담당자가 사용합니다.

| 코드 | 목적 |
| --- | --- |
| `exclude_chinese_language.py` | 현재 중국어 논문 제외본 생성과 모델 재평가 |
| `update_ce_experimental_al.py` | 실제 Ce 실험값으로 다음 실험 후보 선택 |
| `casting_target_al.py` | 기본 합금에 대한 잠정 실험 후보 계산 |
| `optimize_preparation_ml.py` | 이전 전체 자료의 조성·제조 방법 모델 비교 |
| `composition_active_learning.py` | 이전 조성별 AL 모의실험 재현 |
| `evaluate_current_holdout.py` | 이전 고정 테스트 모델 비교 |
| `collect_*`, `fetch_*`, `discover_*` | 논문 탐색과 수집 |
| `extract_*`, `assemble_*`, `build_*` | 원문에서 값 추출·표 구성 |
| `report_*`, `interpret_*` | 집계와 해석 |

코드 파일명은 서로 import하는 관계를 유지하기 위해 그대로 뒀습니다. `research_folder_map.json`은 이전 결과 경로와 새 결과 경로의 대응표입니다.
