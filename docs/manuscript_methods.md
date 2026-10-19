# 문헌 검색 및 데이터 구축 방법: 논문용 초안

최신 집계(2026-10-19): **44편·283개 관측 레코드**, 정규화된 i_corr 값 251개·단위 미확정 32개, 임시 후보 24편·151개·보류 132개다. 모두 검토 대기이며 사람의 독립 검증은 완료되지 않았다. 50편 검토목록 중 6편은 채택 가능한 i_corr가 없어 통합본에 넣지 않았다. 이번 추가분 36개는 모두 보류했으며 새 모델을 적합하지 않았다. [추가 수집과 보충자료 확인](expansion50_20261019.md), [현재 자료의 해석](interpretation_20261019.md)을 참조한다.

후속 그래프 추출에는 기존 마지막 주기 대표값 14개 외에 초페라이트계 합금의 저자 산출 i_corr 막대값 3개가 추가되었다. 축·좌표·단위·원문 위치·판독 허용폭을 보존했고 그래프 추정치는 모두 모델에서 보류했다. 판독 허용폭은 실험 오차나 통계적 신뢰구간이 아니며 분극곡선의 최저 전류를 i_corr로 취급하지 않았다. 아래 10월 16일 보완 설명은 이전 단계의 이력이다.

최신 보완: 2026-10-16 통합본은 **37편·247개 관측 기록**, 임시 후보 151개·보류 96개다. 후속 그래프 수치화에서 126개 연속 주기 관측점을 기록했으나 독립 실험으로 중복 집계하지 않고 14개 시료·용액 조합의 마지막 주기 대표값만 추가했으며 모두 학습에서 보류했다. [그래프 추출과 판독 허용폭](target400_graph_extraction.md)을 따른다. 아래의 그래프 추출 제외 설명은 기존 233개 자료의 수집 절차를 기술한다. 아래 31편·219개 집계와 과거 교차검증도 이전 스냅샷이다. 400개 수집 또는 최종 모델 검증을 완료한 것으로 기술하지 않는다.

후속 확장 단계에서는 원본 PDF 그래프의 축 교정과 식별 가능한 표식 좌표 판독으로 근삿값을 수집하고, 원래 단위·환산값·주기 번호·픽셀 판독 허용폭을 보존하였다. 보간선에서 새 관측값을 생성하지 않았으며, 같은 시료의 연속 주기를 독립 실험으로 취급하지 않았다. 순환 전압전류 시험 값과 Tafel i_corr의 방법적 동등성 및 최종 조성이 미확인된 자료는 보류하였다. 해당 14개는 기존 명시적 수치 추출 자료와 구분해야 한다.

In a subsequent expansion, graph-derived estimates were digitized from identifiable markers in the original PDF raster images using linear axis calibration. Original units, converted current densities, cycle indices, and a pixel-based reading tolerance were retained. The tolerance describes reading resolution rather than experimental uncertainty. Consecutive polarization cycles were not treated as independent experiments: only the last observed cycle for each of 14 material–solution series was appended to the master dataset. All 14 graph-derived representatives were held from modeling because equivalence to Tafel-derived corrosion current density and final bulk chemistry remained unconfirmed. The graph-exclusion statements below describe the earlier 233-record collection stage.

상·조성 보강(2026-10-16): 확보한 전문 블록 25편을 gpt-6.1-sol로 재독하여 시험 전 모재 상·이차상·조성을 보충하였다. 원문 위치와 인용문이 일치하는 필드만 반영하고, 미보고 성분·분율은 생성하지 않았다. 저자의 재료 계열 설명과 시험 전 조직 관찰 근거를 구분했다. 당량은 조성 기술자로 계산하고 실제 상분율로 해석하지 않았다. 기존 타깃과 보류 상태를 유지했다. 새 46개 후보 피처 및 135개 관측값/19편의 개발 교차검증 방법은 [상·조성 보강 기록](phase_features_v4.md)을 따른다. 사람의 원문 검증과 최종 독립 검증은 아직 완료되지 않았다.

