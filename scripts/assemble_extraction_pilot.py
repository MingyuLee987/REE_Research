"""Assemble provisional extractions/transcriptions with quality holds, no padding."""
import json
import re
from pathlib import Path
import pandas as pd
from ree_research.schema import COMPOSITION, prepare

ROOT = Path(__file__).resolve().parents[1]


def quality_hold_reasons(row):
    reasons = []
    explicit_hold = row.get('quality_hold_reason', '')
    if pd.notna(explicit_hold) and str(explicit_hold).strip():
        reasons.append(str(explicit_hold).strip())
    if re.search(r'conflict|inconsisten|contradict', str(row.get('notes', '')), re.I):
        reasons.append('source_inconsistency_requires_review')
    if row['reported_composition_count'] < 3:
        reasons.append('fewer_than_3_reported_composition_values')
    return ';'.join(reasons)


def main():
    sources, frames, usage = [], [], []
    for run_file in sorted((ROOT / 'data/processed/extractions').glob('*/run.json')):
        run = json.loads(run_file.read_text(encoding='utf-8'))
        if run.get('requires_annotation_check'):
            check_path = run_file.parent / 'vision_check_summary.json'
            if not check_path.exists():
                raise ValueError('Printed annotation check missing; do not merge')
            checks = json.loads(check_path.read_text(encoding='utf-8'))
            if len(checks) != 3 or not all(c.get('all_match') for c in checks):
                raise ValueError('Printed annotation check failed; review source before merge')
            run['usage'] = {key: sum(c.get('usage', {}).get(key, 0) for c in checks)
                            for key in ['input_tokens', 'output_tokens', 'total_tokens']}
        sources.append({'source': run_file.parent.name, 'rows': run['rows'],
                        'method': run.get('method', 'llm_source_extraction')})
        usage.append(run.get('usage', {}))
        if not run['rows']:
            continue
        frame = pd.read_csv(run_file.parent / 'pending_measurements.csv')
        frame['extraction_source'] = run_file.parent.name
        frames.append(frame)
    if not frames:
        raise ValueError('No extracted measurements available')
    raw = pd.concat(frames, ignore_index=True)
    if raw.record_id.duplicated().any():
        raise ValueError('Duplicate record IDs; review rather than silently discard')
    # Never combine older table transcriptions and LLM outputs as independent data.
    raw['reported_composition_count'] = raw.reindex(columns=COMPOSITION).notna().sum(axis=1)
    raw['hold_reason'] = ''
    for idx, row in raw.iterrows():
        raw.loc[idx, 'hold_reason'] = quality_hold_reasons(row)
    provisional = raw[raw.hold_reason.eq('')].copy()
    # Physical checks only. Review statuses are deliberately NOT promoted to verified.
    prepare(provisional, allowed_review_statuses=('pending',))
    out = ROOT / 'data/processed/pilot100'
    out.mkdir(parents=True, exist_ok=True)
    raw.to_csv(out / 'llm_pending_all.csv', index=False)
    provisional.to_csv(out / 'provisional_for_model.csv', index=False)
    raw[raw.hold_reason.ne('')].to_csv(out / 'held_for_review.csv', index=False)
    status = {'scope': 'REE bulk ferrous alloys and controls from the same studies only',
              'target_rows': 300, 'extracted_rows': len(raw), 'extracted_papers': raw.paper_id.nunique(),
              'provisional_rows': len(provisional), 'provisional_papers': provisional.paper_id.nunique(),
              'held_rows': len(raw) - len(provisional), 'human_verified_rows': 0,
              'shortfall_to_100_extracted': max(0,100-len(raw)), 'generation_access': 'working',
              'shortfall_to_target': max(0,300-len(raw)),
              'sources': sources,
              'tokens': {key: sum(u.get(key,0) for u in usage) for key in ['input_tokens','output_tokens','total_tokens']},
              'status': 'provisional_collection_incomplete' if len(raw)<300 else 'provisional_collection_target_met_not_human_verified'}
    (out / 'current_status.json').write_text(json.dumps(status, indent=2), encoding='utf-8')
    lines=['# Sol 추출 검토 목록', '', '모든 행은 pending입니다. 아래 값은 인간 검토 완료 자료가 아닙니다.', '',
           '| 논문 DOI | 시료 | i_corr (A/cm²) | 원문 위치 | 보류 사유 |', '| --- | --- | ---: | --- | --- |']
    for _, row in raw.iterrows():
        lines.append(f"| [{row.doi}](https://doi.org/{row.doi}) | {str(row.sample_id).replace('|','/')} | {row.icorr_A_cm2:.6g} | {row.source_locator} | {row.hold_reason or '수치·단위·시료 연결 검토 필요'} |")
    (out / 'review_queue.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(json.dumps(status, indent=2))


if __name__ == '__main__':
    main()
