# REE_Research

희토류 첨가 철계 합금의 조성과 시험 조건으로 **부식전류밀도(i_corr)**를 예측하고 Active Learning과 무작위 선택을 비교하는 연구입니다. 같은 논문의 무첨가 대조군을 포함하며 코팅·용액 억제제·비철 합금은 제외합니다.

2026-10-15 기준 **논문 27편·실험 데이터 포인트 189개**를 저장했습니다. 목표 300개까지 111개가 부족합니다.

| 구분 | 데이터 포인트 |
| --- | ---: |
| 전체 수집본 | 189 |
| 자동 검사 후 임시 분석 후보 | 135 |
| 단위·조성·수치 문제로 보류 | 54 |
| 사람의 원문 검증 완료 | 0 |
| 전체 중 Springer Nature·Wiley 자료 | 121 |

모두 사람 검토 전입니다. Elsevier 그림의 별도 전류 표기 60개는 단위·조건 미확정으로 포함하지 않았습니다. CSV 인용문에 줄바꿈이 있어 편집기의 줄 번호와 데이터 포인트 수는 다릅니다.

## 진행 방식

```text
출판사 API 검색 → 연구 범위 선별 → 원문·표 확보
→ LLM 추출 및 근거 저장 → 사람의 원문·단위·중복 검토
→ 피처 구성 → 모델 학습 → Active Learning vs 무작위 선택
```

Elsevier·Springer Nature 검색 API와 Wiley TDM을 실제 사용했습니다. Elsevier 원문 API의 403은 지속되며 DOI가 일치하는 공개 저장소 전문 등을 별도로 확보합니다. 검색 성공과 원문 확보는 구분합니다.

추출 LLM은 **`gpt-6.1-sol`**입니다. `gpt-6-luna`는 선별용 설정만 준비했으며 이번 추출에는 사용하지 않았습니다. 수치·단위·시료·근거 위치를 보관하고 미보고 값을 임의로 채우지 않습니다.

기본 `corrosion` 피처는 조성·환경·열처리 및 파생 변수 28개 후보입니다. 학습 데이터에서 확보율 50% 이상, 두 논문 이상 관찰, 비상수 조건을 만족하는 변수를 선택합니다. 타깃은 `log10(icorr_A_cm2)`입니다.

Ridge / SVR / GPR 등의 비교 및 Active Learning 코드는 구현했습니다. 최신 임시 후보 135개로 평가를 다시 실행하지는 않았습니다. 이전 실험에서 R² 0.8은 달성하지 못했고, 사람 검증 데이터의 Active Learning 결과도 아직 없습니다. 평가는 논문 단위로 분리하고 관련 재료 계열의 논문 간 중복도 검토해야 합니다.

## 주요 로컬 파일

| 파일 | 내용 |
| --- | --- |
| `data/processed/pilot100/llm_pending_all.csv` | 전체 189개와 출처·근거 |
| `data/processed/pilot100/provisional_for_model.csv` | 임시 후보 135개 |
| `data/processed/pilot100/held_for_review.csv` | 보류 54개 |
| `data/processed/context_v2/features_v3_pending.csv` | 임시 후보의 피처 포함 데이터 |
| `data/processed/round300/status.json` | 목표와 추가 수집 집계 |
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
- [Methods 한국어·영어 초안](docs/manuscript_methods.md): 본문은 이전 판본이며 상단에 최신 집계를 표시했습니다.
- [Elsevier 접근과 공개 전문 확보](docs/elsevier_access.md)
- [상태 기록](docs/status.md) · [파일럿 이력](docs/pilot100.md)
- [초기 워크플로와 실행 이력](docs/workflow_history.md)

이전 모델 점수는 실행 당시 데이터의 기록이며 현재 전체 수집본의 검증 성능으로 해석하지 않습니다.