기준일: **2026-10-19**. 저장된 API 응답, 수집 코드, 원문 및 추출 기록에 근거한 Methods 초안입니다. 실제 수행하지 않은 전수 검색, 이중 독립 검토, 최종 모델 평가를 완료한 것으로 서술하지 않았습니다. API 검색식 감사는 10월 16일 스냅샷이며 후속 웹 검색 전체를 포함하지 않습니다. 이번 변경 전 문서는 [이전 판본](manuscript_methods_before_20261019.md)에 보존했습니다.

## 1. 검색 범위와 키워드

목적은 **희토류가 벌크 철계 합금에 첨가된 실험 연구와 동일 연구의 대조군에서 보고한 부식전류밀도**를 수집하는 것입니다. 아래 용어는 저장된 검색식에서 확인된 용어입니다. 모든 용어를 한 검색식에 동시에 넣은 것은 아닙니다.

| 개념 | 저장된 API 검색식의 용어 | 사용 목적 |
| --- | --- | --- |
| 희토류 | `"rare earth"`, `cerium`, `lanthanum`, `yttrium`, `praseodymium`, `neodymium`, `mischmetal` | 희토류 첨가 연구 검색. Europe PMC 보완 검색에는 `Ce`, `La`, `scandium`도 사용 |
| 철계 재료 | `steel`, `steels`, `iron`, `"pure iron"`, `ferrous`, `"Fe-based"` | 철계 합금·강·순철 연구 확보. 일부 Springer 검색은 `stainless`, `rebar` 사용 |
| 부식·측정 | `corrosion`, `polarization`, `"current density"`, `"corrosion current"`, `"corrosion current density"`, `Tafel` | 부식 및 전기화학 측정 자료 탐색 |
| 합금화·개재물 | `addition`, `microalloying`, `inclusion`, `alloying` | 벌크 합금 첨가 연구의 검색 우선순위 강화 |
| 일부 검색식의 제외어 | `inhibition`, `inhibitor`, `coating`, `coatings`, `conversion`, `synergism`, `nanoparticles`, `deposited` | 표면처리·억제제 연구의 검색 잡음 감소. 모든 검색에 일괄 적용하지 않음 |

일반 설명에서 `i_corr`를 목표 변수로 사용하지만, 이를 모든 API 검색에 필수 검색어로 넣지는 않았습니다. 검색식에 없는 단어를 실제 수행한 검색식에 사후 추가하지 않았습니다. Wiley Online Library를 포함한 후속 출판사 페이지 탐색에는 논문 제목, DOI, 재료명 및 중국어 용어(예: 稀土, 铈, 镧, 钇, 腐蚀电流密度)를 활용했습니다. 이 웹 검색의 전체 검색어·시각을 통합한 로그는 없으므로, API 검색식 목록을 전체 웹 검색 기록으로 표현하지 않습니다.

## 2. 검색 서비스와 원문 확보 경로

| 서비스/경로 | 실제 역할 | 논문에서 구분할 점 |
| --- | --- | --- |
| Elsevier Scopus API | 제목·초록·키워드 및 제목 검색 | 여러 출판사를 포괄하는 서지 검색 서비스. Scopus 검색 결과가 모두 Elsevier 논문인 것은 아님 |
| Elsevier ScienceDirect | 출판사 페이지·검색 결과 및 접근 가능한 공개 자료 확인 | 검색과 원문 API 접근은 별도. Article Retrieval API의 403은 미해결 |
| Springer Nature Metadata API | 메타데이터 기반 후보 검색 | 메타데이터 확보가 전문 확보를 뜻하지 않음 |
| Springer Nature Open Access API | 공개 논문 검색 및 이용 가능한 JATS 원문 확보 | 공식 PDF 확보와 별도로 출처 기록 |
| Wiley Online Library 및 출판사 페이지 후속 탐색 | 제목·DOI로 Wiley 후보 논문 확인 | 웹 후속 탐색이며 전체 검색어·시각의 통합 로그는 없음 |
| Wiley TDM API | 이미 확인한 DOI로 원문 PDF 요청 | 포괄적 문헌 검색 데이터베이스로 사용했다고 기술하지 않음 |
| Europe PMC | 공개 문헌 보완 검색 및 DOI 일치 원문 XML 확보 | 출판사와 저장소를 구분. DOI가 같은 사본은 별도 논문으로 중복 집계하지 않음 |
| 출판사·학회 공식 HTML/PDF | 후속 제목/DOI 검색 및 표·그림 확인 | MDPI·중국 학회지 등 세 출판사 이외의 자료도 전체 수집본에 포함 |

