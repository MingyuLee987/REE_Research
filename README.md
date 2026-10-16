# REE_Research

최신 집계: **37편·247개 관측 기록**, 임시 모델 후보 151개·보류 96개입니다. Dy·Tb 첨가 철계 비정질 합금의 그래프에서 126개 주기별 관측점을 읽고, 같은 조건의 연속 주기를 중복 집계하지 않도록 마지막 주기 대표값 **14개만 통합본에 추가**했습니다. 추가값은 측정법·조성 검토를 위해 모두 보류했습니다. **최대 400개 목표까지 153개 부족**합니다. [그래프·단위·판독 오차·추가 검색 기록](docs/target400_graph_extraction.md).

이전 집계: 36편·233개, 임시 후보 151개·보류 82개. `data/processed/target300_v2/ml_input_max80_missing.csv`에는 임시 후보에서 **결측률 80% 이하인 피처 36개**를 정리했습니다. [수집 근거·피처 기준·미확보 사유](docs/target300_v2.md). 아래 225개·219개 및 과거 모델 점수도 이전 시점 기록입니다.

기존 경로 갱신 완료: `data/processed/pilot100/llm_pending_all.csv`에 **33편·225개**와 단위 통일 내용을 반영했습니다. 임시 후보 145개·보류 80개이며 `data/processed/paper_review/paper_index.csv`도 33편으로 갱신했습니다. 아래 219개 집계는 이전 수집 시점의 기록입니다.

단위 정리본: `data/processed/units_v1/llm_pending_all.csv` (225개). 명확한 210개의 `icorr_value`·`icorr_unit`을 A/cm²로 통일하고 원래 값·단위·환산 배율을 보존했습니다. 단위 불확실 15개는 계속 보류합니다. [단위 기준과 변환 방법](docs/unit_standardization.md).

추가 수집: 새 논문 2편에서 실험 보고값 6개를 확보한 **33편·225개 별도 통합본**을 `data/processed/expand_20261016/llm_pending_all.csv`에 저장했습니다. 임시 후보 145개·보류 80개이며 기존 파일 잠금에 따른 갱신 상태는 `status.json`을 확인하세요. [추가 원문·수치·보류 사유](docs/expansion_20261016.md).

논문별 원문·결측치 검토 폴더: [`data/processed/paper_review/README.md`](data/processed/paper_review/README.md). 통합 CSV의 31편/219개를 논문별로 나누고 확보한 원문 사본, 수정용 CSV 및 결측 셀 목록을 묶었습니다. 재생성 명령은 `.\.venv\Scripts\python.exe scripts/build_paper_review_folders.py`입니다. 수정용 파일은 재실행해도 덮어쓰지 않으며, 수정 결과는 아직 통합본에 자동 병합되지 않습니다. 이 폴더는 기존 데이터와 동일하게 Git에서 제외됩니다.

상·조성 보강본을 추가했습니다. 전문 블록 25편을 재독해 임시 후보 142개 중 114개에 상 근거를 확보했습니다. 새 프로파일은 46개 후보 피처이며 동일 SVR의 개발 교차검증 R²는 0.110 → 0.246입니다. 최종 독립 검증 결과는 아닙니다. 기존 통합 CSV에도 반영했고 정리본은 `data/processed/phase_v4/measurements_clean.csv`입니다. [재독 범위·피처·검증 결과](docs/phase_features_v4.md)를 확인하세요. 아래 28개 피처 설명은 이전 `corrosion` 프로파일 기준입니다.

희토류 첨가 철계 합금의 조성과 시험 조건으로 **부식전류밀도(i_corr)**를 예측하고 Active Learning과 무작위 선택을 비교하는 연구입니다. 같은 논문의 무첨가 대조군을 포함하며 코팅·용액 억제제·비철 합금은 제외합니다.

2026-10-16 기준 **논문 31편의 실험 보고값 219개**를 저장했습니다. 기존 189개에서 보고값 30개를 추가했으며, 이 중 15개는 원문 단위 문제로 정규화된 i_corr가 미확정입니다. **219개 모두를 유효한 i_corr 데이터로 세면 안 됩니다.** [이번 추가 자료와 보류 근거](docs/add30_20261016.md)를 확인하세요.

| 구분 | 데이터 포인트 |
| --- | ---: |
| 전체 수집 기록(단위 미확정 포함) | 219 |
| 정규화된 i_corr 칸에 값이 있는 기록(검증 전) | 204 |
| 자동 검사 후 임시 분석 후보 | 142 |
| 단위·조성·수치 문제로 보류 | 77 |
| 사람의 원문 검증 완료 | 0 |
| 전체 중 Springer Nature·Wiley 자료 | 121 |

