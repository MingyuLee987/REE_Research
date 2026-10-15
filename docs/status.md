# 현재 진행 현황

> **최신 수집: 전체 27편·189개 실험 데이터 포인트.** 임시 후보 135개, 보류 54개이며 모두 사람 검토 전인 `pending`입니다.
>
> API 추가 검색과 원문 확보로 기존 167개에서 22개를 추가했습니다. 목표 300개까지는 111개 부족합니다. Elsevier 그림의 전류 표기 60개는 단위·전극 면적·조건 대응 미확정으로 합치지 않았습니다. Springer Nature·Wiley 부분집합은 10편·121개입니다. 기존 모델 성능은 이전 데이터의 실행 이력입니다.

[추가 논문·단위·재현 방법](collection_300.md)


> **피처 수정 v3:** 기본 프로파일을 `corrosion`으로 변경했습니다. 조성·환경·열처리와 파생 변수 28개 후보를 학습 데이터의 확보율에 따라 선택합니다. 14편·110개 개발 비교에서 논문별 MAE가 개선됐지만 전체 R² 개선은 확인하지 못했습니다. [피처 구성·실제 비교 결과](feature_design_v3.md)를 참고하세요. 아래 기존 피처·모델 수치는 이전 실행 이력입니다.







## 최신 상태 — 2026-10-15

- 범위: 희토류 첨가 철계 합금 연구와 같은 논문의 대조군만 포함.
- Sol 연결 및 실제 추출 완료: 19편 처리, 9편에서 33행. 7행 보류, 26행 임시 분석, 모든 행은 사람 검토 전 pending.
- 임시 모델 비교: 내부 CV로 SVR 선택, 별도 테스트 2편·7행에서 R²=-1.271. 100행 및 R² 0.8 목표는 미달.
- AI 부식 원 논문을 참고한 v2 설계 추가: core 14개, extended 21개, literature 44개 후보. 열처리·재료/표면 상태·노출 이력·시험 프로토콜·추가 조성을 수집.
- `ree enrich-context`로 필드별 근거를 가진 문맥 추출을 지원. 신규 컬럼을 만들었다는 것과 실제 확보/성능 개선은 구분.
- 대표 3편·12행에 문맥 값 118개 보강. 타깃과 pending 상태는 유지. 보강 입력은 `data/processed/context_v2/provisional_enriched.csv`.
- v2는 기존 테스트 논문을 개발 평가에서 제외하고, 개발 CV와 새로운 최종 테스트를 구분함.
- 제외 후 개발 19행·7편의 내부 CV에서는 Ridge 선택, 평균 R²=0.2672. 최종 테스트 재평가는 하지 않았으며 R² 0.8 달성 결과가 아님.
- 자동 테스트 16개 통과.
- 상세 근거: [문헌 기반 피처 설계](literature_feature_design.md), [100행 진행 기록](pilot100.md).

## 아래는 초기 실행 기록

2026-10-15 (Asia/Seoul)

- Elsevier Scopus, Springer Meta, Springer OA 키를 각각 실제 3건 검색 요청으로 확인. 세 요청 모두 HTTP 200 및 결과 레코드 3건 반환.
- 검색어: Elsevier `TITLE-ABS-KEY(cerium AND corrosion AND steel)`, Springer `cerium corrosion steel`.
- 검색 응답은 Git 제외 경로 `data/raw/`에 저장. 검색은 연결 확인용이며 관련 문헌 선별/중복 제거는 미완료. 검색 결과 수는 학습 가능 측정 데이터 수가 아님.
- 합성 데이터: 15개 가상 논문 × 8행, 총 120행. 19개 피처 검증 후 Ridge/SVR/GPR × random/uncertainty × 3시드 비교를 실행.
- 합성 출력: `outputs/demo/`. 실제 측정 결과, 문헌 근거 또는 AL 우월성의 증거로 사용 금지.
- 자동 검증: 입력 검토 상태, pool 정답 변경에 대한 예측/선택 점수 불변성, 논문 단위 테스트 격리와 라벨 예산.

다음 데이터 단계는 철계 합금 범위로 후보 논문을 선별하고, 원문 및 표를 확보하여 `data/measurements_template.csv`에 원문 근거와 함께 기록하는 작업이다. 자동 LLM 추출은 공급자/모델이 미선정되어 연결하지 않았다. 추출 프롬프트는 `docs/extraction_prompt.md`에 준비되어 있다.

## 후속 진행

- `data/raw/discovery/`에 검색 6개 응답, 총 150개 레코드 저장.
- `ree screen`으로 DOI 정규화 및 중복 제거: 141개 후보, 9개 중복 병합.
- `data/processed/literature/candidates.md` 및 `candidates.json` 생성. 모든 후보는 pending_manual_review이며 측정값은 미추출.
- 제목/초록 키워드 점수는 검토 순서에만 사용. 적합 판정이나 데이터 품질 검증으로 사용하지 않음.
- Elsevier 공식 원문 API로 DOI `10.1016/j.jmrt.2025.11.079` 요청: HTTP 403. 원문 미확보. 검색 권한과 원문 권한을 구분하여 기록.
- 추가 명령: `ree screen`, `ree fetch-elsevier`. 원문 응답과 메타데이터 응답을 구분.