따라서 전체 데이터셋을 **“Elsevier, Springer Nature, Wiley의 세 출판사 논문만으로 구성하였다”**고 쓰면 현재 기록과 맞지 않습니다. 적절한 표현은 **“세 출판사 자료를 중심으로 검색하고 공개 저장소 및 기타 출판사·학회의 원문으로 보완하였다”**입니다.

## 3. 실제 실행한 검색식: 대표 예시

다음 문자열은 저장된 응답에서 회수한 실제 검색식입니다. 줄바꿈만 가독성을 위해 추가했습니다. 전체 문자열과 저장 응답 경로·SHA256·페이지별 레코드 수는 [Supplementary 검색식 목록](search_query_log.md) 및 [기계 판독 로그](search_query_log.json)에 있습니다.

### Scopus: 합금화 중심 탐색 (S08)

```text
TITLE-ABS-KEY((cerium OR lanthanum OR "rare earth")
AND (steel OR steels)
AND corrosion
AND (addition OR microalloying OR inclusion OR alloying))
```

### Scopus: 전기화학 측정 중심 탐색 (S07)

```text
TITLE-ABS-KEY((cerium OR lanthanum OR "rare earth")
AND (steel OR steels)
AND (polarization OR "current density" OR Tafel))
```

### Scopus: 제목 중심 및 잡음 제외 탐색 (S01)

```text
TITLE(cerium OR lanthanum OR yttrium OR "rare earth" OR mischmetal)
AND TITLE(corrosion)
AND TITLE(steel OR iron)
AND NOT TITLE(inhibition OR inhibitor OR coating OR coatings
OR conversion OR synergism OR nanoparticles OR deposited)
```

이 검색식의 저장 응답은 총 hit 226개를 보고했으며 시작점 0, 25, …, 225의 10개 응답 파일로 해당 결과를 조회했습니다. **226개는 이 검색식의 서지 결과 수이고 적합 논문 수나 실험 데이터 포인트 수가 아닙니다.**

### Scopus: 2026-10-16 추가 검색 (S11)

```text
TITLE-ABS-KEY((cerium OR lanthanum OR yttrium)
AND steel AND "corrosion current")
```

이 검색식은 총 hit 136개를 보고했지만 저장한 응답은 첫 25개입니다. 전수 조회라고 기술하지 않습니다.

### Springer Nature: 서비스에 전달한 문자열 예시

```text
cerium corrosion steel
lanthanum corrosion steel
yttrium corrosion steel
cerium corrosion stainless
"rare earth" rebar corrosion
"rare earth" "steel" "corrosion"
cerium corrosion steel microalloying
```

Scopus의 `TITLE-ABS-KEY`와 동일한 필드 제한을 적용했다고 기술하지 않습니다. Springer 문자열의 용어가 해당 서비스에서 모두 필수 AND 조건으로 처리됐다고 사후 가정하지 않습니다. 검색 결과를 후속 제목·초록·원문 검토로 선별했습니다. 일부 OA 수집 코드에는 검색식별 최대 1,500개 조회 제한이 있습니다.

### Europe PMC: 공개 원문 보완 탐색 (S19)

