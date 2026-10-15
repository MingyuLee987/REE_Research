# Springer Nature·Wiley 실험 데이터 수집

사용자가 확인한 목표는 **기존 수집 자료를 포함해 두 출판사 논문에서 실험 데이터 포인트 총 100개 이상 확보**입니다. 새로운 100개를 별도로 추가하는 목표와 구분합니다.

2026-10-15 현재 **8편·107개 데이터 포인트**를 별도 데이터셋으로 저장했습니다. 이번 작업에서 새로 추가한 값은 5편의 **39개**입니다. 합성 데이터, 기존 논문의 재다운로드, 표·그림에서 반복된 같은 결과는 추가 실험으로 세지 않았습니다.

| 출판사 | 수집 데이터 포인트 |
| --- | ---: |
| Springer Nature (Nature 저널과 Springer 저널 포함) | 97 |
| Wiley | 14 |
| 합계 | **111** |

**107개 중 임시 분석 후보는 77개, 검토 보류는 30개**입니다. 수집 개수 목표를 충족했지만 분석 가능한 100개나 사람이 검증한 100개를 확보했다는 뜻은 아닙니다. 모든 값의 최종 검토 상태는 `pending`이며 사람 검증 완료는 0개입니다.

## 바로 확인할 파일

- [두 출판사 전체 107개](../data/processed/nature_wiley/measurements_pending.csv)
- [두 출판사 임시 후보 77개](../data/processed/nature_wiley/provisional_for_model.csv)
- [보류 데이터 30개](../data/processed/nature_wiley/held_for_review.csv)
- [논문별 집계·출판사·검토 상태](../data/processed/nature_wiley/summary.json)

지금 IDE에서 열려 있는 `synthetic_demo_v2.csv`는 합성 예제입니다. 실제 문헌 데이터를 확인하려면 위 `measurements_pending.csv`를 여세요. 전체 출판사 수집본에는 현재 18편·151개가 있으며 두 출판사만 따로 내보냈습니다.

## 새로 추가한 연구

