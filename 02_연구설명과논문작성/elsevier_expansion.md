# Elsevier 포함 추가 수집

2026-10-15 수집분입니다. 범위는 **희토류를 합금 내부에 첨가한 철계 합금과 해당 논문의 대조군**입니다. 이번에는 Elsevier 12개, Springer 4개를 추가했습니다. 기존 151개에서 **22편·167개 실험 데이터 포인트**가 됐습니다. 임시 분석 후보는 117개, 보류는 50개이며 사람 검증 완료는 0개입니다.

## 실제 데이터 파일

- [전체 수집본 167개](../01_논문원문과데이터/processed/pilot100/llm_pending_all.csv)
- [임시 분석 후보 117개](../01_논문원문과데이터/processed/context_v2/provisional_enriched.csv)
- [검토 보류 50개](../01_논문원문과데이터/processed/pilot100/held_for_review.csv)
- [Springer Nature·Wiley 부분집합 111개](../01_논문원문과데이터/processed/nature_wiley/measurements_pending.csv)

합성 예제 `synthetic_demo.csv`, `synthetic_demo_v2.csv`는 파일 정리 과정에서 제거했습니다. 실제 문헌 수집값은 위 파일에 저장했습니다.

## 추가한 논문과 수치

| 논문 | 추가 데이터 포인트 | 수치 근거 | 보류 사유 |
| --- | ---: | --- | --- |
| [GCr15 베어링강의 La·Ce 및 열처리](https://doi.org/10.1016/j.corcom.2022.06.004) | 6 | Table 4. 열간압연, 소둔, 담금질·뜨임별 대조강/RE강 | 출판사 검색 결과에서 표 확보. 원문 전체 대조 필요 |
| [La·Ce 첨가 저합금강](https://doi.org/10.1016/j.jmrt.2025.01.207) | 3 | Table 3: 2.98, 3.377, 3.603 μA/cm² | 본문 NaCl 0.5%와 그림 설명 3.5%가 다름. 최소 i_corr 시료에 대한 서술도 표와 다름 |
| [Y 첨가 해양용 강](https://doi.org/10.1016/j.jmrt.2023.12.189) | 3 | Table 4: 열처리 유지 1/3/5 h에 9.73/8.87/6.95 ×10⁻⁶ A/cm² | 주요 조성은 범위·상한으로만 보고. 전체 원문 및 시험 조건 대조 필요 |
| [La·Ce 처리 304 스테인리스강](https://doi.org/10.1007/s42243-025-01553-x) | 4 | 원문 PDF 10쪽 Table 4: CC-1~4, 7.253/6.593/5.439/3.412 μA/cm² | 부식 시험은 연속주조 빌릿(CC), 주요 조성표는 LF 단계. 최종 빌릿 조성으로 동일시하기 전 확인 필요 |

GCr15 Table 1의 열 순서는 C, Si, Mn, Cr, **S, P**, RE, Fe입니다. P와 S를 바꾸지 않았습니다. 미보고 조성, 범위의 중간값, 미정량 실온은 임의로 채우지 않았습니다. La·Ce 저합금강의 NaCl 농도도 결측으로 남겼습니다.

Y강 Table 6의 추가 수치 6개는 pH·주사 속도·온도별 결과이나 다른 조건과 반복 기준값의 대응을 확정하지 못해 전체 167개에 넣지 않았습니다. [미병합 후보 목록](../01_논문원문과데이터/raw/elsevier_expansion/unmerged_table6_candidates.csv)에 보관했습니다. 열처리 유지 시간을 부식 노출 시간으로 사용하지 않았습니다.

## Elsevier를 어떻게 읽었나

Scopus·ScienceDirect 검색 API는 성공하지만 Article Retrieval API는 여전히 `403 AUTHENTICATION_ERROR`입니다. 위 Elsevier 12개는 **ScienceDirect 출판사 페이지가 검색 결과에 제공한 표**에서 전사한 값입니다. `retrieval_provider=publisher_search_excerpt`, 원자료 스냅샷 경로·SHA-256·표 번호·단위를 기록했습니다. 원문 전체 확보와 사람이 수행하는 대조 검증은 아직 남아 있습니다.

원문 대조가 필요한 데이터가 자동으로 모델 입력에 들어가지 않도록 `quality_hold_reason`을 추가했습니다. 집계 스크립트가 이를 보류 사유로 반영하며 Elsevier 값 12개 모두 임시 모델 입력에서 제외됐습니다.

[Elsevier iScience의 Ce 처리 강 HAZ 연구](https://doi.org/10.1016/j.isci.2025.113319)는 Europe PMC의 DOI 일치 XML을 확보했습니다. 출판사 그림 CDN의 Figure 5 원본도 읽었지만 i_corr 숫자가 인쇄되지 않은 막대그래프여서 추가하지 않았습니다. 그래프 좌표를 추정해 측정값인 것처럼 넣지 않았습니다.

추가 탐색한 N80 La·Ce, Ce 내후강, Cu·Ce 2205, Ce 초오스테나이트강 연구는 공개된 검색 내용만으로 수치·조건을 확정하지 못해 병합하지 않았습니다. [Springer 저합금강 RE 연구](https://doi.org/10.1007/s40195-022-01404-8)는 공식 PDF를 확보하고 Sol로 검사했지만 추출 가능한 명시적 i_corr 데이터 포인트는 0개였습니다.

## 재현

프로젝트 가상환경에서 다음을 순서대로 실행합니다. 추출 스크립트는 기존 응답을 재사용합니다. 새 논문에 대한 Sol 호출만 API 비용이 발생할 수 있습니다.

```powershell
.\.venv\Scripts\python.exe 04_분석실행코드/extract_publisher_round2.py
.\.venv\Scripts\python.exe 04_분석실행코드/build_elsevier_expansion.py
.\.venv\Scripts\python.exe 04_분석실행코드/assemble_extraction_pilot.py
.\.venv\Scripts\python.exe 04_분석실행코드/assemble_context_pilot.py
.\.venv\Scripts\python.exe 04_분석실행코드/build_nature_wiley_dataset.py
.\.venv\Scripts\python.exe 04_분석실행코드/update_collection_docs.py
```

이번에는 수집과 품질 분류를 갱신했습니다. 새 모델 성능이나 R²=0.8을 달성했다는 결과는 없습니다. 원문 대조와 중복·단위·시험조건 확인을 마친 데이터를 사용해 논문 단위 분할로 모델 및 Active Learning을 비교해야 합니다.
