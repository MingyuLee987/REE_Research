"""Source-linked pilot measurements transcribed from acquired JATS tables.

These are pending human review and must not be used as verified training labels.
"""
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
rows = []


def add(pmcid, sample, composition, target, table, composition_table, environment, **extras):
    source = ROOT / 'data/raw/europepmc' / pmcid
    metadata = json.loads((source / 'metadata.json').read_text(encoding='utf-8'))
    blocks = json.loads((source / 'blocks.json').read_text(encoding='utf-8'))
    evidence = next(b['text'] for b in blocks if b['locator'] == 'table-wrap:' + table)
    row = dict(record_id=f'{pmcid}-{sample}', paper_id=metadata['doi'], doi=metadata['doi'],
               sample_id=sample, source_locator='table-wrap:' + table, evidence_quote=evidence,
               composition_locator=composition_table, review_status='pending', icorr_A_cm2=target,
               electrolyte_condition_cat=environment, source_url=f'https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/',
               source_file=str(source / 'article.xml'), extraction_method='source_table_transcription')
    row.update(composition)
    row.update(extras)
    rows.append(row)


def main():
    # 316L: measured composition table 2 and Jcorr (A/cm2) table 4.
    for sample, values, target in [
        ('1', [.015,.005,.006,.965,1.92,13.55,18.62,2,.352,0],3.07e-6),
        ('2', [.013,.004,.005,.962,1.92,13.57,18.71,2.05,.351,.0023],2.13e-6),
        ('3', [.016,.005,.006,.961,1.89,13.50,18.69,2.06,.354,.0082],1.71e-6),
    ]:
        comp=dict(zip(['C','S','P','Si','Mn','Ni','Cr','Mo','Cu'],values[:9]))
        add('PMC11720852',sample,comp,target,'materials-18-00069-t004','materials-18-00069-t002',
            'NaCl_3.5wtpct', RE_ppm=values[9]*10000,RE_element_cat='none' if sample=='1' else 'Ce',
            scan_rate_mV_s=.167,condition_locator='p:8')
    # Exclude 3 solution-inhibitor rows; retain only the zero-inhibitor conditions.
    for sample, si,mn,p,s,re_ppm,target in [
        ('0La',.29,1.24,.012,.012,0,4.04e-4),
        ('67La',.28,1.36,.0068,.002,67,2.52e-5),
        ('110La',.28,1.33,.007,.0081,110,1.91e-5),
        ('230La',.28,1.33,.0066,.0032,230,1.15e-5),
        ('310La',.28,1.34,.0069,.0076,310,6.65e-6),
    ]:
        add('PMC11433059',sample,dict(C=.16,Si=si,Mn=mn,P=p,S=s),target,
            'materials-17-04467-t002','materials-17-04467-t001','NaHSO3_0.01molL_no_added_La_salt',
            RE_ppm=re_ppm,RE_element_cat='none' if re_ppm==0 else 'La',scan_rate_mV_s=.5,
            ocp_stabilization_min=30,condition_locator='p:15',
            notes='Room temperature reported, numeric temperature left missing. pH from separate pure-La test not transferred.')
    for sample,re_ppm,target in [('0RE',0,1.893e-6),('0.03LaCe',360,1.829e-6),('0.3LaCe',3300,1.290e-6)]:
        add('PMC13304421',sample,dict(C=.05,Si=.50,Mn=1.50,Ni=1.0,Cu=.5,Mo=.25,Cr=2),target,
            'materials-19-02685-t002','materials-19-02685-t001',
            'NaCl_0.1wtpct+CaCl2_0.05wtpct+Na2SO4_0.05wtpct',RE_ppm=re_ppm,
            RE_element_cat='none' if re_ppm==0 else 'Ce+La',scan_rate_mV_s=.333,condition_locator='p:9;p:10',
            notes='P <=0.005 and S <=0.008 are censored; numeric values left missing. Use Table 2, not rounded abstract. Room temperature not converted to 25 C.')
    for sample,comp,target in [
        ('normal_without_RE',{},5.31e-5),
        ('Al_deoxidized',dict(C=.053,Si=.23,Mn=.13,P=.005,S=.003,Cu=.39,Cr=1.21,Ni=.31),4.60e-5),
        ('TiZr_deoxidized',dict(C=.050,Si=.22,Mn=.13,P=.005,S=.003,Cu=.43,Cr=1.22,Ni=.33),2.93e-5),
    ]:
        add('PMC6829360',sample,comp,target,'materials-12-03359-t002','materials-12-03359-t001',
            'NaCl_3.5wtpct',RE_ppm=0 if not comp else 50,RE_element_cat='none' if not comp else 'Ce+La',
            temperature_C=25,scan_rate_mV_s=.333,condition_locator='p:7',
            notes='Normal control composition not supplied in Table 1. 0.5 wt.% NaCl belongs to SVET/other tests, not these polarization values.')
    destination=ROOT / 'data/processed/pilot100'
    destination.mkdir(parents=True,exist_ok=True)
    frame=pd.DataFrame(rows)
    assert len(frame)==14 and frame.record_id.is_unique and frame.icorr_A_cm2.gt(0).all()
    frame.to_csv(destination / 'pending_measurements.csv',index=False)
    summary={'target_rows':100,'pending_rows':len(frame),'pending_papers':frame.paper_id.nunique(),
             'verified_rows':0,'gap_to_target_verified':100,'r2':None,
             'status':'blocked_before_training',
             'blockers':['OpenAI generation returned HTTP 429 credit_balance_exhausted',
                         'Only 14 directly table-transcribed rows; require human verification and more independent papers'],
             'source_scope':'ferrous RE bulk alloying and untreated controls; excludes inhibitor/coating rows'}
    (destination/'status.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    main()