| 논문 | 새 데이터 포인트 | 추출 근거 | 상태 |
| --- | ---: | --- | --- |
| [Wiley: 희토류 첨가 탄소강·내후강](https://doi.org/10.1002/maco.201911150) | 4 | Table 2, 0.1 mol/L Na2SO4 | i_corr 명시. 조성은 범위·상한 또는 미보고이므로 4개 모두 보류 |
| [Wiley: 저합금강 토양 모사 용액](https://doi.org/10.1002/maco.202213672) | 5 | Table 5, ×10^-6 A/cm² | 임시 후보. RE 투입량과 실제 조성을 구분 |
| [Springer: La 첨가 스테인리스강 용접부](https://doi.org/10.1007/s10853-025-11514-0) | 10 | 0일 Figure 9a 및 12일 Figure 9b/Table 4 | 용접부 실제 조성 미보고와 원문 수치 차이로 10개 모두 보류 |
| [Springer: Ce 함유 S31254 열처리](https://doi.org/10.1007/s11663-025-03817-z) | 18 | Table IV, ×10^-7 A/cm² | 표제의 S4와 행·본문의 S2가 달라 S2 13개 보류. S0 5개 임시 후보 |
| [Springer: Ce–La 첨가 Q355B](https://doi.org/10.1007/s11663-026-04267-x) | 2 | 본문의 명시적 i_corr 및 Figure 10 | 임시 후보. 실제 잔류 Ce+La 65 ppm 사용 |

Wiley는 제공된 토큰으로 공식 TDM API에서 PDF를 받았습니다. Springer는 공식 `link.springer.com/content/pdf/...pdf` 주소에서 원문을 받았습니다. La 용접부 논문은 OA JATS API에서 조회되지 않았지만 공식 PDF 요청은 HTTP 200으로 성공했습니다. Elsevier 원문 API는 사용하지 않았습니다.

나머지 기존 68개는 Springer Nature의 La 합금 해수 연구 60개와 Ce 첨가 철근 연구 3개, Wiley의 희토류 용접금속 연구 5개입니다. 같은 DOI를 다시 받은 것은 새 데이터로 추가하지 않았습니다.

## 수치 확인과 중복 처리

- Sol이 본문·표를 추출하고 인용 근거를 검사했습니다. 직접 전사한 값은 방법을 별도로 기록했고 사람 검증 완료로 표시하지 않았습니다.
- S31254 Table IV에는 20개 항목이 있지만 같은 S2 무처리 대조값이 세 온도군에 반복됩니다. 이를 한 번만 세어 18개 조건을 남겼습니다. 열처리 온도와 부식 측정 온도 25 °C를 구분했습니다.
- S31254의 그래프에는 더 많은 시료 곡선이 있지만 수치가 인쇄되지 않은 좌표를 추정해 추가하지 않았습니다. 표에는 S2라고 쓰였는데 표제는 S4라고 하므로 해당 13개는 임시 모델에서 제외했습니다.
- La 용접부의 12일 Table 4와 Figure 9b는 같은 조건을 중복 수집하지 않았습니다. 0 La는 표 3.644와 그림 3.664 µA/cm², 0.5 La는 본문 1.005와 표·그림 1.055 µA/cm²가 다릅니다. 표 값을 보존하되 전체 용접부 데이터는 보류했습니다.
- Wiley의 탄소강 논문은 조성 범위나 상한값을 중앙값·정확한 값으로 바꾸지 않았습니다. 보고되지 않은 조성은 결측입니다.

## 포함하지 않은 원문

공식 원문을 확보해도 타깃이 명시되지 않으면 데이터 포인트가 늘지 않습니다. 다음은 이번에 확인한 주요 제외 자료입니다.

| DOI | 제외 이유 |
| --- | --- |
| 10.1002/srin.202300041 | 범위 내 수치 i_corr를 추출하지 못함 |
| 10.1002/srin.201300438 | 피팅된 수치 i_corr 대신 국부부식·분극 거동 중심 |
| 10.1002/maco.202213104 | 중량 감소·부식속도를 i_corr로 대체하지 않음 |
| 10.1002/maco.201508380 | 범위 내 명시적 수치 i_corr를 추출하지 못함 |
| 10.1002/mawe.201900045 | 범위 내 명시적 수치 i_corr를 추출하지 못함 |
| 10.1007/s11663-025-03792-5 | 국부부식·부식층 연구, 명시적 수치 i_corr 미확보 |
| 10.1007/s11665-019-04112-0 | 분극곡선은 있지만 명시적 수치 타깃 미확보 |
| 10.1007/s11665-015-1651-6 | 범위 내 명시적 수치 i_corr를 추출하지 못함 |
| 10.1007/978-3-030-05861-6_53 | 명시적 수치 i_corr 미확보 |
| 10.1023/B:MASC.0000023502.72468.31 | 명시적 수치 i_corr 미확보 |

추출 0개는 논문에 어떤 형태로도 값이 없다는 확정 판정이 아니라, 이번 원문 검토·추출에서 채택할 수치를 확보하지 못했다는 뜻입니다. 합금에 희토류를 첨가하지 않고 용액 억제제나 코팅에만 넣은 논문도 제외했습니다.

## 재현

```powershell
uv run --no-sync python scripts/collect_publisher_round2.py
uv run --no-sync python scripts/extract_publisher_round2.py
uv run --no-sync python scripts/build_s31254_table_rows.py
uv run --no-sync python scripts/curate_publisher_round2.py
uv run --no-sync python scripts/assemble_extraction_pilot.py
uv run --no-sync python scripts/assemble_context_pilot.py
uv run --no-sync python scripts/build_nature_wiley_dataset.py
```

기존 60개를 다시 독립 논문으로 취급하지 않습니다. 데이터가 한 논문에 집중돼 있어 모델 평가는 논문 단위로 분리해야 합니다. 이번 작업은 수집·검토 분류까지이며 모델 재학습이나 새 R² 계산은 하지 않았습니다.