```text
(cerium OR lanthanum OR "rare earth")
AND (steel OR steels OR "pure iron")
AND corrosion AND OPEN_ACCESS:Y
```

추가로 제목 제한 검색과 DOI 기반 사본 확인을 사용했습니다. DOI 사본 확인 쿼리는 새로운 주제 검색과 구분하여 보충 목록에 보존했습니다.

## 4. 기간, 언어, 등급, 검색 수의 보고

- 최신 수집 갱신일은 **2026년 10월 19일**입니다. 아래 API 검색식 감사 수치는 10월 16일 스냅샷입니다. 개별 응답에 요청 시각이 없으면 “미기록”으로 표시했습니다. 파일 수정 시각을 검색 시각으로 대체하지 않았습니다.
- 모든 검색에 공통된 출판연도 구간은 없습니다. 일부 Scopus 검색에는 `PUBYEAR < 2020`, `PUBYEAR > 2019 AND PUBYEAR < 2026`, `PUBYEAR < 2015`, `PUBYEAR > 2024`를 각각 적용했고 다른 검색에는 연도 제한이 없습니다.
- 저장된 API 검색식에 일괄적인 언어 제한은 없으며 중국어 원문도 포함했습니다. “영문 논문만 포함”이라고 쓰지 않습니다.
- Q1/Q2 저널 한정, JCR/SJR 기준, 피인용 횟수 하한을 적용하지 않았습니다.
- 현재 감사에서 회수한 것은 **46개 서비스–검색식 조합과 176개 저장 응답 파일**입니다. 재사용·페이지 응답을 포함하므로 176회의 독립적인 신규 검색이나 176편의 논문으로 해석하지 않습니다. 전체 웹 검색 기록도 아닙니다.
- 검색식별 API 총 hit는 서로 겹치므로 합산하지 않습니다. 일부 검색은 첫 페이지 또는 제한된 결과만 확보했습니다. 초기 141편 후보 집계도 후속 전체 수집의 최종 분모로 사용하지 않습니다.

## 5. 문헌 및 실험 기록의 포함·제외 기준

**문헌 검색과 최종 데이터 포함은 다른 단계입니다.** 제목·초록의 키워드 점수는 검토 우선순위를 정하는 용도였으며 적합성 확정이나 LLM 독립 선별 검증을 뜻하지 않습니다.

| 단계 | 기준 |
| --- | --- |
| 연구 범위 포함 | 희토류를 벌크 철계 재료에 첨가한 실험 연구 및 같은 연구의 무첨가/비교 대조군 |
| 수치 추출 대상 | 시료에 연결되는 명시적 i_corr 수치. 원문 표·본문 또는 그림에 인쇄된 숫자 |
| 연구 범위 제외 | 희토류 코팅·증착층만 연구한 자료, 용액 내 희토류 억제제, 비철 합금, 리뷰의 재인용 수치, 철계 재료가 아닌 내화물의 부식 |
| 목표 변수 제외 | 부동태 전류, 부식전위, 국부 전류, Rct/Rp, 중량감소 부식속도만 있는 경우. 이 값을 i_corr로 대체하지 않음 |
| 후속 그래프 추출 | 축·시료·단위가 식별되는 i_corr 표식·막대값은 추정치와 판독 허용폭으로 기록하고 모델에서 보류. 반복 평균 복제와 분극곡선 최저 전류의 i_corr 대체는 제외 |
| 기록하되 분석 보류 | 조성·시료·조건 대응 불명확, 전체 원문 없이 표/초록 발췌만 확보, 원문 수치/단위 불일치, 정규화 타깃 미확정 |

DOI는 소문자화하고 DOI URL 접두사를 제거하여 중복 서지 기록을 통합했습니다. DOI가 없으면 정규화된 제목을 보조 식별자로 사용했습니다. 서로 다른 DOI를 제목이 같다는 이유만으로 합치지 않았습니다. 같은 실험이 표·그림·다른 논문에서 재사용되었는지는 별도 원문 검토가 필요합니다. 자동 record ID 중복 검사만으로 모든 과학적 중복이 제거됐다고 주장하지 않습니다.

