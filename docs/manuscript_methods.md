# 논문 Methods 초안: 문헌 검색과 LLM 보조 데이터 구축

> 아래 본문의 집계는 **초안 작성 당시 22편·167개 판본**입니다. 이후 추가 수집으로 전체는 27편·189개, 임시 후보 135개·보류 54개가 됐으며 300개 목표에는 111개가 부족합니다. [최신 수집·접근 한계](collection_300.md)를 기준으로 최종 투고 시 집계와 출처 범위를 다시 고정해야 합니다. 현재도 사람 검증 완료는 0개입니다.

작성 기준: 2026-10-15의 코드, 원자료 및 추출 로그. 아래 영어·한국어 본문은 **현재 실제 수행한 작업**을 기술합니다. 사람 검증과 최종 모델·Active Learning 평가는 완료되지 않았으므로 완료했다고 표현하지 않았습니다.

## 먼저 확정해야 할 데이터 범위

| 출판사 | 데이터가 확보된 논문 | 수집 실험 데이터 포인트 | 임시 분석 후보 | 보류 |
| --- | ---: | ---: | ---: | ---: |
| Springer Nature: Nature 및 Springer 저널 | 6 | 97 | 68 | 29 |
| Wiley | 3 | 14 | 9 | 5 |
| Elsevier | 3 | 12 | 0 | 12 |
| 위 세 출판사 합계 | 12 | 123 | 77 | 46 |
| 다른 출처를 포함한 전체 수집본 | 22 | 167 | 117 | 50 |

출판사별 집계는 저장된 데이터에서 재계산하였으며, 수집 완료와 사람 검증 완료는 구분합니다. 전체 사람 검증 완료는 0개입니다. 본문에 사용하는 데이터 범위는 전체 수집본인지 세 출판사 부분집합인지 일관되게 명시해야 합니다. 현재 피처 비교의 117개 입력은 다른 출처를 포함한 전체 수집본의 임시 후보이며, 세 출판사만의 분석 결과가 아닙니다.

## English manuscript text

### Literature identification and eligibility criteria

A targeted literature search was conducted to identify experimental studies of corrosion in rare-earth-containing bulk ferrous alloys and the corresponding control materials investigated within the same studies. The search and acquisition workflow used Elsevier Scopus and ScienceDirect search services, Springer Nature metadata and open-access services, and DOI-based retrieval of Wiley articles. Publisher-page searches and follow-up searches using article titles and DOIs supplemented API-based discovery. Search terms combined rare-earth identifiers (e.g., cerium, lanthanum, yttrium, and “rare earth”) with ferrous-material and corrosion terms (e.g., steel, stainless steel, corrosion, polarization, current density, and Tafel). Search queries were adapted to the syntax of each service. Searches included both older publications and recent studies; a single publication-year interval was not imposed across all queries. The latest collection update was performed on 15 October 2026.

Candidate records were consolidated using normalized DOIs to identify repeated bibliographic records. Titles and abstracts were used to prioritize potentially relevant articles, followed by examination of accessible experimental sections, tables, and figures. Studies were eligible for measurement extraction when they investigated rare-earth additions to bulk ferrous materials or within-study controls and explicitly reported corrosion current density, together with an identifiable sample and measurement condition. Studies limited to rare-earth-containing coatings, rare-earth additions to an electrolyte as corrosion inhibitors, non-ferrous alloys, or review-derived secondary measurements were excluded. Passive current density, corrosion potential, local scanning-electrode current, electrochemical impedance parameters, and weight-loss-derived corrosion rates were not substituted for corrosion current density. This was a targeted, iterative data-acquisition procedure rather than an exhaustive systematic review.

### Acquisition of article content

