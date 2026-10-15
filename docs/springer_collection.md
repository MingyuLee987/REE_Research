# Springer Nature API 추가 수집

> 이 문서는 이전의 60개 추가 수집 기록입니다. 이후 Wiley·Springer 자료를 더 수집했으며 [최신 두 출판사 데이터셋](nature_wiley_collection.md)은 8편·107개입니다.

2026-10-15, 기존 API 키로 Springer Nature **Open Access API**를 사용해 검색하고 JATS 원문을 받았습니다. 구독 원문용 TDM 권한이 생겼다는 뜻은 아닙니다.

## 확보한 데이터

[Corrosion behavior and electrochemical properties of heat-treated Fe-20Cr-18Ni-6Mo-0.8Cu-0.2N-La alloys in alkaline seawater](https://doi.org/10.1038/s41529-025-00682-8)에서 **60행**을 확보했습니다. 요청한 약 50행보다 많은 것은 전체 조건 조합을 보존했기 때문입니다.

| 구분 | 원문 조건 |
| --- | --- |
| 합금 | La 명목 함량 0, 0.5, 1.0, 1.5, 2.0 wt.%의 철계 스테인리스강 |
| 실제 La 분석값 | 0, 0.49, 0.98, 1.48, 1.98 wt.% — Table 1 ICP-AES |
| 온도 | 25, 50, 75 °C |
| 노출 시간 | 0, 2, 4, 8일 → 0, 48, 96, 192시간 |
| 타깃 | Figures 6a, 8a, 10a에 인쇄된 i_corr, A/cm² |
| 용액 | seawater + 40 g/L NaOH + 7.1 g/L Na2SO4 |
| pH | 원문 `>14`; 수치형 pH는 결측으로 보존 |
| 열처리 | 1200 °C, 1시간, 수냉 |

5조성 × 3온도 × 4노출 시간 = **60개 서로 다른 실험 조건**입니다. 그림의 곡선이나 좌표에서 값을 추정한 것이 아니라, 그림 안에 명시적으로 인쇄된 수치를 전사했습니다. 기존 데이터셋에 없던 DOI이며, 같은 결과를 본문·초록에서 다시 세지 않았습니다.

## API와 LLM이 한 일

1. `https://api.springernature.com/openaccess/json`으로 7개 검색식을 페이지별 조회했습니다. DOI 중복을 제거한 후보는 2,081개입니다. 검색 결과에는 참고문헌에만 검색어가 등장한 자료도 있으므로 모두 적합 논문은 아닙니다.
2. `/openaccess/jats?q=doi:...`로 대상 논문 원문을 확보하고 요청 DOI와 JATS의 실제 article-id가 같은지 검사했습니다.
3. JATS 그림 링크를 따라 Springer Nature의 공식 이미지 서버에서 Figures 6·8·10 원본 이미지를 확보했습니다.
4. 에이전트가 인쇄된 수치 60개를 전사했습니다. Sol에는 전사값을 주지 않고 원본 이미지만 읽혀 별도로 대조했습니다. 동일 모델 계열의 재독은 사람 검증이나 독립 실험 검증을 대체하지 않습니다.
5. 원문 Table 1의 실제 조성과 결합했습니다. 조성 미보고 C·Si·Mn 등을 0이나 강종 표준값으로 채우지 않았습니다.

검색에서 페이지 크기 100 요청은 403이었으며 25로 줄여 진행했습니다. 일부 429는 제한된 대기 후 재시도했습니다. API 키는 응답 저장 전 제거합니다.

## 파일

- [이번 Springer 60행](../data/processed/extractions/springer_la_asw_2025/pending_measurements.csv)
- [원본 이미지 재독 대조 결과](../data/processed/extractions/springer_la_asw_2025/vision_check_summary.json)
- [원문과 API 메타데이터](../data/raw/springer_round/s41529-025-00682-8/metadata.json)
- [누적 전체 데이터](../data/processed/pilot100/llm_pending_all.csv)
- [문맥 보강 포함 임시 후보](../data/processed/context_v2/provisional_enriched.csv)

전체 데이터는 **13편·112행**, 기존 품질 기준상 보류 7행을 제외한 임시 후보는 **105행**입니다. 모두 `pending`이며 사람 검증 완료는 **0행**입니다. 100행이라는 추출 개수 목표를 넘었지만 검증한 100행을 확보한 것은 아닙니다. 모델 성능은 이번에 다시 계산하지 않았습니다.

## 해석할 때 주의할 점

이번 60행은 **한 논문**에서 나왔습니다. 논문 60편이나 독립적으로 검증된 표본 60개로 해석하지 않습니다. 모델 평가에서 이 DOI의 모든 행은 반드시 같은 분할에 두어야 합니다. 해당 논문이 데이터셋의 절반 이상이므로 논문별 가중치, 논문 단위 CV, 이 논문 포함/제외 민감도 분석이 필요합니다.

이 연구는 고합금 스테인리스강의 강알칼리 해수 환경입니다. 기존 탄소강·중성 염수 데이터와 범위가 넓어졌으므로, 전체 행 수 증가만으로 기존 연구 범위의 예측 성능이 높아졌다고 판단하지 않습니다. 논문은 원래 합금 표면을 산 세정한 뒤 측정했으므로 산 세정 조건도 기록했습니다.

추가로 받은 HRB400-Cr-RE 논문은 I_pass 표를 i_corr로 바꾸지 않았고, Y-304 논문의 부식전위 표와 Ce-2507 논문의 EIS 저항 표도 타깃으로 사용하지 않았습니다. 기존 HRB500E 논문은 DOI 중복으로 추가하지 않았습니다.

## 재현 명령

```powershell
uv run --no-sync python scripts/collect_springer_round.py
uv run --no-sync python -m scripts.fetch_springer_sources
uv run --no-sync python scripts/build_springer_annotation_rows.py
uv run --no-sync python -m scripts.check_springer_annotations
uv run --no-sync python scripts/assemble_extraction_pilot.py
uv run --no-sync python scripts/assemble_context_pilot.py
```

마지막 합치기는 이미지 대조에 불일치가 없는지 확인한 뒤 실행합니다. 원문 그림 파일과 JATS가 있어야 전사 스크립트를 실행할 수 있습니다.