## 6. 원문 처리, LLM, 단위 및 검토

PDF는 pypdf와 필요한 경우 PyMuPDF로 페이지 단위 텍스트를 추출하고 XML/HTML은 문단·표 단위 근거 블록으로 변환했습니다. PDF의 글자 인코딩 문제 등으로 텍스트 판독이 불가능한 경우 렌더링한 원문을 시각적으로 확인했습니다.

**OpenAI `gpt-6.1-sol`**을 Responses API로 호출하여 JSON 스키마에 따라 시료, 조성, 희토류 종류·함량, 환경·처리·측정 조건, 원래 i_corr 수치·단위 및 출처 위치를 추출했습니다. 별도 미세조정은 하지 않았습니다. `gpt-6-luna`는 선별용 설정만 준비했으며 실제 추출에 사용한 모델로 기술하지 않습니다. temperature, top-p, 생성 seed는 코드에서 명시적으로 설정하지 않았습니다.

텍스트 추출값은 근거 문구와 출처 블록을 자동 대조했습니다. 근거 문구 일치가 시료·조건 연결의 과학적 정확성을 보증하지는 않습니다. 일부 수치표·그림의 인쇄값은 에이전트가 전사하고 동일 Sol 모델의 이미지 입력으로 대조했습니다. 모든 값이 LLM 텍스트 추출을 통과했다고 기술하지 않으며, 이 과정을 “독립된 사람 검증”으로 부르지 않습니다.

단위가 명확한 i_corr는 A/cm²로 통일했습니다(mA/cm² ×10⁻³, µA/cm² ×10⁻⁶). 명시적인 표의 배율도 반영했습니다. 조성은 wt.%, 희토류 함량은 질량 ppm으로 기록했습니다(1 wt.%=10,000 ppm). 명목 첨가량·실제 최종 재료 함량을 구분하고 범위·상한·미보고 조성을 임의의 점 추정치나 0으로 치환하지 않았습니다. 실온을 25 °C로 지정하거나 근거 없이 NaCl wt.%를 Cl⁻ mol/L로 환산하지 않았습니다.

출처 DOI, 시료 ID, 표/페이지/그림 위치, 근거 문구 또는 전사 기록, 원래 수치·단위, 가능한 파일 해시 및 검토 상태를 보존했습니다. 현재 사람의 독립 원문 검증은 완료하지 않았습니다.

## 7. 논문 본문용 한국어 문안

Wiley의 활용 경로는 다음과 같이 명시한다. 아래 문안의 출판사 페이지 후속 탐색에는 Wiley Online Library가 포함되며, Wiley TDM API는 서지 검색이 아닌 DOI 기반 원문 확보에 사용하였다.

