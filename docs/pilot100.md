# 실제 문헌 100행 파일럿

목표는 철계 희토류 첨가 합금과 그 무첨가 대조군의 `log10(icorr [A/cm²])`를 예측하여, 논문 단위 홀드아웃에서 R² 0.8 달성 여부를 평가하는 것입니다. 점수는 목표이며 보장되지 않습니다.

## 현재 실행 상태 (2026-10-15)

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