Bibliographic discovery and full-text acquisition were treated as separate steps. For Springer Nature publications, accessible original content was acquired using the open-access JATS service or official publisher PDF links. Wiley PDFs were retrieved using the Wiley Text and Data Mining API with a client token after identification of the article DOI. Elsevier search services returned bibliographic records; however, the Article Retrieval API remained inaccessible with an HTTP 403 authentication/configuration response in the execution environment. Consequently, Elsevier full-text acquisition was not considered successful solely on the basis of a successful metadata search.

Where available, DOI-matched public repository copies were obtained as alternative article sources. For an Elsevier iScience article, a DOI-verified full-text XML copy was obtained from Europe PMC. This article did not contribute numerical corrosion-current-density records because the relevant accessible figure did not display explicit numerical values suitable for the adopted extraction procedure. Separately, twelve candidate measurements from three Elsevier articles were transcribed from numerical tables exposed in search results for the publisher's own article pages. These records were labeled as publisher-search-excerpt evidence and withheld from the provisional modeling dataset pending full-source verification. Repository copies, publisher PDFs/XML, and publisher-search excerpts were recorded as distinct evidence types.

### LLM-assisted extraction and provenance tracking

Article content was converted into source-addressable evidence blocks. XML content was represented using paragraph and table identifiers, whereas PDF text was associated with page-level locators. A large language model, OpenAI GPT-6.1 Sol (API model identifier: `gpt-6.1-sol`), was accessed through the Responses API to assist measurement extraction and contextual-variable extraction. The model identifier was confirmed from locally stored API responses. Task-specific instructions and a strict JSON schema constrained the outputs to predefined measurement, composition, test-condition, and provenance fields. No project-specific model fine-tuning was performed. The code did not explicitly set temperature, top-p, or a generation seed; therefore, deterministic generation was not assumed.

For each extracted measurement, the requested information included sample identity, corrosion current density in its reported unit, alloy composition, rare-earth identity and content, test environment, and source references. Composition and test-condition locators were requested separately from the locator supporting the corrosion-current-density value. Additional contextual information, including heat-treatment history, material state, exposure time, and electrochemical testing conditions, was extracted in a separate evidence-constrained step without modifying the previously extracted target values. Missing, censored, ranged, or ambiguous numerical measurements were retained as missing values rather than replaced with estimated point values. Unquantified descriptions such as “room temperature” and “neutral solution” were not assigned numerical temperature or pH values.

LLM-derived target evidence was checked against the supplied source blocks by matching quoted text after whitespace normalization. When an evidence quotation comprised separate lines, each fragment was required to occur within the cited block; separated fragments were not represented as a single continuous quotation. Invalid locators, unsupported target quotations, nonpositive corrosion current densities, and duplicate sample-condition identities caused extraction validation to fail. These automated checks established source traceability but did not establish the scientific correctness of sample-to-condition attribution or replace expert review.

The dataset also included agent-assisted transcription of numerical table entries and explicitly printed numerical annotations within figures. Values inferred solely from curve positions, bar heights, or image coordinates were not included. For one Springer Nature study contributing 60 data points, printed figure annotations were additionally read using the same Sol model with image input and compared with the transcribed values. This constituted an automated cross-check using the same model family, not independent human validation. Extraction mode and evidence type were retained for each available record or source-level extraction run; not all collected measurements were produced by text-only LLM extraction.

### Data harmonization, duplicate handling, and quality control

A measurement record represented a distinct reported alloy–processing–environment–measurement condition. Reported means were not expanded into separate observations on the basis of the stated number of experimental repeats. Measurements repeated in tables and figures or under multiple headings were checked for duplication and retained once when they represented the same reported condition. For example, repeated untreated control values in the S31254 heat-treatment study were collapsed before aggregation.

Corrosion current density was harmonized to A cm⁻² using factors of 10⁻³ for mA cm⁻² and 10⁻⁶ for μA cm⁻², with any explicitly reported table multiplier retained during conversion. Alloy compositions were recorded in wt.% and rare-earth contents in mass ppm, where an unambiguous wt.% value could be converted using 1 wt.% = 10,000 ppm. Nominal additions, feedstock compositions, intermediate processing-stage compositions, and measured final-material compositions were distinguished. Unreported elemental contents were not interpreted as zero. NaCl weight percentage was not converted to molar chloride concentration without sufficient supporting information. Heat-treatment duration, corrosion exposure time, and open-circuit-potential stabilization time were treated as separate quantities.