> 희토류 첨가 철계 합금의 부식전류밀도 예측을 위한 문헌 데이터 수집을 위해 반복적 표적 문헌 검색을 수행하였다. 서지 검색에는 Elsevier Scopus API와 Springer Nature Metadata 및 Open Access API를 사용하였으며, Europe PMC의 공개 문헌 검색과 Wiley Online Library를 포함한 출판사·학회 페이지의 제목 및 DOI 기반 후속 탐색으로 자료를 보완하였다. 확인된 Wiley 논문의 원문 PDF는 Wiley Text and Data Mining(TDM) API를 통해 DOI 기반으로 요청·확보하였다. Wiley TDM API는 키워드 기반 서지 검색에 사용하지 않았다. 검색어는 희토류 관련 용어(cerium, lanthanum, yttrium, rare earth 등), 철계 재료 용어(steel, steels, iron, pure iron 등), 부식·전기화학 측정 용어(corrosion, polarization, current density, Tafel 등), 합금화 관련 용어(addition, microalloying, inclusion, alloying)를 조합하였고 서비스별 검색 문법에 맞추어 적용하였다. 실제 검색식과 확보된 페이지 범위는 보충자료에 제시하였다. 검색은 2026년 10월 16일까지 갱신하였으며, 모든 검색에 공통된 출판연도·언어·저널 사분위 등급 제한을 적용하지 않았다. 본 절차는 데이터 구축을 위한 표적 탐색이며 전수 체계적 문헌고찰로 간주하지 않았다.
>
> 검색된 문헌은 DOI를 정규화하여 중복 서지 기록을 통합한 뒤 제목·초록과 접근 가능한 원문을 순차적으로 확인하였다. 희토류가 벌크 철계 재료에 첨가된 실험 연구 및 동일 연구의 대조군을 포함하였으며, 희토류 코팅, 용액 내 부식억제제, 비철 합금 및 리뷰의 재인용 수치는 제외하였다. 시료에 연결되는 명시적 부식전류밀도 수치를 표·본문 또는 그림의 인쇄된 숫자에서 수집하였고, 부동태 전류·부식전위·임피던스·중량감소 부식속도로 대체하지 않았다. 후속 단계에서는 식별 가능한 i_corr 표식·막대값을 축 교정으로 추정하고 좌표·원래 단위·판독 허용폭을 보존했으며 해당 추정치는 모델에서 보류하였다. 서지 검색과 원문 확보는 구분하였으며, Wiley 원문은 확인된 DOI로 TDM API를 통해 확보하였다. Elsevier Article Retrieval API의 접근 제한은 지속되어, 가능한 공개 사본 및 출판사 표·초록 발췌를 대체 근거로 기록하였고 발췌만 확보한 자료는 분석에서 보류하였다.
>
> 원문을 출처 위치가 부여된 근거 블록으로 변환한 후 OpenAI gpt-6.1-sol을 이용하여 합금 조성, 희토류 함량, 시험 조건, i_corr 및 근거 정보를 구조화하였다. 에이전트의 수치 전사와 일부 이미지 입력 대조도 병행하고 추출 경로를 구분하였다. 단위가 명확한 경우에만 A/cm²로 환산하였으며, 미보고 값은 결측으로 유지하였다. 원문 근거 문구와 식별자를 자동 확인하고 조성 부족, 단위·수치 불일치 및 시료·조건 대응의 불확실성이 있는 자료에는 보류 사유를 부여하여 임시 모델 입력에서 제외하였다. 이러한 검사는 출처 추적을 위한 자동 검사로 수행되었으며 독립적인 사람 검증을 대체하지 않았다.

## 8. English manuscript text

### Literature search and eligibility

A targeted, iterative literature search was performed to collect experimental corrosion-current-density data for rare-earth-containing bulk ferrous alloys and the corresponding within-study controls. Bibliographic discovery used the Elsevier Scopus API and the Springer Nature Metadata and Open Access APIs, supplemented by Europe PMC searches and title- and DOI-based searches of publisher and society websites, including Wiley Online Library. Full-text PDFs of identified Wiley articles were requested and acquired by DOI through the Wiley Text and Data Mining (TDM) API; this API was used for full-text retrieval rather than keyword-based bibliographic discovery. Search expressions combined rare-earth identifiers (e.g., cerium, lanthanum, yttrium, and “rare earth”), ferrous-material terms (e.g., steel, steels, iron, and “pure iron”), corrosion and electrochemical terms (e.g., corrosion, polarization, “current density,” and Tafel), and alloying-related terms (addition, microalloying, inclusion, and alloying). Expressions were adapted to each service; the recorded expressions and retrieved page ranges are provided in the Supplementary Methods. Collection was updated through 19 October 2026; the API-query audit describes the earlier 16 October snapshot. No common publication-year interval, language restriction, or journal-quartile criterion was applied across all searches. The procedure was intended for targeted dataset construction and was not an exhaustive systematic review.

