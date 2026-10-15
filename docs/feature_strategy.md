# 수집하기 쉬운 입력으로 시작하기

> **피처 수정 v3:** 기본 프로파일을 `corrosion`으로 변경했습니다. 조성·환경·열처리와 파생 변수 28개 후보를 학습 데이터의 확보율에 따라 선택합니다. 14편·110개 개발 비교에서 논문별 MAE가 개선됐지만 전체 R² 개선은 확인하지 못했습니다. [피처 구성·실제 비교 결과](feature_design_v3.md)를 참고하세요. 아래 기존 피처·모델 수치는 이전 실행 이력입니다.


19개 고정 입력을 강제하던 초기 설계를 변경했습니다. 현재 33행 추출·26행 임시 분석까지 진행했으며, 아래 14개 후보는 기본 재현 프로필입니다. AI 부식 원 논문을 참고한 **44개 후보의 literature 프로필**과 검증 계획은 [피처 설계 v2](literature_feature_design.md)에 정리했습니다. 최적 피처 조합이 확정된 것은 아닙니다.

## 기본 모델: 최대 14개 후보

| 후보 | 개수 | 기록 방법 |
| --- | ---: | --- |
| C, Si, Mn, P, S, Cr, Ni, Mo, Cu | 9 | 원문 조성표의 wt.% |
| RE_log1p_ppm | 1 | 보고된 희토류 질량 ppm에서 코드가 계산 |
| RE_element_cat | 1 | Ce, La, Ce+La, 무첨가 확인 시 none |
| temperature_C | 1 | 보고된 실제 온도. room temperature를 임의로 25로 바꾸지 않음 |
| pH | 1 | 보고된 pH. neutral을 임의로 7로 바꾸지 않음 |
| electrolyte_condition_cat | 1 | 용액과 농도를 함께 표현: NaCl_3.5wtpct, NaCl_0.6molL 등 |

같은 용액의 표현은 통일하고, 다른 농도나 첨가제가 있는 용액은 구분합니다. wt.%와 mol/L를 근거 없이 같은 조건으로 합치지 않습니다. 전해질과 온도를 모르는 행을 단순 조성 비교에 섞으면 환경 차이를 합금 효과로 해석할 수 있으므로 별도 범위 제한/민감도 분석이 필요합니다.

## 확장 모델: 추가 7개 후보

Cl 이온 mol/L, 노출 시간, 분극 속도, OCP 안정화 시간, 가스 조건, 원문 모재 상 분류, high_Cr_indicator.

이들은 버리지 않고 수집 양식에 남깁니다. `--profile extended`일 때만 모델 후보가 됩니다. 기본 모델에서 high_Cr_indicator를 뺀 것은 Cr 함량으로부터 파생된 중복 정보이기 때문입니다.

## 결측값을 다루는 방법

1. 원문에 없는 값은 빈칸으로 보존합니다. 미보고 원소 함량은 0이 아닙니다.
2. 누락된 입력 열도 허용합니다. 코드 내부에서 결측 열로 생성합니다.
3. 각 AL 반복의 현재 학습 데이터에서 확보율 80% 이상인 컬럼만 사용합니다. 전부 결측인 열은 항상 제외합니다. 테스트 데이터와 후보 pool은 이 결정에 사용하지 않습니다.
4. 남은 수치 결측은 학습 데이터 중앙값으로 보간하고 결측 표시 변수를 추가합니다. 범주 결측은 unknown입니다. 모델 계산 입력에는 결측이 남지 않지만 원문 데이터가 완전해진 것은 아닙니다.
5. 선택 컬럼은 `learning_curves.csv`의 selected_features에 저장합니다. AL 도중 확보율이 바뀌면 컬럼 구성도 바뀔 수 있습니다. 비교 결과는 이 전체 절차의 효과입니다.

`--min-coverage 1.0`은 현재 학습 데이터에서 결측이 전혀 없는 컬럼만 고릅니다. 향후 테스트/pool에도 결측이 없다는 보장은 아닙니다. 모든 후보가 기준 미달이면 잘못된 0 입력을 만들지 않고 중단합니다.

정답 icorr_A_cm2와 논문/행 식별자, 원문 위치, 근거, 검토 상태는 계속 필수입니다. 확보율 판단에 i_corr와의 상관관계나 테스트 성능은 쓰지 않습니다.

```powershell
uv run ree benchmark data/processed/measurements.csv --profile core --min-coverage 0.8 --output outputs/core
uv run ree benchmark data/processed/measurements.csv --profile extended --min-coverage 0.8 --output outputs/extended
```

전해질·pH·온도를 입력에 포함한 부식 데이터 연구를 참고하여 환경 피처를 유지했습니다. 이 자료는 현재 RE 데이터셋에서의 예측력이나 확보율을 보장하지 않습니다: [조성 및 환경 기여를 함께 다룬 원 논문](https://www.nature.com/articles/s41529-022-00281-x).
