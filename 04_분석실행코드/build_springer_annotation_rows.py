"""Transcribe explicit printed i_corr annotations, never estimate plotted curves.

All 5 alloys x 3 temperatures x 4 times are retained, pending human review.
Composition is read from the publisher's JATS Table 1, not nominal alloy names.
"""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import pandas as pd
from ree_research.schema import prepare

ROOT = Path(__file__).resolve().parents[1]
DOI = '10.1038/s41529-025-00682-8'
SOURCE = ROOT / '01_논문원문과데이터/raw/springer_round/s41529-025-00682-8'
# Each list is ordered by nominal La content 0, 0.5, 1.0, 1.5, 2.0 wt.%.
# Numbers are printed annotations in figures 6a, 8a, 10a, in A/cm2.
VALUES = {
    25: {
        0: ['1.322e-7','6.091e-8','1.477e-6','3.548e-6','7.423e-6'],
        2: ['5.481e-9','1.542e-5','5.633e-9','1.826e-9','1.327e-6'],
        4: ['5.982e-7','5.495e-6','7.852e-6','1.549e-5','1.466e-6'],
        8: ['2.476e-7','1.223e-5','5.623e-6','2.518e-6','3.064e-6'],
    },
    50: {
        0: ['9.202e-7','9.016e-7','1.251e-6','2.393e-6','9.016e-7'],
        2: ['5.062e-7','1.997e-5','3.109e-6','3.697e-6','3.012e-6'],
        4: ['9.594e-7','3.872e-7','3.656e-6','9.862e-7','1.959e-6'],
        8: ['5.495e-7','5.272e-7','2.499e-6','3.211e-6','5.248e-6'],
    },
    75: {
        0: ['1.029e-6','9.578e-7','1.723e-6','1.211e-6','4.857e-6'],
        2: ['7.308e-7','1.597e-6','4.095e-6','4.667e-6','2.948e-6'],
        4: ['4.130e-7','1.820e-6','5.023e-6','4.140e-6','5.297e-6'],
        8: ['1.267e-6','1.183e-6','4.887e-6','5.728e-6','4.540e-6'],
    },
}


def main():
    root = ET.fromstring((SOURCE/'article.xml').read_text(encoding='utf-8'))
    for node in root.iter():
        node.tag = node.tag.rsplit('}', 1)[-1]
    table = next(t for t in root.iter('table-wrap') if t.get('id') == 'Tab1')
    cells = [[''.join(c.itertext()).strip() for c in row] for row in table.iter('tr')]
    headers = cells[0][1:]
    alloys = {row[0]: dict(zip(headers, row[1:])) for row in cells[1:]}
    rows = []
    for temperature, days_values in VALUES.items():
        figure = {25: 6, 50: 8, 75: 10}[temperature]
        image = SOURCE/f'figure{figure}.png'
        image_hash = hashlib.sha256(image.read_bytes()).hexdigest()
        for days, values in days_values.items():
            for alloy, text_value in zip(alloys, values):
                comp = alloys[alloy]
                sample_id = f'{alloy}_{temperature}C_{days}d'
                row = {key: float(comp[key]) for key in ['Cr','Ni','Mo','Cu','N','P','S']}
                row.update(record_id=hashlib.sha256((DOI+':'+sample_id).encode()).hexdigest()[:20],
                    paper_id=DOI, doi=DOI, sample_id=sample_id,
                    RE_ppm=float(comp['La'])*10000,
                    RE_element_cat='none' if alloy == '0La' else 'La',
                    nominal_La_wt_pct=float(alloy[:-2]), temperature_C=temperature,
                    exposure_h=days*24, icorr_A_cm2=float(text_value),
                    icorr_value=float(text_value), icorr_unit='A/cm2',
                    original_icorr_printed=text_value,
                    electrolyte_condition_cat='seawater+NaOH_40gL+Na2SO4_7.1gL',
                    electrolyte_family_cat='alkaline_seawater', pH_reported='>14',
                    reference_electrode_cat='Ag/AgCl', icorr_method_cat='Tafel_fitting',
                    heat_treatment_temperature_C=1200, heat_treatment_duration_h=1,
                    heat_treatment_cat='solution_annealed_water_cooled',
                    matrix_family_reported='austenitic',
                    alloy_family_reported='Fe20Cr18Ni6Mo0.8Cu0.2N_La',
                    pre_exposure_protocol_cat='alkaline_seawater_immersion_then_acid_rinse_10s',
                    surface_preparation_cat='diamond_polished_1um',
                    source_locator=f'Fig{figure}a;Tafel of {days} days;{alloy}',
                    composition_locator='table-wrap:Tab1;'+alloy,
                    condition_locator='p:Par43;p:Par50;p:Par51;p:Par52',
                    evidence_quote=f'Figure {figure}a; Tafel of {days} days; {float(alloy[:-2]):g} wt.% La; i_corr {text_value} A cm^-2',
                    evidence_match='printed_figure_annotation_visual_transcription_not_curve_digitization',
                    review_status='pending', review_flag='needs_independent_source_review',
                    extraction_method='agent_visual_printed_annotation_transcription',
                    retrieval_provider='springer_openaccess_jats',
                    source_file=str(SOURCE/'article.xml'), source_image_file=str(image),
                    source_image_sha256=image_hash,
                    source_url='https://doi.org/'+DOI,
                    source_image_url='https://media.springernature.com/full/springer-static/image/art%3A10.1038%2Fs41529-025-00682-8/MediaObjects/'+f'41529_2025_682_Fig{figure}_HTML.png',
                    notes='Printed i_corr annotations, not estimated curve coordinates. '
                          'ICP-AES measured La used for RE ppm, not nominal La. '
                          'pH >14 is censored; numeric pH remains missing. '
                          'Acid rinse: 20% HNO3+10% HF+70% water, 10 s. '
                          'Same paper; no independent human verification.')
                rows.append(row)
    frame = pd.DataFrame(rows)
    assert len(frame) == 60 and frame.record_id.nunique() == 60
    # Cross-check three explicit text/conclusion anchors against the image transcription.
    for sample, value in [('0La_25C_8d',2.476e-7),('0.5La_50C_8d',5.272e-7),('0.5La_75C_8d',1.183e-6)]:
        assert frame.set_index('sample_id').loc[sample,'icorr_A_cm2'] == value
    prepare(frame, allowed_review_statuses=('pending',))
    out = ROOT/'01_논문원문과데이터/processed/extractions/springer_la_asw_2025'
    out.mkdir(parents=True, exist_ok=True)
    frame.to_csv(out/'pending_measurements.csv', index=False)
    (out/'annotation_transcription.json').write_text(json.dumps({
        'doi':DOI, 'values_by_temperature_and_days':VALUES,
        'order':list(alloys), 'method':'printed labels, no curve digitization',
        'human_verified':False}, indent=2), encoding='utf-8')
    (out/'run.json').write_text(json.dumps({'source':str(SOURCE),
        'method':'agent_visual_printed_annotation_transcription', 'model':None,
        'retrieval_provider':'springer_openaccess_jats', 'requires_annotation_check':True,
        'rows':60, 'usage':{}}, indent=2), encoding='utf-8')
    print('60 pending rows; 1 paper; 3 temperatures x 4 exposure times x 5 alloys')


if __name__ == '__main__':
    main()
