# 현재 분석: 중국어 논문 제외

추가 탐색: [R² > 0.5 목표 결과](../../02_연구설명과논문작성/R2_0p5_추가탐색_20261019.md). 202개 설정의 주 평가와 조성별 보조 평가를 더 수행했지만 기준을 달성하지 못했습니다. 결과는 `추가모델탐색_R2목표/`에 보관합니다. 과거 영문 테스트 2편·7개의 재평가와 새 독립 테스트는 구분합니다.

본문이 중국어인 논문 11편·55개 기록을 제외한 분석입니다. 중국 소속 저자의 영문 논문은 남아 있습니다.

| 확인할 내용 | 파일 |
| --- | --- |
| 전체 제외본 33편·228개 기록 | [llm_pending_all_no_chinese.csv](llm_pending_all_no_chinese.csv) |
| 모델 적격 자료 17편·119개 | [provisional_for_model_no_chinese.csv](provisional_for_model_no_chinese.csv) |
| 실제 재학습 자료 15편·112개 | [development_enriched_no_chinese.csv](development_enriched_no_chinese.csv) |
| 어떤 논문을 왜 제외했는지 | [paper_language_decisions.csv](paper_language_decisions.csv) |
| 제외된 55개 기록의 보관본 | [excluded_chinese_records.csv](excluded_chinese_records.csv) |
| 모델 결과 요약, 분석 담당자용 | [report.json](report.json) |
| 모델이 예측한 값과 실제 값 | [development_predictions.csv](development_predictions.csv) |
| 재사용 가능한 학습 모델 | `selected_model.joblib` |
| 실행 중 출력된 진행 기록 | `실행기록.log` |

**현재 고정 테스트 R²는 없습니다.** 이전 테스트 3편이 모두 중국어 논문이라 제외됐습니다. 선택 모델은 Ridge이며 중첩 교차검증 R²는 −4.358로 일반화가 불안정합니다. 선택에 사용한 개발 점수 0.309만 최종 성능으로 보지 마세요.

[자세한 설명](../../02_연구설명과논문작성/no_chinese_20261019.md). `language_*.png`, `body_*.png`는 언어 판정을 위해 원문을 직접 확인한 이미지입니다. 삭제 대상 임시 그림이 아니라 제외 근거입니다.
