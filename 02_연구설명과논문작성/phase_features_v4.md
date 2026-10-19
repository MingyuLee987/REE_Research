# 상·조성 피처 보강 (2026-10-16)

전체 31편의 실험 보고값 219개를 보존했다. 정규화된 i_corr가 있는 기록은 204개이며, 단위 배율이 불명확한 15개는 타깃을 비워 두었다. 임시 분석 후보는 142개/21편, 보류는 77개, 사람의 검증 완료는 0개다.

## 원문 재독

확보한 전문 텍스트 블록 25편을 **gpt-6.1-sol**로 재독했다. Elsevier 4편은 전문 블록 미확보, 중국어 PDF 2편은 텍스트 손상으로 이번 재독에서 제외했다. 31편 전체의 전문을 재독한 결과가 아니다.

원문 인용문과 위치가 매칭되는 필드만 보충했다. 저자의 재료 계열 설명과 시험 전 조직 관찰 근거는 `phase_evidence_type`으로 구분했다. 타깃·원래 보고값·보류 사유·검토 상태를 유지했다. 상·조성·근거 필드 445개를 보충했고 전체 219개 중 142개, 임시 후보 142개 중 **114개(80.3%)**에 모재 상 정보를 확보했다. LLM 근거 일치 검사는 사람의 검증을 대체하지 않는다.

## 피처 정의

| 종류 | 내용 |
| --- | --- |
| 원문 상 2개 | `matrix_phase_reported`, `secondary_metallic_phases_reported` |
| 보고 분율 5개 | 오스테나이트·페라이트·마르텐사이트·베이나이트·펄라이트(%) |
| 범주 2개 | `matrix_phase_group`, `secondary_phase_group` |
| 조성 기술자 6개 | Schaeffler Cr/Ni 당량과 차이, WRC-1992 Cr/Ni 당량, C+N |
| 상×조성 5개 | 오스테나이트×Ni/Cr, 페라이트×Cr, 마르텐사이트×C, 혼합 조직×log1p(RE ppm) |

조성은 wt.% 기준이다.

- Schaeffler: Cr_eq = Cr + Mo + 1.5Si + 0.5Nb; Ni_eq = Ni + 30C + 0.5Mn.
- WRC-1992: Cr_eq = Cr + Mo + 0.7Nb; Ni_eq = Ni + 35C + 20N + 0.25Cu.
- Schaeffler balance = Cr_eq − Ni_eq; C_N_sum = C + N.

당량은 스테인리스 용접 조직 도표에서 유래한 **조성 기술자**다. 벌크 철계 합금 전체의 실제 상·상분율 예측값으로 해석하지 않는다. [Outokumpu 기술자료](https://www.outokumpu.com/-/media/from-sharepoint/documents/product/outokumpu-steel-grades-properties-global-standards.pdf)와 [Welding Journal의 WRC-1992 식](https://s3.amazonaws.com/WJ-www.aws.org/supplement/WJ_2012_04_s113.pdf)을 참고했다.

미보고 Nb·N 등을 0으로 간주하지 않으며 필요한 성분이 없으면 당량도 결측으로 유지한다. ‘단일상’을 임의의 100% 분율로 바꾸지 않았다. 분율은 저자가 정의한 미세조직 구성요소 기준이며 완전한 상분율 합계로 간주하지 않는다. 부식 후 녹층·산화물과 전기화학적 결과값은 입력에서 제외했다.

전체 지원 스키마는 75개 피처다. 새 `phase_corrosion` 프로파일은 수치형 40개·범주형 6개, **46개 후보**다. 임시 후보 전체에서 확보율 50% 이상·2편 이상·비상수 조건을 만족하는 피처는 25개다. 실제 학습에서는 폴드 내부에서 다시 선택한다. 상분율·완전한 당량은 확보율이 낮아 현재 선택되지 않는다. 현재 개선을 당량 자체의 효과로 주장하면 안 된다.

## 개발 성능 비교

기존 테스트 논문 2편/7개를 제외한 135개/19편에서 4-fold 그룹 교차검증을 수행했다. 관련 La 합금 논문은 같은 그룹으로 묶어 총 18개 그룹을 사용했다. 모든 비교는 같은 관측값·분할·고정 모델 설정을 사용했다. 피처 선택·대치·스케일링은 학습 폴드 내부에서 수행하고 논문별 MAE 평균으로 모델을 선택했다.

| 동일 SVR 비교 | pooled OOF R² | pooled MAE | 논문별 MAE 평균 |
| --- | ---: | ---: | ---: |
| 재독 전 | 0.110 | 0.819 | 0.939 |
| 조성 보충 | 0.184 | 0.787 | 0.884 |
| 상·조성 보강 | 0.246 | 0.735 | 0.861 |

타깃과 MAE는 log10(i_corr [A/cm²]) 기준이다. 이는 미검증 데이터의 **개발 교차검증**이며 피처·모델 선정에도 사용했으므로 최종 독립 테스트 성능으로 보고하지 않는다. R² 0.8에는 도달하지 않았다. 모든 모델이 개선되지는 않았고 새 피처에서 Ridge는 크게 불안정했다. 알려지지 않은 논문 간 시료 중복도 추가 확인해야 한다. 전체 결과는 `03_분석결과와실험계획/90_이전분석기록/06_금속조직_변수분석/comparison.csv`에 있다.

## 파일과 재현

- 갱신된 통합본: `01_논문원문과데이터/processed/pilot100/llm_pending_all.csv` (219개)
- 인용문 줄바꿈을 정리한 통합본: `01_논문원문과데이터/processed/phase_v4/measurements_clean.csv`
- 임시 모델 입력: `01_논문원문과데이터/processed/phase_v4/model_input_pending.csv` (142개)
- 피처·근거 통합본: `01_논문원문과데이터/processed/phase_v4/features_pending.csv`
- 피처 확보율: `01_논문원문과데이터/processed/phase_v4/feature_coverage.csv`
- 재독 전 백업: `01_논문원문과데이터/processed/phase_v4/baseline_all.csv`, `baseline_context.csv`
- 필드별 근거: `01_논문원문과데이터/processed/phase_v4/applied_field_evidence.json`

```powershell
.\.venv\Scripts\python.exe 04_분석실행코드/assemble_phase_dataset.py --publish
.\.venv\Scripts\python.exe 04_분석실행코드/evaluate_phase_features.py
.\.venv\Scripts\ree.exe template --profile phase_corrosion --output 01_논문원문과데이터/measurements_template.csv
```

재조립은 저장된 재독 결과를 사용한다. API 재독은 `04_분석실행코드/reread_phase_context.py`이며 새 요청에는 비용이 발생한다. 일반 CLI 기본 프로파일은 기존 `corrosion`이므로 새 피처 사용 시 `--profile phase_corrosion`을 명시한다. 전용 비교 스크립트에는 관련 합금 계열 그룹 묶음도 적용되어 있다.
