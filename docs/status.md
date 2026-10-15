# 초기 실행 현황

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