Repeated bibliographic records were consolidated using normalized DOIs, with normalized titles used as a secondary identifier when a DOI was unavailable. Titles and available abstracts were used to prioritize source examination, followed by inspection of accessible article content. Experimental studies of rare-earth additions to bulk ferrous materials and their within-study controls were eligible. Studies confined to rare-earth-containing coatings, rare-earth electrolyte inhibitors, non-ferrous alloys, and secondary measurements quoted in reviews were excluded. Extraction targeted explicit numerical corrosion current densities associated with identifiable samples. Passive currents, corrosion potentials, impedance parameters, local currents, and weight-loss corrosion rates were not substituted for corrosion current density. In subsequent stages, identifiable current-density markers and author-derived bars were digitized using calibrated axes and explicit reading tolerances; these graph estimates remained held from modeling. Reported means were not replicated according to experimental repeat counts.

### Acquisition, extraction, and quality control

Bibliographic discovery was distinguished from full-text acquisition. Accessible publisher XML, HTML, and PDFs and DOI-matched public repository copies were used as source documents. Wiley PDFs were requested by DOI through the Wiley Text and Data Mining API. Elsevier Article Retrieval API access remained restricted in the execution environment; successful bibliographic search responses were not treated as successful full-text retrieval. Numerical publisher-page excerpts were retained as a distinct evidence type, and excerpt-only records were held from provisional modeling pending full-source review.

Source documents were converted to addressable paragraph, table, or page-level evidence blocks. OpenAI gpt-6.1-sol, accessed through the Responses API with structured JSON outputs, assisted extraction of sample identities, compositions, rare-earth contents, test conditions, corrosion current densities, and provenance. Agent-assisted transcription and selected image-input cross-checks of printed numerical entries were also used and recorded separately. No project-specific fine-tuning was performed. The extraction code did not explicitly set temperature, top-p, or a generation seed. Automated source-fragment matching established traceability rather than scientific validation of sample–condition attribution. Corrosion current density was converted to A cm⁻² only when the reported unit and multiplier were unambiguous. Unreported or ambiguous values were retained as missing. Records with insufficient composition, unresolved units, conflicting values, or uncertain sample–condition correspondence were assigned explicit holds and excluded from provisional modeling. All records remained pending independent human review.

## 9. 현재 집계와 투고 전 확정 사항

현재 통합본은 **44편·283개 레코드**이며 정규화된 i_corr 값 251개, 단위 미확정 32개입니다. 임시 후보는 24편·151개, 보류는 132개, 사람 검증 완료는 0개입니다. 이번 추가분 36개는 모두 보류했으며 새 모델을 학습하지 않았습니다. 별도 50편 검토목록을 추출 완료 논문 수로 표현하지 않습니다. 기존 개발 교차검증 점수는 당시 데이터의 결과이며 이번 통합본의 최종 검증 성능이 아닙니다.

투고 전 실제로 완료해야 할 사항은 다음과 같습니다.

1. 원문·단위·시료 대응을 사람이 확인하고 검토자 수와 불일치 해결 방법을 실제 기록에 맞게 기재합니다.
2. 최종 포함 논문 수와 실험 데이터 수, 보류·제외 수를 고정합니다. 원문 재사용/관련 재료 계열의 중복도 검토합니다.
3. PRISMA 형태의 흐름도를 쓰려면 API·웹·DOI 후속 탐색을 통합한 식별·중복·제외 장부를 먼저 완성합니다. 현재 검색 hit 총합으로 대신하지 않습니다.
4. 최종 학습/검증 분할, 사용 피처, 모델·Active Learning 결과는 실제 평가 후 Methods와 Results에 추가합니다.

재현: `python -B scripts/audit_search_queries.py`로 로컬에 저장된 검색식 목록을 다시 생성할 수 있습니다. 신규 API 호출은 없습니다. 원문과 실제 데이터는 기존 Git 제외 정책에 따라 별도로 보존합니다.
