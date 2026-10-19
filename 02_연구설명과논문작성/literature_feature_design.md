# AI 부식 논문을 참고한 피처 설계 v2

> **피처 수정 v3:** 기본 프로파일을 `corrosion`으로 변경했습니다. 조성·환경·열처리와 파생 변수 28개 후보를 학습 데이터의 확보율에 따라 선택합니다. 14편·110개 개발 비교에서 논문별 MAE가 개선됐지만 전체 R² 개선은 확인하지 못했습니다. [피처 구성·실제 비교 결과](feature_design_v3.md)를 참고하세요. 아래 기존 피처·모델 수치는 이전 실행 이력입니다.


작성일: 2026-10-15. 연구 범위는 희토류 첨가 철계 합금과 같은 논문의 대조군으로 유지합니다.

핵심 변경은 조성만 늘리는 것이 아니라 **동일한 i_corr가 어떤 재료 상태·환경·노출 이력·시험 방법에서 측정됐는지 함께 기록**하는 것입니다. 개선 가능성을 검증할 설계이며 R² 상승을 보장하지 않습니다.

## 실제 확인한 원 논문

| 원 논문 | 예측 대상 / 확인한 설계 | 이번 연구에 적용할 내용 | 그대로 가져오지 않는 내용 |
| --- | --- | --- | --- |
| [Sasidhar 등, Science Advances (2023), 10.1126/sciadv.adg7992](https://doi.org/10.1126/sciadv.adg7992) | E_pit 예측. 조성·pH·Cl 농도·온도 외에 미세조직/재료 분류와 열처리·시험 방법·scan rate 텍스트를 NLP로 함께 사용 | 열처리, 재료 상태, 시험 프로토콜을 구조화하고 원문 근거를 보존 | E_pit은 i_corr가 아님. 이 논문의 평균 R² 약 0.78±0.06은 우리 모델의 기대 성능이 아님. 수백 행을 쓴 DNN을 26행에 그대로 적용하지 않음 |
| [Scientific Reports (2024), 10.1038/s41598-024-68562-w](https://doi.org/10.1038/s41598-024-68562-w) | 매설강 i_corr 예측. 노출 시간·수분·pH·비저항·염화물·황산염·유기탄소 등을 비교하고 RF/SVR/MLP 평가 | 노출 시간을 중요한 후보로 유지하고 관련 변수를 다 넣는 대신 내부 검증으로 선택 | 토양 비저항·유기탄소를 수용액 희토류 합금 데이터에 억지로 추가하지 않음. 같은 연구의 높은 R²가 논문 간 일반화 성능을 뜻하지 않음 |
| [Nyby 등, Scientific Data (2021), 10.1038/s41597-021-00840-y](https://doi.org/10.1038/s41597-021-00840-y) | 전기화학 부식 데이터 설계. 조성·온도·pH·Cl 농도·미세조직·열처리와 서로 다른 전기화학 지표를 구분 | 단위, 시험 지표, 원문·처리 조건을 함께 기록하는 표준화 기준 | 전체 1274개 레코드를 모두 철계 i_corr로 간주하지 않음. E_pit/i_pass/질량감소율을 i_corr 타깃에 섞지 않음 |

위 논문은 공식 출판사 원문 또는 Europe PMC 공개 원문 XML로 확인했습니다. 로컬 참고 원문은 Git 제외 경로 `01_논문원문과데이터/raw/references/`에 보존했습니다. 문헌에서 가져온 설계 근거와 아래의 프로젝트 구현 선택을 구분해야 합니다.

## 44개 후보를 세 프로필로 분리

| 프로필 | 후보 수 | 용도 |
| --- | ---: | --- |
| `core` | 14 | 기존 결과를 재현할 기본 조성·RE·환경 입력 |
| `extended` | 21 | 기존 시험 조건과 모재 분류 등을 추가 |
| `literature` | 44 | 아래 재료 상태·처리·환경 후보까지 추가 |

44개가 항상 모두 모델에 들어가는 것은 아닙니다. 학습 fold에서 확보율을 확인해 선택하고, 필요하면 `--coverage-grid 0.5 0.8`로 두 기준을 내부 CV에서만 비교합니다. 50% 기준은 데이터가 적은 후보도 검토하기 위한 프로젝트 가정이며 문헌이 보장한 최적값이 아닙니다. 모든 값이 없는 열은 어느 기준에서도 제외합니다.

### v2에서 추가한 컬럼

| 묶음 | 컬럼 | 이유 / 기록 기준 |
| --- | --- | --- |
| 추가 조성 | Al, N, Nb, Ti, V, W, Sb | wt.%. 개재물·제조 원료·모재 조성을 실제 용접금속 조성으로 대체하지 않음 |
| 농도 | nacl_wt_pct | Cl 이온 mol/L와 별개. NaCl 질량%를 원래 단위로 보존 |
| 열처리 | heat_treatment_temperature_C, heat_treatment_duration_h, heat_treatment_cat | 실제 해당 시료의 최종 열처리. 담금질·뜨임이면 마지막 뜨임 온도/시간과 전체 순서 범주를 기록 |
| 초기 조직 | grain_size_um, alloy_family_reported | 부식 전 모재 평균 결정립과 보고된 합금 계열. 원소 함량만으로 분류를 추정하지 않음 |
| 시험 산소 | dissolved_oxygen_mg_L | 실제 수치가 보고된 경우만. gas_condition도 함께 보존 |
| 표면 준비 | surface_finish_grit, surface_preparation_cat | 최종 연마 grit과 준비 방법. polishing 크기 μm를 grit으로 임의 변환하지 않음 |
| 시료 위치 | product_form_cat | base_metal, weld_metal, HAZ, CGHAZ 등. 같은 조성이라도 위치/처리 차이를 구분 |
| 사전 노출 | pre_exposure_protocol_cat, exposure_log1p_h | immersion/wet_dry_cycle/salt_spray 등과 ln(1+exposure_h). 별도 질량감소 시험 시간을 잘못 연결하지 않음 |
| 측정 시 표면 | surface_state_cat | fresh_polished/rust_layer_retained/rust_removed. 실험 준비 단계와 실제 분극 측정 시 상태를 구분 |
| 전해질 계열 | electrolyte_family_cat | NaCl/NaHSO3/mixed_salts 등. 전체 농도 문자열과 분리하여 새로운 농도 조건의 공통 화학계를 표현 |
| 측정 프로토콜 | icorr_method_cat, reference_electrode_cat | Tafel/LPR 등의 측정법과 기준전극. 분극 속도·OCP 안정화 시간도 기존 확장 후보로 유지 |

초기 합금 설계 예측과 이미 노출된 시료의 현재 부식 상태 예측은 서로 다른 사용 상황입니다. 노출 시간을 입력하려면 예측 시점에 그 시간이 알려져 있어야 합니다. 데이터가 모이면 fresh 표면과 rusted 표면을 구분한 분석도 계획하되, 테스트 점수를 보고 유리한 행만 남기지 않습니다.

## 입력에 넣지 않는 값

- paper_id, DOI, 표 번호, 시료 ID, 논문 제목: 출처·분리용 메타데이터.
- evidence_quote와 notes: i_corr 결과나 결과 해석이 포함될 수 있으므로 원문 그대로 벡터화하지 않음.
- 같은 분극/EIS 실험의 Ecorr, Rp, Rct, Tafel 기울기, 환산 부식속도: 실험 전 조성·조건 기반 예측에서는 제외. 특히 LPR의 Rp 등은 i_corr 계산과 직접 연결되어 순환 예측이 될 수 있음.
- 부식 후 측정된 거칠기·녹층 두께·손실량: 사전 예측 입력에서 제외. 이를 사용하는 별도 부식 진단 연구와 구분.
- PREN: 주로 공식 저항과 특정 합금계에 대한 지표이므로 모든 희토류 철계 i_corr에 통용되는 식으로 추가하지 않음.

## Sol이 추가 컬럼을 채우는 방법

`ree enrich-context`는 기존 record_id와 sample_id를 원문과 대조하여 문맥 컬럼만 추출합니다. i_corr나 기존 타깃을 수정하지 않습니다. 새 값마다 해당 필드를 뒷받침하는 원문 인용과 위치가 있어야 저장하며, 값이 없거나 근거가 충돌하면 null로 둡니다. 결과는 여전히 pending입니다.

```powershell
uv run ree enrich-context 01_논문원문과데이터/processed/extractions/PMC11720852/pending_measurements.csv --source-dir 01_논문원문과데이터/raw/europepmc/PMC11720852 --output-dir 01_논문원문과데이터/processed/context_v2/PMC11720852
```

원문 근거는 `field_evidence.json`, 보강 데이터는 `enriched_pending.csv`에 저장합니다. 동일 입력의 저장 응답은 재사용하므로 같은 디렉터리의 재검증에 추가 유료 호출을 하지 않습니다. 원문 인용 일치가 수치·시료 연결의 정확성까지 보장하지는 않아 사람 검토가 필요합니다.

## 검증 계획

1. 기존 26행 테스트 결과(-1.271)는 v1 기록으로 동결합니다.
2. 보강한 각 값의 원문·단위·시료·시점을 검토하고 확보율을 확인합니다.
3. v1에서 확인한 테스트 논문 2편은 개발 평가에서 제외합니다: `10.3390/met15010085`, `10.1155/2018/4071352`.
4. 남은 개발 논문의 GroupKFold 안에서 core/extended/literature와 확보율 기준을 비교합니다. 모델·피처 전처리는 모두 학습 fold에서 적합합니다.
5. 아직 결과를 보지 않은 새 논문을 최종 테스트로 확보하고, 100행 규모가 갖춰지면 사전에 고정한 절차로 평가합니다.
6. 성능이 개선된 경우에만 별도 검증 데이터로 Active Learning vs Random Sampling을 평가합니다. 논문 수·각 조건의 확보율과 예측 시 사용할 수 있는 입력을 함께 보고합니다.

개발 전용 실행 예시(기존 임시 26행 중 제외 후 19행):

```powershell
uv run ree compare-models 01_논문원문과데이터/processed/pilot100/provisional_for_model.csv --rows 19 --allow-provisional --profile literature --coverage-grid 0.5 0.8 --development-only --exclude-papers 10.3390/met15010085 10.1155/2018/4071352 --output 03_분석결과와실험계획/90_이전분석기록/08_초기_개발검증
```

이 예시는 실행 형식입니다. 기존 파일에는 새 문맥 컬럼이 없으므로 새 컬럼의 효과를 검증하려면 먼저 보강 자료를 합친 입력으로 바꿔야 합니다. 개발 CV 수치를 새로운 최종 테스트 R²로 보고하지 않습니다.

## 이번에 실제 실행한 결과

- 대표 논문 3편(La 첨가 탄소강, Ce 첨가 316L, Y 첨가 H13)의 12행에서 비어 있던 문맥을 Sol로 추출했습니다.
- 필드별 원문 근거가 있는 비결측 값 118개를 적용했습니다. 기존 26개 i_corr 값은 변경하지 않았으며 검토 상태도 pending입니다.
- 보강 자료: `01_논문원문과데이터/processed/context_v2/provisional_enriched.csv`. 필드 근거: 각 논문 폴더의 `field_evidence.json`. 확보율: `01_논문원문과데이터/processed/context_v2/feature_coverage.csv`.
- 기존 테스트 논문 2편을 제외한 개발 자료 19행·7편에서 `literature` 프로필과 확보율 0.5/0.8을 내부 GroupKFold로 비교했습니다.
- 내부 CV로 선택된 모델은 **Ridge**, 평균 개발 CV R² **0.2672**, MAE **0.5531**(로그 타깃 단위)입니다. 새 홀드아웃 평가는 하지 않았습니다. 결과는 `03_분석결과와실험계획/90_이전분석기록/08_초기_개발검증/model_comparison.json`입니다.
- 새 열 추가, 기존 열의 확보율 기준 변경, 모델 튜닝을 함께 시험했으므로 이 수치만으로 특정 열의 효과를 입증할 수 없습니다. 아직 R² 0.8 모델을 확보한 것이 아닙니다.
- 노출 시간처럼 시료별 연결 근거가 충분하지 않은 값은 빈칸으로 남았습니다. 44개 열이 모두 채워진 데이터셋은 아닙니다.

실행 명령:

```powershell
uv run python 04_분석실행코드/enrich_context_pilot.py
uv run python 04_분석실행코드/assemble_context_pilot.py
uv run ree compare-models 01_논문원문과데이터/processed/context_v2/provisional_enriched.csv --rows 19 --allow-provisional --profile literature --coverage-grid 0.5 0.8 --development-only --exclude-papers 10.3390/met15010085 10.1155/2018/4071352 --output 03_분석결과와실험계획/90_이전분석기록/08_초기_개발검증
```

첫 스크립트는 저장된 응답이 없을 때 유료 Sol 호출을 합니다. 저장 응답이 있으면 재검증하며 재호출하지 않습니다.