Records with conflicting source values or sample attribution, insufficient reported composition, incomplete full-source evidence, or unresolved correspondence between the composition measurement stage and the tested specimen were assigned explicit hold reasons. The aggregation procedure excluded held records from the provisional modeling input. Source DOI, source locator, available quotation or transcription evidence, original unit, extraction method, and review status were retained; source paths and available SHA-256 hashes supported traceability. All collected measurements remained labeled as pending human review. The terms “verified dataset” and “human-validated measurements” are therefore not applicable to the current collection.

### Current dataset status and feature preparation

At the collection cutoff, the combined dataset contained 167 candidate experimental data points from 22 studies, including sources beyond the three primary publishers. The Springer Nature, Wiley, and Elsevier subset contained 123 data points from 12 studies. Following the implemented quality holds, 117 data points from 16 studies were retained as provisional modeling candidates across the full collection; these were not human-verified observations. The remaining 50 data points were held for further review. Collection counts were distinguished from modeling-eligible and human-verified counts.

For exploratory prediction, the target was defined as log₁₀[i_corr/(A cm⁻²)]. A corrosion-focused profile comprised 28 candidate descriptors representing composition, rare-earth content, environment, exposure and measurement conditions, and processing history, including input-only logarithmic transformations and composition interaction terms. Features were selected within each training fold using a reporting fraction of at least 50%, nonconstant training values, and availability in at least two training studies. Numerical imputation, missingness indicators, scaling, and categorical encoding were fitted using training data only. Study identifiers, source text, corrosion current density, and electrochemical outcome variables directly related to the target were excluded from the predictor set. Feature comparison was exploratory and did not establish final predictive or active-learning performance.

## 한국어 본문 초안

### 문헌 검색 및 데이터 선정

희토류 첨가 철계 합금의 부식전류밀도 예측을 위한 문헌 데이터셋을 구축하기 위해 Elsevier, Springer Nature 및 Wiley의 논문을 중심으로 표적 문헌 검색을 수행하였다. Elsevier의 Scopus 및 ScienceDirect 검색 서비스와 Springer Nature의 메타데이터·오픈액세스 서비스를 활용하였으며, 출판사 페이지 및 논문 제목·DOI를 이용한 후속 검색으로 후보 문헌을 보완하였다. Wiley 논문은 확인된 DOI를 기반으로 공식 Text and Data Mining API를 통해 원문 PDF를 확보하였다. 검색어는 cerium, lanthanum, yttrium, rare earth와 steel, stainless steel, corrosion, polarization, current density 및 Tafel 등을 조합하였으며, 서비스별 검색 문법에 맞게 적용하였다. 최신 수집 갱신일은 2026년 10월 15일이다. 본 절차는 데이터 확보를 위한 반복적 표적 검색으로 수행되었으며, 모든 관련 문헌을 포괄하는 체계적 문헌고찰로 간주하지 않았다.

중복 문헌은 정규화된 DOI를 기준으로 식별하였다. 희토류가 벌크 철계 합금에 첨가된 실험 연구와 동일 논문의 대조군을 포함하였으며, 시료 및 시험 조건에 연결할 수 있는 명시적 부식전류밀도 수치를 수집하였다. 희토류 코팅, 용액 내 부식억제제로 투입된 희토류, 비철 합금 및 리뷰 논문의 재인용 데이터는 제외하였다. 부동태 전류밀도, 부식전위, 국부 전류, 임피던스 파라미터 및 중량감소 기반 부식속도는 부식전류밀도로 대체하지 않았다.

### 원문 확보 및 LLM 보조 추출