모두 사람 검토 전입니다. 이번에 추가한 AH36 15개는 원문 보고값을 보존하되 `icorr_A_cm2`는 비웠습니다. 별도 Elsevier 그림의 전류 표기 60개는 이번에도 집계에 포함하지 않았습니다. CSV 인용문에 줄바꿈이 있어 편집기의 줄 번호와 데이터 포인트 수는 다릅니다.

## 진행 방식

```text
출판사 API 검색 → 연구 범위 선별 → 원문·표 확보
→ LLM 추출 및 근거 저장 → 사람의 원문·단위·중복 검토
→ 피처 구성 → 모델 학습 → Active Learning vs 무작위 선택
```

Elsevier·Springer Nature 검색 API와 Wiley TDM을 실제 사용했습니다. Elsevier 원문 API의 403은 지속되며 DOI가 일치하는 공개 저장소 전문 등을 별도로 확보합니다. 검색 성공과 원문 확보는 구분합니다.

추출 LLM은 **`gpt-6.1-sol`**입니다. `gpt-6-luna`는 선별용 설정만 준비했으며 이번 추출에는 사용하지 않았습니다. 수치·단위·시료·근거 위치를 보관하고 미보고 값을 임의로 채우지 않습니다.

기본 `corrosion` 피처는 조성·환경·열처리 및 파생 변수 28개 후보입니다. 학습 데이터에서 확보율 50% 이상, 두 논문 이상 관찰, 비상수 조건을 만족하는 변수를 선택합니다. 타깃은 `log10(icorr_A_cm2)`입니다.

Ridge / SVR / GPR 등의 비교 및 Active Learning 코드는 구현했습니다. 상·조성 보강 후 개발 교차검증을 수행했으며 결과는 위 v4 문서를 참고하세요. R² 0.8은 달성하지 못했고, 사람 검증 데이터의 Active Learning 결과도 아직 없습니다. 평가는 논문 단위로 분리하고 관련 재료 계열의 논문 간 중복도 검토해야 합니다.

## 주요 로컬 파일

| 파일 | 내용 |
| --- | --- |
| `data/processed/pilot100/llm_pending_all.csv` | 전체 수집 기록 219개와 출처·근거 |
| `data/processed/pilot100/provisional_for_model.csv` | 임시 후보 142개 |
| `data/processed/pilot100/held_for_review.csv` | 보류 77개 |
| `data/processed/context_v2/features_v3_pending.csv` | 임시 후보의 피처 포함 데이터 |
| `data/processed/add30_20261016/status.json` | 최신 추가 30개 및 집계 |
| `data/processed/round300/status.json` | 10월 15일 추가 수집 당시 집계 |
| `data/raw/` | 원문·API 응답·추출 근거 |

`pilot100`은 기존 폴더명이며 현재 데이터 수의 제한이 아닙니다. 합성 예제는 연구 데이터에 포함하지 않습니다.

## 설치와 확인

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
```

새 환경에서는 `.env.example`을 `.env`로 복사해 본인 키를 입력합니다. 기존 `.env`는 유지하세요. 추출은 유료 API를 호출합니다.

```powershell
.\.venv\Scripts\ree.exe --help
.\.venv\Scripts\ree.exe search --provider springer-meta --query 'cerium steel corrosion' --limit 5 --output data/raw/springer_search.json
.\.venv\Scripts\python.exe -B -m unittest discover -s tests
```

Git에는 코드·문서·빈 양식·키 없는 `.env.example`을 저장합니다. `.env`, 원문과 API 응답(`data/raw/`), 실제 로컬 데이터(`data/processed/`), 실행 결과(`outputs/`)는 제외합니다. 새 clone에는 실제 수집 데이터가 자동으로 생기지 않습니다.

## 상세 문서

- [최신 추가 수집과 300개 목표 현황·재현 명령](docs/collection_300.md)
- [피처 설계와 과거 모델 비교](docs/feature_design_v3.md)
- [Methods 한국어·영어 초안](docs/manuscript_methods.md): 실제 검색어·검색식, 선정 기준, 추출 및 검토 절차를 현재 기록에 맞춰 정리했습니다.
- [실행한 API 검색식 보충 목록](docs/search_query_log.md): 검색식별 저장 응답과 조회 범위를 확인할 수 있습니다.
- [Elsevier 접근과 공개 전문 확보](docs/elsevier_access.md)
- [상태 기록](docs/status.md) · [파일럿 이력](docs/pilot100.md)
- [초기 워크플로와 실행 이력](docs/workflow_history.md)

이전 모델 점수는 실행 당시 데이터의 기록이며 현재 전체 수집본의 검증 성능으로 해석하지 않습니다.
