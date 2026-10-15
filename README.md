# REE_Research

합성 예제 CSV·합성 실행 결과·Python 캐시는 정리했습니다. 실제 실험 데이터는 [전체 167개 수집본](data/processed/pilot100/llm_pending_all.csv), [피처 포함 임시 후보 117개](data/processed/context_v2/features_v3_pending.csv)에서 확인하세요. 아래 합성 예제 실행 명령은 필요할 때 파일을 다시 생성하는 용도입니다.

논문 작성용 [Methods 영어·한국어 초안](docs/manuscript_methods.md): 출판사별 검색·원문 확보 경로, 사용 LLM(`gpt-6.1-sol`), 추출·단위 변환·중복 처리·검토 상태를 실제 기록에 맞춰 정리했습니다.

> **피처 수정 v3:** 기본 프로파일을 `corrosion`으로 변경했습니다. 조성·환경·열처리와 파생 변수 28개 후보를 학습 데이터의 확보율에 따라 선택합니다. 14편·110개 개발 비교에서 논문별 MAE가 개선됐지만 전체 R² 개선은 확인하지 못했습니다. [피처 구성·실제 비교 결과](docs/feature_design_v3.md)를 참고하세요. 아래 기존 피처·모델 수치는 이전 실행 이력입니다.


> **최신 추가 수집 (2026-10-15): 전체 22편·167개 실험 데이터 포인트.** 임시 분석 후보 117개, 검토 보류 50개입니다. 모두 `pending`이며 사람 검증 완료는 0개입니다.
>
> 이번에는 Elsevier 3편에서 12개, Springer 원문에서 4개를 추가했습니다. Elsevier 원문 API는 여전히 403이며 출판사 검색 결과의 표를 전사한 값은 전부 보류했습니다. Springer Nature·Wiley 부분집합은 9편·111개(임시 후보 77개)입니다. 아래 모델 성능은 이전 실행 이력이며 이번에 재학습하지 않았습니다.

[추가 논문·단위·재현 방법](docs/elsevier_expansion.md)



Elsevier 공개 전문 읽기를 연결했습니다. `ree fetch-elsevier --allow-open-copy`는 API 실패 시 DOI를 확인한 공개 저장소 전문을 받아 기존 추출기에 넘깁니다. iScience 논문에서 본문·표 수집을 실제 확인했습니다. API 자체의 403은 별도로 기록합니다. [실행 방법](docs/elsevier_access.md).


희토류가 들어간 철계 합금의 **조성과 부식 시험 조건을 보고 부식전류밀도(i_corr)를 예측**하는 연구입니다.
여기에 Active Learning을 붙여, **어떤 데이터를 먼저 학습하면 적은 데이터로 예측 성능을 높일 수 있는지** 비교합니다.

> 현재 기본 피처는 `corrosion` 후보 28개이며, 학습 fold에서 확보율 50% 이상·두 논문 이상 관찰·비상수 조건으로 선택합니다. [최신 피처 설명](docs/feature_design_v3.md).

## 실제 문헌 100행 파일럿 진행

[현재 수집 현황과 실행 방법](docs/pilot100.md)을 정리했습니다. 충전 후 Sol 추출이 정상 동작했고 19편 처리에서 9편의 실험값 33행을 확보했습니다. 7행은 수치 불일치/조성 부족으로 보류하고, 사람 검토 전 26행으로 임시 모델 비교를 실행했습니다. 선택된 SVR의 논문 단위 홀드아웃 R²는 -1.271로 목표에 미달했습니다. 실제 100행·사람 검증 완료 결과는 아직 없습니다. 일반 철계 합금은 섞지 않고 희토류 첨가 연구와 같은 논문의 대조군만 유지합니다.

| 현재 집계 (2026-10-15) | 결과 |
| --- | --- |
| Sol로 처리한 원문 | 19편 |
| i_corr를 추출한 논문 / 실험값 | 9편 / 33행 |
| 수치 불일치·조성 부족으로 보류 | 7행 |
| 임시 모델 비교에 사용 | 26행, 모두 사람 검토 전 |
| 비교한 모델 | Ridge, SVR, GPR, Random Forest, Extra Trees |
| 내부 교차검증으로 선택한 모델 | SVR |
| 별도 테스트 | 논문 2편의 7행, R² **-1.271** |
| 목표 | 검증한 100행 확보 및 R² 0.8 달성 여부 평가. 현재 미달 |

