"""Publish truthful paper counts and keep targetless papers outside the master."""
import hashlib
import json
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/processed/expand50'


def main():
    master=pd.read_csv(ROOT/'data/processed/pilot100/llm_pending_all.csv',dtype=str)
    new=pd.read_csv(OUT/'new_observations.csv',dtype=str)
    held=pd.read_csv(ROOT/'data/processed/pilot100/held_for_review.csv',dtype=str)
    provisional=pd.read_csv(ROOT/'data/processed/pilot100/provisional_for_model.csv',dtype=str)
    assert len(master)==len(held)+len(provisional)
    assert set(master.record_id)==set(held.record_id)|set(provisional.record_id)
    assert not (set(held.record_id)&set(provisional.record_id))
    baseline=pd.read_csv(OUT/'baseline_before_append.csv',dtype=str)
    pd.testing.assert_frame_equal(baseline,master.iloc[:len(baseline)][baseline.columns].reset_index(drop=True))
    ledger=[]
    for doi,g in master.groupby('doi'):
        title=next((t for t in g.paper_title.dropna() if t.strip()),doi)
        ledger.append(dict(doi=doi,title=title,status='observations_in_master_pending_review',
                           records_in_master=len(g),normalized_targets=int(g.icorr_A_cm2.notna().sum()),
                           source_file=g.source_file.dropna().iloc[0],source_url='https://doi.org/'+doi))
    pending=[
      ('10.1038/s41529-022-00263-z','Unveiling nano-scaled chemical inhomogeneity impacts on corrosion of Ce-modified 2507 super-duplex stainless steels',
       'data/raw/round300/sources/springer_s41529-022-00263-z/article.pdf',
       'Main Table 1 is EIS resistance, not icorr. Supplementary PDF (17 pages) has structural/spectroscopic data and composition; no icorr table recovered.'),
      ('10.1038/s41529-026-00746-3','Enhancement mechanisms of Cr and RE on the corrosion resistance of HRB400 rebar in chloride-containing concrete pore solution',
       'data/raw/round300/sources/springer_s41529-026-00746-3/article.pdf',
       'Main Table 1 reports passive current, not corrosion current. Supplementary PDF (11 pages) provides surface chemistry/morphology; no icorr table recovered.'),
      ('10.3390/ma18030641','Enhanced Performance of Austenitic Oxide Dispersion-Strengthened 316L Steel: A Study on Y2O3 Reinforcement and Corrosion Behaviour',
       'data/raw/europepmc/PMC11818875/article.xml',
       'Table 4 has Ecorr, cathodic slope and breakdown potential; no explicit icorr. A future curve fit would be a derived model estimate, requiring fit-window validation.'),
      ('10.1007/s42243-020-00377-1','Effect of yttrium addition on microstructure, mechanical and corrosion properties of 20Cr13 martensitic stainless steel',
       'data/raw/target400/sources/y20cr13/article.pdf',
       'Table 3 gives Ecorr and Epit only. Figure 9 is a polarization curve, not direct icorr markers. Do not read its minimum as icorr.'),
      ('10.1007/s11665-019-04112-0','Effects of Ce Addition on Grain Boundary Character Distribution, Corrosion Behavior and Impact Toughness of AISI 204Cu Stainless Steel',
       'data/raw/springer_round2/s11665-019-04112-0/article.pdf',
       'Original PDF acquired and screened; no explicit icorr table recovered. Corrosion evidence must not be relabeled as an icorr record.'),
      ('10.3390/ma18112443','Effect of the Rare Earth Element Cerium on the Corrosion Resistance of Steel for an Offshore Platform in a Simulated Marine Atmospheric Environment',
       'data/raw/add30_20261016/mdpi2443/article.pdf',
       'Figure 10 has polarization curves; no tabulated icorr. Page 13 explicitly describes dissolved-oxygen diffusion control. Arbitrary linear Tafel extrapolation is not accepted. Data availability refers inquiries to corresponding author; no separate raw icorr supplement identified.')]
    for doi,title,source,reason in pending:
        p=ROOT/source
        assert p.is_file(),p
        assert doi not in set(master.doi)
        ledger.append(dict(doi=doi,title=title,status='source_reviewed_no_accepted_icorr_record',
                           records_in_master=0,normalized_targets=0,source_file=str(p),
                           source_url='https://doi.org/'+doi,source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),reason=reason))
    inventory=pd.DataFrame(ledger)
    assert inventory.doi.str.lower().nunique()==50
    inventory.to_csv(OUT/'paper_inventory_50_screened.csv',index=False,encoding='utf-8-sig')
    inventory[inventory.records_in_master.eq(0)].to_csv(OUT/'six_papers_without_accepted_icorr.csv',index=False,encoding='utf-8-sig')
    supplements=[]
    for p in sorted((ROOT/'data/raw/expand50').glob('s41529-*/supplement_1.pdf')):
        info=json.loads((p.parent/'retrieval.json').read_text(encoding='utf8'))
        entry=next(e for e in info['supplementary'] if e['file'].endswith('.pdf'))
        supplements.append(dict(doi=info['doi'],file=str(p),url=entry['url'],sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                                accepted_icorr_records=0,status='downloaded_and_text_reviewed_no_icorr_table'))
    (OUT/'supplementary_audit.json').write_text(json.dumps(supplements,indent=2),encoding='utf8')
    status=json.loads((OUT/'status.json').read_text(encoding='utf8'))
    status.update(screened_paper_inventory=50,extracted_paper_target_achieved=False,
                  provisional_records=len(provisional),held_records=len(held),
                  new_reported_table_records=int(new.value_origin.eq('reported_table').sum()),
                  supplementary_pdf_files_reviewed=len(supplements),
                  note='50 is the screened inventory, NOT the number of papers with extracted icorr records. Master has 44 papers; six remain without accepted icorr. All 36 additions held.')
    (OUT/'status.json').write_text(json.dumps(status,indent=2),encoding='utf8')
    current=ROOT/'data/processed/pilot100/current_status.json'
    info=json.loads(current.read_text(encoding='utf8'))
    info.update(extracted_rows=len(master),extracted_papers=master.doi.nunique(),held_rows=len(held),
                normalized_target_present_rows=int(master.icorr_A_cm2.notna().sum()),
                normalized_target_missing_rows=int(master.icorr_A_cm2.isna().sum()),
                shortfall_to_target=max(0,info.get('target_rows',400)-len(master)),
                target_papers=50,paper_shortfall=6,last_collection_update='2026-10-19',
                expansion_report='docs/expansion50_20261019.md')
    current.write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(status,indent=2))


if __name__=='__main__':main()