Springer Nature 논문은 이용 가능한 공식 JATS XML 또는 출판사 PDF로 확보하였으며, Wiley 논문은 TDM API로 확보하였다. Elsevier는 검색 API와 원문 API의 접근 상태를 구분하였다. Article Retrieval API에서 HTTP 403이 지속되어 원문 API 접근이 성공한 것으로 처리하지 않았으며, 가능한 경우 DOI가 일치하는 공개 저장소의 원문 사본을 확인하였다. 출판사 검색 결과에 노출된 수치표에서 확보한 Elsevier 데이터는 전체 원문과 대조하기 전까지 별도 보류하였다.

확보한 문서는 문단·표 또는 PDF 페이지 단위의 출처 식별자를 갖는 근거 블록으로 변환하였다. OpenAI Responses API를 통해 **GPT-6.1 Sol(`gpt-6.1-sol`)**을 사용하였으며, 지정된 JSON 스키마에 따라 시료, 합금 조성, 희토류 함량, 부식 시험 조건, 부식전류밀도 및 출처 근거를 구조화하여 추출하였다. 사용 모델 식별자는 저장된 API 응답에서 확인하였다. 별도의 프로젝트 전용 미세조정은 수행하지 않았다. 생성 temperature, top-p 및 seed는 코드에서 명시적으로 지정하지 않았다.

모델에는 원문에 없는 값을 추정하지 않고 결측으로 유지하도록 지시하였다. 추출된 부식전류밀도의 근거 문구가 인용된 원문 블록에 존재하는지 자동 확인하였으며, 잘못된 출처 식별자, 근거 문구 불일치, 비양의 목표값 및 중복 시료·조건은 오류로 처리하였다. 열처리·재료 상태 등 추가 문맥 변수는 별도 추출 단계에서 필드별 근거와 함께 보완하였고, 기존 목표값은 변경하지 않았다. 수치표와 그림에 인쇄된 숫자의 에이전트 보조 전사도 병행하였으나, 그래프 좌표나 막대 높이만으로 값을 추정하지 않았다. 일부 그림의 인쇄값은 동일 Sol 모델의 이미지 입력으로 교차 확인하였으며, 이를 독립적인 사람 검증으로 간주하지 않았다.

### 단위 표준화 및 품질 관리

각 실험 데이터 포인트는 보고된 합금·처리·환경·측정 조건의 조합으로 정의하였다. 반복 측정의 평균값을 반복 횟수만큼 복제하지 않았으며, 표와 그림 또는 여러 표제에 재수록된 동일 조건의 결과는 중복 집계하지 않았다. 부식전류밀도는 원문 배율을 반영하여 A/cm²로 통일하였고, 조성은 wt.%, 희토류 함량은 질량 ppm으로 기록하였다. 명목 첨가량과 최종 재료의 실제 함량을 구분하였으며, 미보고 조성은 0으로 대체하지 않았다. 열처리 시간, 부식 노출 시간 및 OCP 안정화 시간도 구분하였다. 밀도 등의 근거 없이 NaCl wt.%를 Cl⁻ mol/L로 변환하지 않았다.

출처 간 수치·시료 불일치, 조성 정보 부족, 원문 전체 미확보 및 조성 측정 단계와 시험 시편 간 대응이 불분명한 자료에는 보류 사유를 부여하여 임시 모델 입력에서 제외하였다. DOI, 원문 위치, 근거 문구 또는 전사 기록, 원래 단위, 추출 방법 및 검토 상태를 보존하였다. 현재 전체 수집본은 22편의 167개 데이터 포인트이며, 이 중 세 출판사 부분집합은 12편의 123개이다. 다른 출처를 포함한 전체 수집본에서 117개를 임시 분석 후보로 분류하고 50개를 보류하였다. 모든 자료는 사람 검토 전인 `pending` 상태이므로, 사람에 의해 검증 완료된 데이터셋으로 기술하지 않았다.

## Supplementary Methods에 넣을 검색식과 구현 정보