R²가 음수라는 것은 이 테스트 데이터에서는 테스트 정답의 평균값으로 예측하는 기준보다 오차가 컸다는 뜻입니다. 현재 결과로 좋은 예측 모델을 확보했다고 판단할 수 없습니다. 테스트 점수를 맞추기 위해 유리한 시드나 데이터만 고르지 않습니다.

바로 확인할 자료: [추출값 검토 목록](data/processed/pilot100/review_queue.md), [33행 전체](data/processed/pilot100/llm_pending_all.csv), [보류 7행](data/processed/pilot100/held_for_review.csv), [임시 비교 결과](outputs/pilot26_provisional/model_comparison.json), [결과 그림](outputs/pilot26_provisional/model_comparison.png).

추출 명령 `ree extract`와 논문 단위 내부 검증으로 Ridge/SVR/GPR/Random Forest/Extra Trees를 비교하는 `ree compare-models`를 추가했습니다.

## OpenAI 모델 설정

본문·표에서 조성/시험조건/i_corr를 추출하는 모델은 `gpt-6.1-sol`, 제목·초록의 대량 1차 선별 후보는 `gpt-6-luna`로 설정했습니다.
어운 사례는 Sol로 재검토하거나 사람이 확인합니다. 이 용도 배치는 부식 데이터 추출 벤치마크로 검증된 최적 조합이 아니라 초기 설정입니다.

`.env`에 `OPENAI_API_KEY`, `OPENAI_MODEL=gpt-6.1-sol`, `OPENAI_SCREENING_MODEL=gpt-6-luna`를 설정했습니다. Sol의 실제 유료 호출과 자동 추출을 실행했습니다. Luna는 선별용 설정만 준비되어 있으며, 이번 추출에 사용하지 않았습니다.

먼저 논문 3~5편을 사람이 정리한 정답표와 비교해 수치·단위·시료/조건 연결·누락률을 확인합니다. 모델 간 일치만으로 verified 처리하지 않습니다. 정확도를 확인한 뒤 저비용 모델의 사용 범위를 늘립니다.

