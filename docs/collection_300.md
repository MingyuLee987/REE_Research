# 300개 목표 추가 수집 기록

2026-10-15. **목표는 총 300개 실험 데이터 포인트이며 아직 달성하지 못했습니다.** 원문·단위가 확인된 22개를 추가하여 전체 **27편·189개**가 됐습니다. 임시 분석 후보는 135개, 검토 보류는 54개, 사람 검증 완료는 0개입니다. 목표까지 111개가 부족합니다. 합성 데이터나 범위 밖의 코팅·억제제 자료로 채우지 않았습니다.

## 이번에 사용한 API와 원문

제공된 Elsevier API 키로 Scopus를, Springer 키로 Metadata/OA 서비스를 호출했습니다. 검색식과 응답은 `data/raw/round300/query_*.json`, `scopus_targeted_*.json`, `scopus_bulk_*.json`에 저장했습니다. Scopus의 벌크 희토류/철계/부식 중심 추가 검색식 한 개는 총 226개 레코드를 반환했고, 시작 위치 0~225에서 25개씩 조회했습니다. 이는 해당 검색식의 결과 수이며 전체 연구의 최종 독립 문헌 수가 아닙니다. 코팅·억제제·내화물 등 범위 밖의 결과를 후속 검토에서 제외했습니다.

Wiley 원문은 제공된 TDM 토큰으로 공식 TDM API에서 받았습니다. Springer 플랫폼 논문은 공식 PDF로 받았고, 다른 학회의 공개 원문도 DOI를 확인하여 확보했습니다. API 키로 **검색에 성공한 것**, **원문을 실제 확보한 것**, **i_corr 수치가 있는 것**을 구분했습니다. 300개 목표를 달성했다고 표시하지 않았습니다.

## 추가 데이터

