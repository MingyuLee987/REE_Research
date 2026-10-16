"""Export credential-free, actually persisted search expressions for Supplementary Methods.

No new network calls. Result counts are per saved query, never a PRISMA denominator.
Filesystem timestamps are deliberately not used as search dates.
"""
import hashlib
import json
from pathlib import Path
from ree_research.screening import normalize_doi

ROOT=Path(__file__).resolve().parents[1]


def main():
    groups={}
    for path in sorted((ROOT/'data/raw').rglob('*.json')):
        try:
            saved=json.loads(path.read_text(encoding='utf-8-sig'))
        except (ValueError,OSError):
            continue
        if not isinstance(saved,dict):continue
        body=saved.get('response',saved)
        if not isinstance(body,dict):continue
        query=saved.get('query')
        if not isinstance(query,str):query=body.get('query')
        if 'search-results' in body:
            if not isinstance(query,str):continue
            provider='Elsevier Scopus'
            results=body['search-results']
            entries=[e for e in results.get('entry',[]) if isinstance(e,dict) and not e.get('error')]
            total=results.get('opensearch:totalResults')
            start=results.get('opensearch:startIndex')
            size=results.get('opensearch:itemsPerPage')
        elif isinstance(body.get('request'),dict) and 'queryString' in body['request']:
            provider='Europe PMC'
            query=body['request']['queryString']
            entries=body.get('resultList',{}).get('result',[])
            total=body.get('hitCount');start=body['request'].get('cursorMark');size=body['request'].get('pageSize')
        elif isinstance(query,str) and isinstance(body.get('records'),list):
            provider={'springer-meta':'Springer Nature Metadata','springer-oa':'Springer Nature Open Access'}.get(saved.get('provider'))
            if not provider:
                if 'springer_round' in path.parts:provider='Springer Nature Open Access'
                else:provider='Springer Nature (service not recovered)'
            entries=body['records']
            result=body.get('result',[])
            result=result[0] if isinstance(result,list) and result else result
            result=result if isinstance(result,dict) else {}
            total=result.get('total');start=result.get('start');size=result.get('recordsDisplayed')
        else:continue
        key=(provider,query)
        if key not in groups:groups[key]={'provider':provider,'query':query,'responses':[],'retrieved_dois':set()}
        row=groups[key]
        row['responses'].append(dict(file=path.relative_to(ROOT).as_posix(),
            sha256=hashlib.sha256(path.read_bytes()).hexdigest(),reported_total=total,
            start_or_cursor=start,reported_page_size=size,records_in_saved_response=len(entries),
            exact_search_timestamp='not_recorded_in_payload'))
        for entry in entries:
            doi=normalize_doi(entry.get('doi',entry.get('prism:doi','')))
            if doi:row['retrieved_dois'].add(doi)
    rows=[]
    for i,((provider,query),row) in enumerate(sorted(groups.items()),1):
        row['search_id']=f'S{i:02d}'
        row['distinct_retrieved_dois_for_this_query']=len(row.pop('retrieved_dois'))
        row['saved_response_count']=len(row['responses'])
        rows.append(row)
    payload=dict(audit_date='2026-10-16',scope='Persisted structured API responses with recoverable query expressions only',
        exclusions='Not a complete ledger of publisher-page, title/DOI, or web searches; raw metadata without stored query is excluded.',
        warning='Reported hit totals overlap; some queries only retrieved a first page. Do not sum totals or use as PRISMA counts.',
        distinct_provider_query_pairs=len(rows),saved_response_files=sum(r['saved_response_count'] for r in rows),queries=rows)
    (ROOT/'docs/search_query_log.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    lines=['# 저장된 실제 API 검색식 목록','',
        '2026-10-16 로컬 응답 감사. 같은 서비스·동일 문자열의 페이지 응답은 한 검색식으로 묶었습니다.',
        '조회한 응답만 포함합니다. 전체 적합 문헌 수, 전체 웹 검색 목록 또는 PRISMA 집계가 아닙니다.',
        '정확한 개별 요청 시각은 응답에 없으면 미기록으로 유지했습니다. 파일 수정 시각으로 대체하지 않았습니다.','']
    for row in rows:
        lines += [f"## {row['search_id']} — {row['provider']}",'','```text',row['query'],'```','',
            f"저장 응답 {row['saved_response_count']}개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI {row['distinct_retrieved_dois_for_this_query']}개.",'']
        for r in row['responses']:
            lines.append(f"- `{r['file']}`: API 전체 hit={r['reported_total']}; 시작점={r['start_or_cursor']}; 실제 저장 레코드={r['records_in_saved_response']}")
        lines.append('')
    (ROOT/'docs/search_query_log.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in payload.items() if k!='queries'},ensure_ascii=False))


if __name__=='__main__':main()