참고: [공식 모델 안내](https://developers.openai.com/api/docs/models), [공식 요금](https://developers.openai.com/api/docs/pricing).

## 1. 지금 어디까지 진행했나요?

현재는 **실제 원문에서 값을 추출하고, 검토 대기 데이터로 임시 모델 비교까지 실행한 단계**입니다. 가상 데이터 실행 결과와 실제 문헌 기반 임시 분석을 구분합니다.

| 작업 | 현재 상태 |
| --- | --- |
| Elsevier·Springer·Wiley·OpenAI 키 저장 | 완료. `.env`에 저장하고 Git에서 제외 |
| API로 논문 검색 | 초기 검색 150건 → 중복 제거 후보 141편. 공개 원문 저장소도 추가 검색 |
| 연구에 맞는 논문 선별 및 원문·표 확보 | 일부 완료. XML·HTML·PDF를 확보해 19편 추출 처리 |
| 논문 데이터를 기록할 CSV 양식 | 작성 완료 |
| LLM 데이터 추출 | Sol 연결 및 실행 완료. 추출값과 원문 근거 저장 |
| 확보율 기반 피처 전처리 및 입력 검증 | 구현 완료 |
| 모델 학습·비교 | 5종을 논문 단위 내부 교차검증으로 비교하고 선택 모델의 별도 테스트 수행 |
| Active Learning과 무작위 선택 비교 | 구현 및 가상 데이터 실행 완료. 실제 검증 데이터로는 아직 미실행 |
| 전체 흐름 실행 확인 | 가상 데이터 120행으로 완료 |
| 사람 검증을 끝낸 100행 연구 결과 | 아직 없음. 26행 임시 결과만 있음 |

검색 결과가 있다고 바로 학습할 수 있는 것은 아닙니다. 논문 안의 조성, 시험 조건, 실제 i_corr를 확인하고 표로 정리해야 합니다.

## 2. 전체 연구는 이렇게 진행합니다

```text
API로 후보 논문 검색
        ↓
연구에 맞는 논문 선별 + 원문/표 확보
        ↓
LLM 또는 사람이 실험값 추출
        ↓
사람이 원문·단위·중복 여부 확인
        ↓
조성·환경 피처와 i_corr 데이터셋 구성
        ↓
Ridge / SVR / GPR 학습
        ↓
Active Learning vs 무작위 선택 비교
```

API는 논문을 찾고 접근 가능한 원문을 받는 역할이고, LLM은 논문 속 수치를 정리하는 역할입니다. 현재 검색과 Sol 추출을 연결했습니다. 사람의 원문 검토가 끝나기 전 시험 분석을 할 때는 별도의 임시 분석 옵션을 사용하고, 검증 완료 데이터로 표시하지 않습니다.

## 3. 모델에 넣는 데이터는 무엇인가요?

**CSV 한 행은 특정 합금이 특정 시험 조건에서 측정된 실험 데이터 한 개**입니다.
같은 논문이라도 합금이나 시험 조건이 다르면 여러 행이 될 수 있습니다.

| 분류 | 개수 | 입력값 |
| --- | ---: | --- |
| 기본 합금 조성 | 9 | C, Si, Mn, P, S, Cr, Ni, Mo, Cu |
| 희토류 | 2 | 희토류 함량의 로그값, 희토류 원소 종류 |
| 부식 시험 환경 | 3 | 온도, pH, 용액·농도를 함께 기록한 전해질 조건 |
| 합계 | **최대 14** | 확보율 기준 적용 전 후보 변수 수 |

분극 속도·OCP 안정화 시간·노출 시간·가스 조건·모재 상 분류·Cl 농도·고Cr 여부는 확장 후보로 보존합니다. `--profile extended`로 사용할 수 있습니다.

현재 정답이 공개된 학습 데이터에서 확보율이 기본 80% 이상인 열만 선택합니다. 전부 결측인 열은 제외하며, 남은 결측은 학습 데이터 기준으로 보간합니다. 이 선택에 테스트 데이터는 사용하지 않습니다. 임시 비교의 최종 학습에서 선택된 열은 C, Si, Mn, RE_log1p_ppm, RE_element_cat, electrolyte_condition_cat입니다. 데이터가 추가되면 선택 열도 바뀔 수 있으며 최적 조합이 검증된 것은 아닙니다.

예측하는 정답은 `log10(i_corr [A/cm²])`입니다. 크기 차이가 큰 전류밀도를 로그값으로 바꿔 학습합니다.

데이터를 모을 때는 아래 기준을 사용합니다.

- 합금 조성은 **wt.%**, 희토류 총함량은 **질량 ppm**으로 기록합니다.
- 희토류 로그값은 `ln(1 + RE_ppm)`으로 코드가 계산합니다.
- 고Cr 여부는 우선 `Cr ≥ 10.5 wt.%`로 정했습니다. 연구 기준 확정 시 조정할 수 있습니다.
- 시험 조건의 단위는 열 이름에 고정했습니다. 예: `chloride_mol_L`, `temperature_C`, `scan_rate_mV_s`.
- 논문에 없는 값은 추측해서 채우지 않습니다. 특히 정답인 i_corr가 없는 행은 학습하지 않습니다.
- 논문 ID, 표/페이지 위치, 근거 문장을 함께 남깁니다. 사람이 확인한 행에만 `review_status=verified`를 표시합니다.
- pH와 전해질 조건은 기본 후보에 포함합니다. 열처리, 표면 처리 등도 추가 열로 보관하여 문헌 간 차이를 검토합니다.

자세한 추출 규칙은 [문헌 데이터 추출 지침](docs/extraction_prompt.md)에 있습니다.

## 4. Active Learning은 어떻게 동작하나요?

우선 **이미 모아 둔 문헌 데이터 중에서 다음에 학습할 실험 데이터를 고르는 방식(A)**을 구현했습니다.

예를 들어 정답이 있는 데이터 500개를 확보했다면 다음처럼 진행합니다.

1. 일부 논문은 최종 성능 평가용으로 따로 둡니다.
2. 나머지 데이터 중 일부만 정답을 공개해 처음 학습합니다.
3. 남은 후보의 조성과 시험 조건을 보고 모델이 가장 확신하지 못하는 데이터를 고릅니다.
4. 선택된 데이터의 정답을 공개하고 다시 학습합니다.
5. 같은 수의 데이터를 무작위로 골랐을 때와 성능을 비교합니다.

즉, 이미 있는 정답을 잠시 가린 뒤 순서대로 공개하는 **과거 데이터 기반 시뮬레이션**입니다. 아직 읽지 않은 논문을 추천하거나 새로운 합금을 실험하는 기능은 포함하지 않았습니다.

| 모델 | 역할 | 확신하지 못하는 정도를 구하는 방법 |
| --- | --- | --- |
| Ridge | 기본 비교 모델 | 데이터를 복원추출해 여러 모델을 만들고 예측값 차이 확인 |
| SVR | 비선형 예측 모델 | Ridge와 같은 방식으로 여러 모델의 예측값 차이 확인 |
| GPR | 예측과 불확실성을 함께 제공 | 모델이 계산한 예측 표준편차 사용 |

Active Learning이 반드시 더 좋은 결과를 내는 것은 아닙니다. 무작위 선택과 비교해서 실제로 이득이 있는지 확인하는 것이 연구의 한 부분입니다.

## 5. 성능을 공정하게 비교하기 위한 설정

- **논문 단위로 분리:** 같은 논문의 데이터가 학습과 테스트에 동시에 들어가지 않게 합니다. 논문 ID 기준 약 20%를 테스트로 분리합니다.
- **테스트 정답 격리:** 테스트 정답은 성능 계산에만 쓰고, 다음 학습 데이터 선택에는 쓰지 않습니다.
- **현재 학습 데이터만으로 전처리:** 결측값 보간, 표준화, 범주형 변환은 매 반복에서 현재 정답이 공개된 데이터에만 맞춥니다.
- **같은 출발점:** 같은 시드에서는 모든 모델과 선택 전략이 같은 테스트 논문, 같은 초기 데이터로 시작합니다.
- **여러 번 반복:** 데이터 분리와 초기 선택을 바꿔 실행하고 평균과 표준편차를 저장합니다.

성능 지표는 MAE, RMSE, R²입니다. MAE와 RMSE는 작을수록 좋고, R²는 클수록 좋습니다. 오차는 로그 타깃 기준입니다.

`ree compare-models`는 학습 논문 내부의 GroupKFold로 모델과 하이퍼파라미터를 고릅니다. 피처 선택과 보간도 각 학습 fold 안에서 수행합니다. 선택된 모델 한 개만 별도 테스트 논문에서 평가합니다. 26행 임시 분석은 seed 42로 한 번 분리해 실행했습니다.

`ree benchmark`의 Active Learning 비교는 초기 고정 모델 설정과 여러 시드를 사용합니다. 비용 단위는 ‘실험 데이터 한 행’이며, 논문 한 편을 읽는 비용까지 평가하는 방식은 별도 설계가 필요합니다. 이미 결과를 확인한 테스트 논문은 향후 최종 검증에서 새 테스트 논문으로 교체해야 합니다.

## 6. 직접 실행해 보기

모든 명령은 프로젝트 폴더의 PowerShell에서 실행합니다.

### ① 실행 환경 설치

```powershell
uv sync --python 3.12
```

`uv.lock`에 기록된 버전으로 Python 패키지를 설치합니다.

### ② 가상 데이터로 전체 흐름 확인

```powershell
uv run ree demo
uv run ree validate data/processed/synthetic_demo.csv
uv run ree benchmark data/processed/synthetic_demo.csv --output outputs/demo
```

가상 논문 15개 × 실험값 8개로 만든 총 120행을 사용합니다. 기본 설정은 처음 20행으로 학습하고, 5행씩 추가해 최대 50행까지 학습하는 것입니다. 이를 3개의 시드로 반복합니다.

**이 결과는 프로그램 작동 확인용이며 실제 문헌 연구 결과가 아닙니다.**

### ③ 현재 확보한 실제 데이터로 임시 비교 재현

```powershell
uv run ree compare-models data/processed/pilot100/provisional_for_model.csv --rows 26 --allow-provisional --seed 42 --output outputs/pilot26_provisional
```

`--allow-provisional`은 사람이 검토하기 전인 pending 데이터를 시험 분석에 사용하는 옵션입니다. 원본의 검토 상태는 그대로 유지하고 결과에도 임시 분석임을 표시합니다. 기본 명령은 검증 완료 자료만 받습니다. 이 명령은 100행 연구 결과를 만드는 명령이 아닙니다.

### ④ 새 원문에서 실험값 추출

확보한 XML 근거 블록은 바로 추출할 수 있습니다.

```powershell
uv run ree extract --source-dir data/raw/europepmc/PMC11720852 --output-dir data/processed/extractions/PMC11720852 --reuse-response
```

위 예시는 저장된 응답을 재검증하므로 추가 API 요청을 하지 않습니다. 새 원문을 추출할 때는 `--reuse-response`를 빼면 Sol 유료 요청이 발생합니다. 원문 파일과 blocks.json, metadata.json이 있는 폴더를 입력으로 사용합니다.

새 PDF는 먼저 입력 폴더를 준비합니다. DOI와 제목은 실제 논문 정보로 바꿉니다.

```powershell
uv run ree prepare-pdf paper.pdf --doi 10.1155/2018/4071352 --title 'Paper title' --output-dir data/raw/my_paper
uv run ree extract --source-dir data/raw/my_paper --output-dir data/processed/extractions/my_paper
```

추출 결과는 pending으로 저장됩니다. 같은 평균값을 반복 측정 수만큼 복제하지 않으며, 표·본문 중복도 별도 실험으로 세지 않습니다.

### ⑤ 검증한 실제 문헌 데이터 100행으로 실행

먼저 빈 입력 양식을 만듭니다. 기존 양식 파일이 있으면 덮어쓰므로 작성 중인 데이터는 별도 파일에 보관하세요.

```powershell
uv run ree template
```

생성된 `data/measurements_template.csv`에 맞춰 원문 데이터를 정리하고, 검증한 데이터를 `data/processed/measurements.csv`로 저장합니다. 그다음 실행합니다.

```powershell
uv run ree validate data/processed/measurements.csv
uv run ree compare-models data/processed/measurements.csv --rows 100 --seed 42 --output outputs/pilot100
uv run ree benchmark data/processed/measurements.csv --output outputs/research --seeds 11 22 33 44 55 --initial 20 --batch 5 --budget 100
```

| 옵션 | 의미 |
| --- | --- |
| `--initial 20` | 처음 정답을 공개할 데이터 20행 |
| `--batch 5` | 반복할 때마다 추가할 데이터 5행 |
| `--budget 100` | 학습 데이터 최대 100행. 후보가 부족하면 먼저 종료 |
| `--seeds 11 22 33 44 55` | 분리와 초기 선택을 바꿔 5번 반복 |

테스트 논문을 제외한 뒤에도 초기 학습량보다 많은 데이터가 있어야 합니다. 코드의 최소 5개 논문 조건은 실행을 위한 최소 조건이며, 연구에 충분한 데이터 규모라는 의미는 아닙니다.

`compare-models`는 검증한 100행과 최소 8개 독립 논문을 요구합니다. 현재 확보한 파일을 100행으로 늘려 주는 기능은 없습니다. `--rows 100`은 전체 비교 입력 행 수이고, 아래 `--budget 100`은 AL 학습에 공개할 최대 라벨 수이므로 서로 다릅니다.

### ⑥ 결과 확인

결과는 `--output`으로 지정한 폴더에 저장합니다.

| 파일 | 확인할 내용 |
| --- | --- |
| `model_comparison.json` | 모델별 내부 CV, 선택 모델과 별도 테스트 R²·MAE·RMSE |
| `holdout_predictions.csv` | 별도 테스트 논문의 실제 로그값과 예측 로그값 |
| `learning_curves.png` | 데이터를 늘릴 때 예측 오차가 어떻게 달라지는지 |
| `learning_curves.csv` | 각 반복의 MAE, RMSE, R² |
| `summary.csv` | 여러 시드의 평균과 표준편차 |
| `missingness.csv` | 각 입력 변수의 결측 비율 |
| `run.json` | 실행 설정, 테스트 논문, 선택된 데이터 이력, 입력 파일 해시와 패키지 버전 |

## 7. API 키와 논문 검색

현재 키는 로컬 `.env`에 다음 변수명으로 저장되어 있습니다. 실제 키 값은 README에 기록하지 않습니다.

```dotenv
ELSEVIER_API_KEY=실제_키
SPRINGER_OPEN_ACCESS_API_KEY=실제_키
SPRINGER_META_API_KEY=실제_키
WILEY_TDM_TOKEN=실제_토큰
OPENAI_API_KEY=실제_키
OPENAI_MODEL=gpt-6.1-sol
OPENAI_SCREENING_MODEL=gpt-6-luna
```

`.env`는 Git에서 제외합니다. 새 환경에서는 `.env.example`을 `.env`로 복사하고 실제 값을 넣습니다.
Python 검색 명령은 `.env`를 자동으로 읽으므로 별도의 로딩 명령이 필요 없습니다.

아래 명령으로 후보 논문을 검색할 수 있습니다.

```powershell
uv run ree search --provider elsevier --query 'TITLE-ABS-KEY((cerium OR lanthanum) AND corrosion AND steel)' --limit 5 --output data/raw/elsevier_search.json
uv run ree search --provider springer-meta --query 'cerium corrosion steel' --limit 5 --output data/raw/springer_meta_search.json
uv run ree search --provider springer-oa --query 'cerium corrosion steel' --limit 5 --output data/raw/springer_oa_search.json
```

각 명령은 한 페이지만 요청하고 최대 5건을 저장합니다. 전체 논문을 자동으로 수집하는 명령은 아닙니다. 검색어가 넓으면 관련 없는 논문도 포함되므로 선별이 필요합니다.

Elsevier는 Scopus 검색을 사용합니다. Springer Meta는 메타데이터 검색, OA는 공개 접근 콘텐츠 검색에 사용합니다. **검색 성공과 논문 원문 전체에 대한 접근은 별개**이며, 제공 범위와 기관 권한에 따라 달라집니다.

다른 PowerShell 작업에서도 키를 쓰고 싶다면 아래 스크립트로 설정된 키와 모델명을 현재 세션에 불러올 수 있습니다. 파일명은 기존 이름을 유지했습니다.

```powershell
. .\scripts\Set-ElsevierEnv.ps1
```

## 8. 주요 파일과 앞으로 할 일

| 경로 | 역할 |
| --- | --- |
| `ree_research/mining.py` | API 검색과 응답 저장 |
| `ree_research/schema.py` | 데이터 검증, 기본 14개 후보 및 확장 후보와 타깃 정의 |
| `ree_research/ingestion.py` | PDF를 페이지별 추출 근거로 준비 |
| `ree_research/extraction.py` | Sol 추출, 근거 대조, 단위 변환, pending 저장 |
| `ree_research/model_selection.py` | 논문 단위 내부 CV로 5종 모델·하이퍼파라미터 비교 |
| `ree_research/benchmark.py` | 모델 학습, Active Learning, 성능 비교 |
| `ree_research/cli.py` | 터미널 실행 명령 |
| `docs/extraction_prompt.md` | 문헌에서 값을 추출할 때 지킬 규칙 |
| `tests/test_protocol.py` | 데이터 검증과 평가 방식에 대한 자동 테스트 |
| `scripts/assemble_extraction_pilot.py` | 추출 파일 통합과 보류 사유 분리 |
| `docs/pilot100.md` | 수집·추출·임시 분석의 상세 진행 기록 |

테스트 13개가 통과했습니다. 검토 상태 차단, pool 정답 미사용, 논문 분리, 확보율 선택, 근거 인용, 원문 응답 구분, API 잔액 부족 시 허위 데이터 생성 방지 등을 확인했습니다.

```powershell
uv run python -m unittest discover -s tests -v
```

다음 작업은 아래 순서입니다.

1. 현재 33행의 수치·단위·시료·조건을 원문에서 사람이 확인하고 보류 사유를 해결합니다.
2. 희토류 첨가 연구와 같은 논문의 대조군 범위에서 추가 원문을 확보합니다. 추출 100행까지 최소 67행이 더 필요합니다.
3. 노출 시간·녹층·열처리 등 조건 차이와 결측 정보가 예측을 제한하는지 검토합니다.
4. 검증한 100행이 모이면 학습 논문 내부에서 모델을 선택하고, 새 최종 테스트 논문으로 평가합니다.
5. 실제 검증 데이터에서 Active Learning과 무작위 선택을 비교합니다.

실제 데이터, API 응답, 실행 결과, API 키는 Git에서 제외하고 코드와 빈 양식만 공유합니다.

API 참고 문서: [Elsevier Scopus Search](https://dev.elsevier.com/documentation/SCOPUSSearchAPI.wadl), [Springer Quick Start](https://dev.springernature.com/docs/quick-start/making-first-api-call/), [Springer API 서비스](https://dev.springernature.com/docs/introduction/overview-services/).

## 9. 실제 문헌 수집 진행 상황 — 2026-10-15

연결 확인 다음 단계로, 실제 후보 논문을 추가 검색했습니다.

- 검색 6회 × 최대 25건으로 **150건**의 레코드를 받았습니다.
- DOI와 제목을 확인해 중복 9건을 합쳤고 **141편의 후보 목록**을 만들었습니다.
- 최신 검색뿐 아니라 2020년 이전, 2020~2025년 검색을 추가했습니다. 전체 문헌을 빠짐없이 모은 체계적 검색은 아직 아닙니다.
- 철계 합금, 희토류, 부식, 전기화학 시험 관련 키워드로 검토 순서를 매겼습니다. 코팅/억제제 연구는 별도 표시했습니다.
- 이 점수는 검토를 돕는 기준입니다. **141편 모두 원문 검토 대기 상태이며, 학습 데이터 141행이 생겼다는 뜻은 아닙니다.**

후보 목록은 로컬의 [읽기 쉬운 목록](data/processed/literature/candidates.md)과 [근거를 포함한 JSON](data/processed/literature/candidates.json)에 저장했습니다. JSON에는 검색 제공자, 검색어, 원본 응답 경로를 남겼습니다.

새 검색 결과를 저장한 뒤 아래 명령으로 후보 목록을 다시 만들 수 있습니다. 기존 생성 목록은 덮어쓰므로 수동 검토 기록은 별도 파일에 보관하세요.

```powershell
uv run ree screen --input-dir data/raw/discovery
```

**원문 접근도 별도로 확인했습니다.** Elsevier 공식 Article Retrieval API로 Ni–Ce 첨가 내후성 강 연구 한 편(`10.1016/j.jmrt.2025.11.079`)을 요청했지만 HTTP 403이 반환됐습니다. 검색 키가 동작하더라도 이 요청에서는 원문을 확보하지 못했습니다. 정확한 제한 원인은 응답 코드만으로 단정할 수 없습니다.

다른 논문을 공식 API로 확인하려면 다음 명령을 사용합니다.

```powershell
uv run ree fetch-elsevier --doi 10.1016/j.jmrt.2025.11.079 --output-dir data/raw/fulltext/ni_ce_2025
```

접근 가능한 경우 XML을 저장하고, 원문 텍스트가 있는지 별도로 기록합니다. 메타데이터만 받으면 원문 확보로 처리하지 않습니다. 이 Elsevier 요청은 실패했지만, 다른 공개 원문과 Wiley TDM을 통해 현재 33행을 추출했습니다.

추가 후보에서도 원문 접근 가능 여부를 확인하고 조성표·분극시험 표를 수집합니다. [공식 원문 API 문서](https://dev.elsevier.com/documentation/ArticleRetrievalAPI.wadl).
