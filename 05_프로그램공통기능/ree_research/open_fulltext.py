"""Read public repository copies while keeping publisher API failures explicit."""
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import requests
from .mining import fetch_elsevier
from .screening import normalize_doi


def fetch_elsevier_open_copy(doi, output_dir):
    doi=normalize_doi(doi)
    if not doi or not doi.startswith('10.1016/'):
        raise ValueError('This reader requires an Elsevier 10.1016 DOI')
    out=Path(output_dir)
    try:
        result=fetch_elsevier(doi,out/'publisher_api')
        if result['status']=='original_text_present_requires_review':
            return result | {'transport':'elsevier_article_api'}
        api_status='metadata_only'
    except RuntimeError as error:
        api_status=str(error)
    # Never forward publisher credentials to a repository. No shared authenticated session.
    try:
        response=requests.get('https://www.ebi.ac.uk/europepmc/webservices/rest/search',
            params={'query':f'DOI:"{doi}"','format':'json','pageSize':10},timeout=40)
        response.raise_for_status()
        hits=response.json().get('resultList',{}).get('result',[])
        match=next((h for h in hits if normalize_doi(h.get('doi',''))==doi
                    and re.fullmatch(r'PMC\d+',h.get('pmcid',''))
                    and h.get('isOpenAccess')=='Y'),None)
        if not match:
            raise ValueError('No matching open repository copy found; publisher API access remains unresolved')
        pmcid=match['pmcid']
        url=f'https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML'
        response=requests.get(url,timeout=40)
        response.raise_for_status()
    except (requests.RequestException, ValueError) as error:
        if isinstance(error,ValueError):
            raise
        raise RuntimeError('Open repository request failed; no full text acquired') from None
    root=ET.fromstring(response.content)
    for node in root.iter():
        node.tag=node.tag.rsplit('}',1)[-1]
    identities=[normalize_doi(n.text or '') for n in root.findall('./front/article-meta/article-id')
                if n.get('pub-id-type')=='doi']
    body=root.find('body')
    if doi not in identities or body is None:
        raise ValueError('Repository DOI mismatch or missing article body; source rejected')
    blocks=[]
    nodes=[]
    front=root.find('./front/article-meta')
    if front is not None:
        nodes.extend(front.findall('./title-group/article-title'))
        nodes.extend(front.findall('abstract'))
    nodes.extend(body.iter('table-wrap'))
    table_paragraphs={id(p) for t in body.iter('table-wrap') for p in t.iter('p')}
    nodes.extend(p for p in body.iter('p') if id(p) not in table_paragraphs)
    for node in nodes:
        text=re.sub(r'\s+',' ',' '.join(node.itertext())).strip()
        if text:
            blocks.append({'locator':f'{node.tag}:{node.get("id",len(blocks))}',
                           'text':text,'xml':ET.tostring(node,encoding='unicode') if node.tag=='table-wrap' else None})
    if not blocks:
        raise ValueError('Repository body contains no extractable evidence')
    out.mkdir(parents=True,exist_ok=True)
    (out/'article.xml').write_bytes(response.content)
    (out/'blocks.json').write_text(json.dumps(blocks,ensure_ascii=False,indent=2),encoding='utf-8')
    metadata={'doi':doi,'pmcid':pmcid,'title':match.get('title'),
              'publisher':'Elsevier','retrieval_provider':'EuropePMC_open_fulltext',
              'source_url':url,'publisher_api_status':api_status}
    (out/'metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
    result=metadata | {'status':'open_repository_body_acquired_requires_review',
        'publisher_api_fixed':False,'body_characters':len(' '.join(body.itertext())),
        'evidence_blocks':len(blocks),'table_blocks':sum(b['locator'].startswith('table-wrap:') for b in blocks),
        'sha256':hashlib.sha256(response.content).hexdigest(),'measurement_status':'not_extracted'}
    (out/'retrieval.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    return result