다음은 저장된 실제 검색 기록의 예시입니다. 모든 서비스에 아래 검색식을 동일하게 적용했다고 기술하지 않습니다.

```text
Elsevier / Scopus:
TITLE-ABS-KEY((cerium OR lanthanum OR "rare earth")
 AND (steel OR steels)
 AND corrosion
 AND (addition OR microalloying OR inclusion OR alloying))

Elsevier / Scopus:
TITLE-ABS-KEY((cerium OR lanthanum OR "rare earth")
 AND (steel OR steels)
 AND (polarization OR "current density" OR Tafel))

Springer metadata:
cerium steel corrosion

Springer open access:
"rare earth" "steel" "corrosion"

Additional recorded keyword searches:
cerium corrosion steel microalloying
lanthanum corrosion steel microalloying
"rare earth" corrosion steel microalloying
yttrium corrosion steel
cerium corrosion stainless
```

초기 API 검색 묶음에는 150개 검색 레코드에서 DOI 중복 9개를 병합하여 141개 후보를 만든 기록이 있습니다. 이후 추가 검색과 원문 확보가 이루어졌으므로 **141개를 최종 전체 검색 문헌 수 또는 최종 스크리닝 분모로 사용하지 않습니다.** PRISMA 흐름도가 필요하면 모든 후속 검색 결과와 제외 사유를 먼저 통합해야 합니다.

| 항목 | 실제 설정·기록 |
| --- | --- |
| LLM API / 모델 | OpenAI Responses API / `gpt-6.1-sol` |
| 텍스트 측정 추출 | strict JSON schema, `max_output_tokens=6000` |
| 추가 문맥 추출 | strict JSON schema, `max_output_tokens=9000`, 필드별 근거 |
| 그림 인쇄값 확인 | 동일 모델 이미지 입력, high detail, `max_output_tokens=4000` |
| temperature / top-p / seed | 명시적으로 설정하지 않음 |
| 모델 응답 | 로컬에 저장하여 재사용·재검증. API 요청은 `store=False` |
| PDF 처리 | pypdf, 필요한 경우 PyMuPDF 대체 판독 |
| 주요 데이터 처리·모델링 | Python, pandas, NumPy, scikit-learn |
| 프롬프트 및 검증 구현 | 아래 로컬 파일 참조 |

- [측정 추출 프롬프트](extraction_prompt.md), [추가 문맥 추출 지침](context_extraction.md)
- [측정 추출 및 단위 변환 구현](../ree_research/extraction.py), [문맥 추출 구현](../ree_research/context.py)
- [API 검색 구현](../ree_research/mining.py), [공개 원문 사본 확보 구현](../ree_research/open_fulltext.py)
- [Wiley·Springer PDF 수집](../scripts/collect_publisher_round2.py), [Elsevier 표 전사](../scripts/build_elsevier_expansion.py)
- [그림 인쇄값 자동 확인](../scripts/check_springer_annotations.py), [품질 보류·집계](../scripts/assemble_extraction_pilot.py)
- [전체 집계](../data/processed/pilot100/current_status.json), [Nature·Wiley 논문별 집계](../data/processed/nature_wiley/summary.json)
- [원문 확보의 실제 한계와 논문별 추가 내역](elsevier_expansion.md), [피처 설계·개발 검증](feature_design_v3.md)

## 투고 전 수정할 부분

사람 검토가 완료되면 검토자 수, 독립 검토 여부, 의견 불일치 해결 절차, 최종 포함·제외 수를 실제 수행 기록에 따라 추가합니다. 아직 하지 않은 이중 독립 검토나 저자 확인을 완료한 것으로 서술하지 않습니다. 최종 연구 범위, 전체 검색 로그, 최종 데이터셋 버전, 실행 환경 버전 및 최종 모델·Active Learning 프로토콜을 확정한 뒤 해당 내용을 본문·보충자료에 함께 고정합니다.
