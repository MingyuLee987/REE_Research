# 앞으로 할 실험: 기본 합금에 Ce 첨가

사용자가 제공한 POSEIDON600 기본 조성과 제조 계획을 바탕으로 만든 실험 준비 폴더입니다. Ce 300 ppm 첨가는 잠정 계획이며 아직 실제 실험 결과는 없습니다.

| 확인할 내용 | 파일 |
| --- | --- |
| 비교할 Ce 함량과 질량 계산 | [candidate_queue.csv](candidate_queue.csv) |
| 실제 측정 결과를 입력할 표 | [experimental_results_pending.csv](experimental_results_pending.csv) |
| 실제 실험값이 들어왔는지 | [experimental_feedback_status.json](experimental_feedback_status.json) |
| 사용자가 준 엑셀에서 읽은 원래 셀 | [workbook_cells.json](workbook_cells.json) |

입력표의 `current_initial_batch=True`가 현재 초기 실험 계획입니다. `icorr_A_cm2`에는 실제 부식 전류밀도, `measured_Ce_ppm`에는 실제 분석한 잔류 Ce를 기록합니다. 계산한 예측값을 실험값 칸에 넣지 마세요.

이 폴더의 `report.json`에 있는 문헌 모델 점수는 중국어 논문 제외 전의 참고 계산입니다. 현재 제외본 모델 점수는 옆의 `01_현재분석_중국어논문제외` 폴더를 확인하세요.

[공정·함량·입력 방법 상세 설명](../../02_연구설명과논문작성/casting_ce_active_learning_20261019.md).
