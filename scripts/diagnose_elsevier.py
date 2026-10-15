"""Compare Elsevier service authentication without exposing credentials."""
import concurrent.futures
import json
import os
from pathlib import Path
import re
import uuid
import xml.etree.ElementTree as ET
import requests
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]


def main():
    local = dotenv_values(ROOT/'.env')
    inherited = os.getenv('ELSEVIER_API_KEY')
    raw = local.get('ELSEVIER_API_KEY') or inherited or ''
    key = raw.strip()
    token = (local.get('ELSEVIER_INST_TOKEN') or os.getenv('ELSEVIER_INST_TOKEN') or '').strip()
    if not key:
        raise ValueError('ELSEVIER_API_KEY is missing')
    out = ROOT/'data/raw/elsevier_diagnostics'
    out.mkdir(parents=True, exist_ok=True)
    audit = {'key_present':True, 'key_matches_32_hex_format':bool(re.fullmatch(r'[0-9a-fA-F]{32}', key)),
             'trimmed_whitespace':raw != key,
             'inherited_key_present':bool(inherited),
             'inherited_differs_from_dotenv':bool(inherited and local.get('ELSEVIER_API_KEY') and inherited.strip()!=key),
             'institution_token_present':bool(token), 'key_source':'dotenv' if local.get('ELSEVIER_API_KEY') else 'process'}
    doi = '10.1016/j.corcom.2022.06.004'
    tasks = [
        ('scopus_search','/content/search/scopus',{'query':'DOI('+doi+')','count':1},'application/json',False),
        ('sciencedirect_search','/content/search/sciencedirect',{'query':doi,'count':1},'application/json',False),
        ('oa_doi_full_xml','/content/article/doi/'+doi,{'view':'FULL'},'text/xml',False),
        ('oa_doi_default_xml','/content/article/doi/'+doi,{},'text/xml',False),
        ('oa_doi_meta_json','/content/article/doi/'+doi,{'view':'META'},'application/json',False),
        ('oa_pii_full_xml','/content/article/pii/S2667266923000063',{'view':'FULL'},'text/xml',False),
        ('oa_query_key_full_xml','/content/article/doi/'+doi,{'view':'FULL'},'text/xml',True),
        ('subscription_full_xml','/content/article/doi/10.1016/j.jmrt.2025.11.079',{'view':'FULL'},'text/xml',False),
    ]

    def probe(task):
        name, path, params, accept, query_key = task
        request_id = str(uuid.uuid4())
        headers = {'Accept':accept,'X-ELS-ReqId':request_id}
        if query_key:
            params = params | {'apiKey':key}
        else:
            headers['X-ELS-APIKey'] = key
        if token:
            headers['X-ELS-Insttoken'] = token
        try:
            response = requests.get('https://api.elsevier.com'+path,params=params,headers=headers,timeout=40)
        except requests.RequestException:
            return {'test':name,'status':'network_error_redacted','request_id':request_id}
        text = response.text
        for secret in [key,token]:
            if secret:
                text = text.replace(secret,'[REDACTED]')
        (out/(name+'.txt')).write_text(text,encoding='utf-8')
        record = {'test':name,'http':response.status_code,'request_id':request_id,
                  'authentication_placement':'query' if query_key else 'X-ELS-APIKey',
                  'bearer_header_sent':False, 'institution_token_sent':bool(token)}
        if response.status_code != 200:
            try:
                root = ET.fromstring(text)
                record['error_code'] = next((n.text for n in root.iter() if n.tag.rsplit('}',1)[-1]=='statusCode'),None)
                record['error_message'] = next((n.text for n in root.iter() if n.tag.rsplit('}',1)[-1]=='statusText'),None)
            except ET.ParseError:
                try:
                    error = response.json().get('service-error',{}).get('status',{})
                    record['error_code'] = error.get('statusCode')
                    record['error_message'] = str(error.get('statusText','')).replace(key,'[REDACTED]')
                except ValueError:
                    record['error_code'] = 'unparsed_error'
        else:
            record['response_bytes'] = len(response.content)
        return record

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        audit['probes'] = list(pool.map(probe,tasks))
    (out/'report.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
    print(json.dumps(audit,indent=2))


if __name__ == '__main__':
    main()
