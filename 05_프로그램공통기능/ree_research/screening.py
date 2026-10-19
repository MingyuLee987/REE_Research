"""Deduplicate discovery results and prioritize manual screening, never labels."""
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote


def normalize_doi(value):
    value = unquote(str(value or '')).strip().lower()
    value = re.sub(r'^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)', '', value)
    return value if re.match(r'^10\.\d{4,9}/\S+$', value) else ''


def title_key(title):
    return re.sub(r'\W+', '', title.casefold())


def priority(title, abstract):
    text = (title + ' ' + abstract).lower()
    signals = {
        'ferrous': bool(re.search(r'\b(steel|steels|iron|ferrous)\b', text)),
        'rare_earth': bool(re.search(r'\b(cerium|lanthanum|rare[ -]earth|ce|la|yttrium|neodymium)\b', text)),
        'corrosion': bool(re.search(r'corrosion|electrochem|polarization|polarisation', text)),
        'measurement': bool(re.search(r'current density|i[_ ]?corr|tafel|potentiodynamic', text)),
        'bulk_alloy': bool(re.search(r'microalloy|alloying|addition|added|inclusion|duplex|stainless', text)),
        'surface_or_inhibitor': bool(re.search(r'coating|inhibitor|conversion film|surface treatment|deposition|oxide films', title.lower())),
        'other_material_or_hot_corrosion': bool(re.search(r'\b(magnesium|alumin(?:um|ium)|castable|slag|refractor)\b', title.lower())),
    }
    score = sum(int(signals[k]) for k in ['ferrous', 'rare_earth', 'corrosion', 'measurement', 'bulk_alloy'])
    score -= 2 * int(signals['surface_or_inhibitor']) + 2 * int(signals['other_material_or_hot_corrosion'])
    return score, signals


def records(path):
    saved = json.loads(path.read_text(encoding='utf-8'))
    provider, body = saved['provider'], saved['response']
    entries = body.get('search-results', {}).get('entry', []) if provider == 'elsevier' else body.get('records', [])
    for row in entries:
        if row.get('error'):
            continue
        title = row.get('dc:title', row.get('title', '')).strip()
        if not title:
            continue
        doi = normalize_doi(row.get('prism:doi', row.get('doi', '')))
        abstract = row.get('dc:description', row.get('abstract', '')) or ''
        if not isinstance(abstract, str):
            abstract = json.dumps(abstract, ensure_ascii=False)
        yield {'title': title, 'doi': doi, 'abstract': abstract,
               'publication_date': row.get('prism:coverDate', row.get('publicationDate', '')),
               'journal': row.get('prism:publicationName', row.get('publicationName', row.get('journalTitle', ''))),
               'sources': [{'provider': provider, 'file': str(path), 'query': saved.get('query', '')}]}


def screen(input_dir, output_dir):
    papers, seen = [], 0
    by_doi, by_title = {}, {}
    for path in sorted(Path(input_dir).glob('*.json')):
        for item in records(path):
            seen += 1
            doi, title = item['doi'], title_key(item['title'])
            # Distinct DOI records must not merge solely on a generic identical title.
            existing = by_doi.get(doi) if doi else None
            if existing is None:
                candidate = by_title.get(title)
                if candidate is not None and (not doi or not papers[candidate]['doi'] or doi == papers[candidate]['doi']):
                    existing = candidate
            if existing is None:
                existing = len(papers)
                papers.append(item)
            else:
                paper = papers[existing]
                paper['sources'].extend(item['sources'])
                if len(item['abstract']) > len(paper['abstract']):
                    paper['abstract'] = item['abstract']
                if not paper['doi']:
                    paper['doi'] = doi
            if doi:
                by_doi[doi] = existing
            by_title.setdefault(title, existing)
    for paper in papers:
        paper['paper_id'] = paper['doi'] or 'title-' + hashlib.sha256(title_key(paper['title']).encode()).hexdigest()[:16]
        paper['priority_score'], paper['signals'] = priority(paper['title'], paper['abstract'])
        paper['screen_status'] = 'pending_manual_review'
        paper['measurement_status'] = 'not_extracted'
    papers.sort(key=lambda p: (-p['priority_score'], p['paper_id']))
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    payload = {'records_seen': seen, 'unique_papers': len(papers), 'duplicates_merged': seen - len(papers), 'papers': papers}
    (out / 'candidates.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    lines = ['# 文献候補 / 문헌 후보 목록', '',
             f'검색 레코드 {seen}건 → 중복 제거 후 {len(papers)}편. 중복 {seen-len(papers)}건 병합.', '',
             '점수는 제목·초록 키워드 기반 검토 순서이며 연구 적합성 판정이 아닙니다. 모든 후보는 수동 검토 대기 상태입니다.',
             '특히 희토류가 합금에 첨가된 경우와 코팅/부식억제제에만 사용된 경우를 원문에서 구분해야 합니다.', '',
             '| 순서 | 우선 점수 | 제목 | DOI | 원문 확인할 내용 |', '| ---: | ---: | --- | --- | --- |']
    for index, paper in enumerate(papers, 1):
        flags = paper['signals']
        checks = ['합금 조성 및 실제 i_corr 표 확인']
        if flags['surface_or_inhibitor']:
            checks.append('희토류가 코팅/억제제에만 사용됐는지 확인')
        if flags['other_material_or_hot_corrosion']:
            checks.append('철계 합금·수용액 부식 범위인지 확인')
        doi = f"[원문](https://doi.org/{paper['doi']})" if paper['doi'] else '없음'
        safe_title = paper['title'].replace('|', '/').replace('\n', ' ')
        lines.append(f"| {index} | {paper['priority_score']} | {safe_title} | {doi} | {'; '.join(checks)} |")
    (out / 'candidates.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return payload
