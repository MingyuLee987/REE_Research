# 실제 문헌 100행 파일럿

> **최신 추가 수집 (2026-10-15): 전체 22편·167개 실험 데이터 포인트.** 임시 분석 후보 117개, 검토 보류 50개입니다. 모두 `pending`이며 사람 검증 완료는 0개입니다.
>
> 이번에는 Elsevier 3편에서 12개, Springer 원문에서 4개를 추가했습니다. Elsevier 원문 API는 여전히 403이며 출판사 검색 결과의 표를 전사한 값은 전부 보류했습니다. Springer Nature·Wiley 부분집합은 9편·111개(임시 후보 77개)입니다. 아래 모델 성능은 이전 실행 이력이며 이번에 재학습하지 않았습니다.

[추가 논문·단위·재현 방법](elsevier_expansion.md)






목표는 철계 희토류 첨가 합금과 그 무첨가 대조군의 `log10(icorr [A/cm²])`를 예측하여, 논문 단위 홀드아웃에서 R² 0.8 달성 여부를 평가하는 것입니다. 점수는 목표이며 보장되지 않습니다.

## 충전 후 현재 실행 상태 (2026-10-15)

- Sol 실제 생성 및 추출 성공. 이전 잔액 부족은 해소됐습니다. 일부 분당 처리 제한에는 대기 후 재시도하도록 구현했습니다.
- 사용자 범위 확정: 희토류 첨가 철계 합금 연구와 해당 논문 대조군만 포함. 일반 철계 합금으로 100행을 채우지 않습니다.
- Europe PMC XML, J-STAGE HTML, Wiley 공식 TDM PDF 및 MDPI 공개 배포 PDF를 확보했습니다. Wiley 토큰으로 원문 한 편을 실제 내려받았습니다.
- **19편을 Sol로 처리해 9편의 33행 추출.** 나머지는 범위 내의 명시적 i_corr가 없어 0행입니다. 빈 논문을 복제하거나 그래프를 임의로 읽어 행을 늘리지 않았습니다.
- 수치 불일치 또는 보고된 조성값 3개 미만인 **7행 보류**, 남은 **26행·9편**을 임시 모델 비교에 사용했습니다. 이 기준은 모델 점수를 보기 전에 적용했습니다.
- 33행 전체, 보류 7행, 임시 분석 26행 모두 `pending`입니다. 사람이 검증한 자료로 바꾸지 않았습니다.
- 임시 비교에서 학습 논문의 내부 CV R² 기준으로 SVR 선택. 같은 seed 42를 유지한 별도 테스트 2편·7행에서 **R²=-1.271, MAE=0.783, RMSE=1.012**. 모두 log10(A/cm²) 타깃 기준이며 R²는 무차원입니다.
- 목표 100행 대비 추출 행이 **67행 부족**합니다. 임시 결과는 100행 연구 성능이나 AL 우월성의 증거가 아닙니다.

### 현재 파일

| 경로 | 내용 |
| --- | --- |
| `data/processed/pilot100/llm_pending_all.csv` | Sol 추출 33행과 원문 근거 |
| `data/processed/pilot100/held_for_review.csv` | 보류 7행과 사유 |
| `data/processed/pilot100/provisional_for_model.csv` | 임시 비교용 26행; 여전히 pending |
| `data/processed/pilot100/review_queue.md` | 사람이 확인할 DOI·시료·수치·원문 위치 |
| `data/processed/pilot100/current_status.json` | 현재 집계 및 저장 응답의 토큰 사용량 |
| `outputs/pilot26_provisional/model_comparison.json` | 5개 모델 내부 CV와 선택 모델 홀드아웃 결과 |
| `outputs/pilot26_provisional/model_comparison.png` | 임시 모델 비교 및 실제값-예측값 그림 |

저장된 응답 기준 입력 288,478 토큰, 출력 19,871 토큰입니다. 이는 청구 금액이 아닙니다. 실패·미저장 요청까지 포함한 실제 비용은 OpenAI 사용량 화면에서 확인해야 합니다. Astra는 호출하지 않았습니다.

```powershell
uv run python scripts/assemble_extraction_pilot.py
uv run ree compare-models data/processed/pilot100/provisional_for_model.csv --rows 26 --allow-provisional --seed 42 --output outputs/pilot26_provisional
```

`--allow-provisional`은 pending 자료에 대한 시험 분석을 명시적으로 허용하며, 결과에는 `provisional_not_human_verified`를 기록합니다. 기본 명령은 계속 verified 자료만 허용합니다. 불확실한 값은 검토/보류하고, 테스트 점수가 낮다고 유리한 시드로 바꾸지 않습니다. 이미 본 테스트 논문은 향후 최종 성능 검증용으로 재사용하지 않는 것이 적절합니다.

### 다음 데이터 단계

추가 원문에서 최소 67개의 새 실험값을 수집하고, 모든 행의 단위·시료·조건을 사람이 확인해야 합니다. 현재 pH·온도·Cr 등 일부 변수의 확보율이 낮아 선택되지 않았고, 녹층 노출시간·열처리 등도 문헌마다 다릅니다. 모델 종류만 바꿔 R² 0.8을 보장할 수 없으며, 데이터 범위·조건 표현과 근거의 품질을 먼저 보강해야 합니다.

PDF를 확보한 경우 다음처럼 추출 입력을 준비할 수 있습니다.

