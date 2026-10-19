"""Reproducible transcription of PDF tables inspected as rendered page images.

These agent transcriptions remain pending independent human review. They are
not LLM quote matches, OCR output, or additional independent replicates.
"""
import hashlib
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def save(source_name, rows):
    source = ROOT / '01_논문원문과데이터/raw/additional' / source_name
    meta = json.loads((source / 'metadata.json').read_text(encoding='utf-8'))
    for row in rows:
        row.update(paper_id=meta['doi'], doi=meta['doi'], review_status='pending',
                   review_flag='needs_independent_source_review',
                   extraction_method='agent_visual_table_transcription',
                   evidence_match='visual_pdf_table_not_automatic_text_match',
                   source_file=str(source / 'article.pdf'),
                   source_url='https://doi.org/' + meta['doi'])
        row['record_id'] = hashlib.sha256(
            (meta['doi'] + ':' + row['sample_id']).encode()).hexdigest()[:20]
    out = ROOT / '01_논문원문과데이터/processed/extractions' / source_name
    out.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out / 'pending_measurements.csv', index=False)
    (out / 'visual_transcription.json').write_text(json.dumps({
        'method': 'agent visual transcription; independent human review pending',
        'pdf_sha256': hashlib.sha256((source / 'article.pdf').read_bytes()).hexdigest(),
        'rows': rows}, ensure_ascii=False, indent=2), encoding='utf-8')
    (out / 'run.json').write_text(json.dumps({
        'source': str(source), 'model': None, 'method': 'agent_visual_table_transcription',
        'rows': len(rows), 'usage': {}, 'independent_human_verified': False}, indent=2), encoding='utf-8')
    print(source_name, len(rows))


def main():
    rows = []
    for sample, comp, re, value in [
        ('1#', [.07,.03,1.44,.012,.003,.030], 0, 8.2716),
        ('2#', [.06,.02,1.52,.015,.001,.025], 44, 4.3779),
        ('3#', [.08,.02,1.52,.013,.002,.023], 47, 2.7771),
        ('4#', [.06,.03,1.48,.010,.001,.024], 57, 3.9912),
    ]:
        rows.append(dict(zip(['C','Si','Mn','P','S','Nb'], comp)) | dict(
            sample_id=sample, RE_ppm=re, RE_element_cat='Ce+La' if re else 'none',
            icorr_A_cm2=value*1e-6, icorr_value=value, icorr_unit='1e-6 A/cm2',
            electrolyte_condition_cat='NaCl_3.5pct',
            alloy_family_reported='A572_Gr65', icorr_method_cat='polarization_fitting',
            reference_electrode_cat='SCE', surface_preparation_cat='ground_and_polished',
            source_locator='page:3;Table 2;' + sample,
            composition_locator='page:2;Table 1;' + sample, condition_locator='page:2;section 1',
            evidence_quote=f'Table 2: Jcorr/(10^-6 A cm^-2); {sample}: {value:.4f}',
            notes='Visual transcription of PDF pp218-219. RE wt.% x10000 to ppm. '
                  'NaCl percent basis unspecified; temperature/pH missing. '
                  'Table value retained; abstract rounds sample 3 to 2.77e-6. '
                  'Independent human source review pending.'))
    save('a572_re_2020', rows)

    rows = []
    compositions = [
        dict(C=.11,Si=.31,Mn=.60,P=.011,S=.0030,Al=.023),
        dict(C=.12,Si=.30,Mn=.60,P=.010,S=.0028,Al=.022),
        dict(C=.11,Si=.32,Mn=.61,P=.008,S=.0030,Al=.026),
    ]
    for sample, re, values in [
        (0, 0, [2.74e-4,2.60e-4,1.46e-4,1.51e-4]),
        (1, 17, [2.59e-4,1.36e-4,1.24e-4,1.07e-4]),
        (2, 23, [1.19e-4,1.11e-4,1.08e-4,4.10e-5]),
    ]:
        for hours, value in zip([72,120,168,216], values):
            rows.append(compositions[sample] | dict(
                sample_id=f'{sample}#_{hours}h', RE_ppm=re,
                RE_element_cat='Ce+La' if re else 'none', exposure_h=hours,
                icorr_A_cm2=value, icorr_value=value, icorr_unit='A/cm2',
                electrolyte_condition_cat='NaHSO3_1molL',
                alloy_family_reported='No10_Al_containing_carbon_steel',
                pre_exposure_protocol_cat='cyclic_immersion_NaHSO3_0.01molL',
                surface_state_cat='rusted', icorr_method_cat='Tafel_fitting',
                reference_electrode_cat='SCE', scan_rate_mV_s=.5,
                source_locator=f'page:6;Table 3;sample {sample}#;{hours}h',
                composition_locator=f'page:3;Table 1;sample {sample}#',
                condition_locator='page:3;sections 1.2 and 1.3',
                evidence_quote=f'Table 3: I0/(A cm^-2); sample {sample}#; {hours} h; {value:.2e}',
                notes='Visual transcription of PDF pp119,122. La+Ce measured wt.% '
                      'sum x10000 gives RE ppm. Pre-corrosion uses 0.01 mol/L NaHSO3; '
                      'electrochemical measurement uses 1 mol/L NaHSO3. '
                      'Do not transfer cyclic-bath temperature to polarization test. '
                      'Four exposure times are distinct conditions, not replicates. '
                      'Independent human source review pending.'))
    save('al_steel_re_2026', rows)


if __name__ == '__main__':
    main()