| 출처 | 데이터 포인트 | 근거 | 품질 처리 |
| --- | ---: | --- | --- |
| [Wiley, La 함유 SASS의 자연해수 부식](https://doi.org/10.1002/adem.202402545) | 10 | PDF 9쪽 Figure 5e/f에 인쇄된 숫자: 5조성 × 0/16일 | 독립 원문 검토 전 pending. 곡선 좌표 추정 없음 |
| [Ce 첨가 고망간강](https://doi.org/10.1134/S2070205124702265) | 2 | Table 2, 2.81×10⁻⁵ 및 6.03×10⁻⁶ A/cm² | 시료별 조성 대신 공통 모재 조성이 보고되어 두 값 보류 |
| [Ce 첨가 중망간강](https://doi.org/10.1134/S2070205125700261) | 2 | Table 3, 2.389×10⁻⁴ 및 2.583×10⁻⁴ A/cm² | C·Mn 외 기존 핵심 조성이 부족하여 보류. Al은 별도 보고값으로 유지 |
| [B·Ce 미세합금화 S31254](https://doi.org/10.11902/1005.4537.2024.043) | 4 | 원문 HTML의 조성표와 i_corr 표 | Sol로 표·단위·시료 근거를 추출하고 자동 인용문 검증. pending |
| [Ce·W 함유 444형 페라이트강](https://doi.org/10.20964/2019.03.31) | 4 | 공식 저널 보관 PDF Table 2, 317/250/235/172 μA/cm² | 임계 부동태 전류·부동태 전류와 구분하여 i_corr만 추출. pending |
| 합계 | **22** | | |

Wiley La 연구는 이전 La 연구들과 조성 계열이 일치하지만 자연해수에서 측정했으므로 기존 알칼리 해수 조건과 동일 실험으로 합치지 않았습니다. 동일 재료 계열을 여러 논문에서 재사용했을 가능성이 있어, 향후 모델 검증에서는 관련 논문들을 같은 그룹으로 묶는 민감도 검사가 필요합니다. 이번에는 새 모델 성능이나 Active Learning 성능을 계산하지 않았습니다.

## 발견했지만 합치지 않은 60개 숫자

[Elsevier Ce 첨가 초오스테나이트강 연구](https://doi.org/10.1016/j.jallcom.2026.189103)의 출판사 그림 원본을 확보했습니다. Figure 6, 7, 8의 작은 표에서 Sol 이미지 입력으로 **인쇄된 전류 표기 60개**를 읽어 원본·응답·단위를 별도 보관했습니다. 이는 아직 확정된 60개 독립 i_corr 실험 데이터 포인트가 아닙니다.

표 헤더는 `Ic(A)`, 축은 `Current density(A)`로 표시되어 있습니다. 따라서 전류 A인지 전류밀도 A/cm²인지 확인하고, 필요한 경우 노출 전극 면적으로 정규화해야 합니다. 그림 a~d와 실제 노출 시간·온도의 대응도 원문 설명과 확인해야 합니다. 현재 원문 전체를 확보하지 못했으므로 면적 1 cm²나 특정 시험 날짜를 가정하지 않았습니다. **이 값들은 전체 189개와 모델 입력 135개에 포함하지 않았습니다.**

저장 위치: [미병합 전류 표기 목록](../data/raw/round300/ce_alkaline_images/unmerged_current_annotations.csv). 이 논문의 전문 Methods와 figure captions가 확보되면 우선 검토할 후보입니다.

## 제외·접근 실패

Wiley의 추가 내후강 원문, Springer의 Y 첨가 304·Ce 첨가 2507·Cr/RE 철근·20Cr13·오래된 이중상강 연구 등도 확보·검토했습니다. 부식속도, 점부식 전위, 부동태 전류만 있거나 수치가 없는 그래프만 확인된 경우 i_corr 데이터로 추가하지 않았습니다. 내화물의 슬래그 부식 연구는 재료 범위에서 제외했습니다. 제공된 키로 Elsevier 검색은 가능하지만 원문 API 접근 문제는 계속되고, 일부 IOP·중국 학회·오래된 원문의 PDF 접근도 실패했습니다. 공개 그림과 보충파일도 확인했지만 정규화에 필요한 원문을 확보하지 못한 경우 보류했습니다.

## 파일

- [전체 수집본 189개](../data/processed/pilot100/llm_pending_all.csv)
- [이번 추가 22개](../data/processed/round300/new_measurements_pending.csv)
- [단위·피처를 계산한 임시 후보 135개](../data/processed/context_v2/features_v3_pending.csv)
- [보류 54개](../data/processed/pilot100/held_for_review.csv)
- [목표·부족분·논문별 집계](../data/processed/round300/status.json)

`pilot100`은 기존 폴더명입니다. 데이터가 100개로 제한된다는 뜻이 아니며, 현재 목표는 상태 파일의 `target_rows: 300`으로 기록됩니다. 기존 피처 비교 보고서는 117개 중 개발 110개를 사용한 과거 결과이며, 파일이 갱신됐다는 이유로 135개를 평가한 성능으로 해석하지 않습니다.

## 재현

```powershell
.\.venv\Scripts\python.exe -B scripts/discover_300.py
.\.venv\Scripts\python.exe -B scripts/collect_300_sources.py
.\.venv\Scripts\python.exe -B scripts/extract_round300.py
.\.venv\Scripts\python.exe -B scripts/build_wiley_seawater_rows.py
.\.venv\Scripts\python.exe -B scripts/assemble_round300.py --annotate-only
.\.venv\Scripts\python.exe -B scripts/assemble_extraction_pilot.py
.\.venv\Scripts\python.exe -B scripts/assemble_context_pilot.py
.\.venv\Scripts\python.exe -B scripts/build_nature_wiley_dataset.py
.\.venv\Scripts\python.exe -B scripts/assemble_round300.py
.\.venv\Scripts\python.exe -B scripts/update_collection_docs.py
```

추가 후속 검색·다운로드 응답도 `data/raw/round300`에 보관했습니다. 위 기본 수집 스크립트가 모든 후속 수동 선택 원문을 새로 다운로드하는 것은 아니므로 재현 시 보관된 원자료를 함께 사용해야 합니다. `read_round300_annotations.py`는 미병합 숫자 60개의 판독을 재현하며, 응답 캐시가 없을 때 Sol API 비용이 발생합니다.