```powershell
uv run ree prepare-pdf paper.pdf --doi 10.1155/2018/4071352 --title 'Paper title' --output-dir data/raw/my_paper
uv run ree extract --source-dir data/raw/my_paper --output-dir data/processed/extractions/my_paper
```

이미 저장한 응답의 근거 검증만 다시 할 때는 `--reuse-response`를 추가합니다. 이 옵션은 새 API 요청 없이 응답을 검증합니다.

## 최초 요청 시 상태 (아래는 충전 전 기록)

- OpenAI Sol 모델 조회: HTTP 200.
- 최소 생성 요청: HTTP 429, `credit_balance_exhausted`. 실제 자동 추출은 잔액 부족으로 실행되지 않았습니다.
- Europe PMC 공식 공개 원문 API를 통해 관련 후보 XML 11편 확보. 이 중 코팅·억제제 논문은 합금 첨가 데이터셋에 포함하지 않습니다.
- 원문 표에서 4편의 14행을 근거와 함께 전사. `data/processed/pilot100/pending_measurements.csv`에 저장했습니다.
- 14행은 인간 검토 전 `pending` 상태입니다. 검증된 100행이 없으므로 실제 모델 학습과 R² 보고는 수행하지 않았습니다.
- 무첨가 대조군의 조성이 보고되지 않은 경우, 미보고 원소, 상한값으로만 보고된 조성, room temperature의 숫자 변환은 빈칸으로 남겼습니다.
- 동일 표에서 평균과 표준편차를 각각 독립 행으로 늘리지 않았습니다. 같은 값이 초록/본문/표에 반복되어도 한 행만 사용합니다.

## 근거와 검토 대상

| 원문 | 전사 행 | 주요 확인 내용 |
| --- | ---: | --- |
| [316L의 Ce 첨가](https://pmc.ncbi.nlm.nih.gov/articles/PMC11720852/) | 3 | 조성 Table 2, Jcorr Table 4, 3.5 wt.% NaCl |
| [La 첨가 탄소강](https://pmc.ncbi.nlm.nih.gov/articles/PMC11433059/) | 5 | Table 1/2. 용액에 La를 억제제로 첨가한 추가 3행 제외 |
| [La/Ce 첨가 저합금강](https://pmc.ncbi.nlm.nih.gov/articles/PMC13304421/) | 3 | Table 1/2, 복합 전해질. P/S 상한은 정확한 수치로 쓰지 않음 |
| [RE 개재물과 초기 부식](https://pmc.ncbi.nlm.nih.gov/articles/PMC6829360/) | 3 | Table 1/2. 분극시험의 3.5 wt.%와 SVET의 0.5 wt.% 구분 |

원본 XML, 표·문단별 근거 블록, 검색 응답은 `data/raw/europepmc/`에 보존했습니다. 이 자료로 사람이 수치·단위·시료 연결·환경·중복을 확인해야 합니다. `pending`을 일괄적으로 `verified`로 바꾸면 안 됩니다.

## 새로 연결한 명령

Sol 추출기는 로컬 원문의 `blocks.json`과 `metadata.json`을 읽고 정해진 JSON 형식으로 추출합니다. 출력도 pending이며, API 실패 시 측정값을 생성하지 않습니다. Astra 전환은 없습니다.

```powershell
uv run ree extract --source-dir data/raw/europepmc/PMC11720852 --output-dir data/processed/extractions/PMC11720852
```

잔액 문제가 해결되고 원문별 추출·검토를 끝내면, 검증한 행을 합쳐 `data/processed/measurements.csv`로 저장합니다. 원소별 미보고는 0으로 바꾸지 않습니다.

```powershell
uv run ree validate data/processed/measurements.csv
uv run ree compare-models data/processed/measurements.csv --rows 100 --seed 42 --output outputs/pilot100
```

## 모델을 고르는 방법

Ridge, SVR, GPR에 Random Forest와 Extra Trees를 더해 비교합니다. 100행과 최소 8개 독립 논문이 필요합니다. 8개는 파일럿 실행 기준이며 충분한 연구 규모를 보장하지 않습니다.

1. 100행보다 많으면 정답을 보지 않고 record_id 순서로 처음 100행을 선택합니다.
2. seed 42로 논문 단위 약 20%를 홀드아웃으로 고정합니다.
3. 나머지 논문 내부의 GroupKFold로 모델 및 하이퍼파라미터를 비교합니다. 확보율 기준 피처 선택과 보간도 각 학습 fold 안에서 수행합니다.
4. 내부 교차검증 R²가 가장 높은 모델 한 개를 고릅니다.
5. 고른 모델을 홀드아웃에 한 번 평가합니다. R², MAE, RMSE와 예측값을 저장합니다.

홀드아웃 점수를 보고 시드/행/모델 설정을 반복 변경하지 않습니다. R² 0.8 미달이면 그대로 보고하고, 추가 독립 문헌 수집·환경 범위 정리·피처 품질 개선을 검토합니다. 테스트 결과를 계속 확인하며 개선하려면 새로운 최종 테스트 논문이 필요합니다.

`outputs/pilot100/model_comparison.json`과 `holdout_predictions.csv`가 실제 실행 결과입니다. 지금은 해당 실제 결과가 없습니다. 별도의 `outputs/pilot100_synthetic_smoke/`는 코드 검증용 합성 데이터 실행이며 연구 성능으로 사용할 수 없습니다.
