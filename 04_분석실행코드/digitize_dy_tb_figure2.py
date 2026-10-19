"""Digitize observed markers, retaining cycle dependence and pixel uncertainty.

Coordinates refer to the two original raster images embedded in PDF page 4,
not a resized screenshot. No interpolated line coordinates are observations.
Only the final observed cycle per material/solution series enters the master;
the complete dependent trajectory remains in the audit CSV.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pymupdf
from PIL import Image, ImageDraw

from ree_research.ingestion import prepare_pdf
from ree_research.schema import prepare
from normalize_dataset_units import normalize

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / '01_논문원문과데이터/raw/target400/sources/dysprosium_terbium'
OUT = ROOT / '01_논문원문과데이터/processed/target400'
MASTER = ROOT / '01_논문원문과데이터/processed/pilot100/llm_pending_all.csv'
DOI = '10.1007/s11003-015-9767-2'
TITLE = 'Corrosion-Electrochemical Properties of Fe-Nb-B Amorphous Alloys Doped with Dysprosium or Terbium'

# Native-image marker centers, manually read and checked against enlarged panels.
# The visibly absent curve 2 in panel b is NOT reconstructed.
PANELS = {
    'a': dict(x=[212,253,294,335,377,418,459,500,541], zero=312,
              upper_y=29, upper_value=.03, image=93, re='none',
              composition='Fe84 Nb2 B14 (at.%)', values={
                  1:[297,300,298,281,311,299,283,270,271],
                  2:[226,197,231,106,166,166,55,165,221],
                  3:[284,310,287,275,285,293,295,302,288],
                  4:[273,266,275,236,296,294,81,291,271],
                  5:[295,277,285,311,311,293,215,289,251]}),
    'b': dict(x=[831,872,913,953,994,1035,1075,1116,1156], zero=331,
              upper_y=92, upper_value=.01, image=93, re='Dy',
              composition='Fe82 Nb2 B14 Dy2 (at.%)', values={
                  1:[307,307,302,300,302,299,302,302,305],
                  3:[282,302,286,279,144,92,72,172,228],
                  4:[284,309,321,237,192,161,155,150,137],
                  5:[273,153,176,165,125,134,160,166,69]}),
    'c': dict(x=[221,265,309,352,396,439,482,526,569], zero=314,
              upper_y=17, upper_value=.0012, image=94, re='Tb',
              composition='Fe82 Nb2 B14 Tb2 (at.%)', values={
                  1:[308,271,271,286,232,225,247,303,293],
                  2:[276,128,180,177,182,156,107,109,117],
                  3:[248,164,128,119,128,131,165,169,194],
                  4:[299,190,215,161,195,193,208,282,271],
                  5:[282,283,291,308,261,202,208,222,205]})}
COLORS = {1:'#d62728',2:'#1f77b4',3:'#2ca02c',4:'#ff7f0e',5:'#9467bd'}


def digitize():
    OUT.mkdir(parents=True, exist_ok=True)
    pdf = pymupdf.open(SOURCE/'source.pdf')
    sha = hashlib.sha256((SOURCE/'source.pdf').read_bytes()).hexdigest()
    prepare_pdf(SOURCE/'source.pdf', SOURCE, DOI, TITLE)
    images = {}
    for xref in (93,94):
        obj = pdf.extract_image(xref)
        path = SOURCE/f'figure2_{xref}.png'
        path.write_bytes(obj['image'])
        images[xref] = Image.open(path).convert('RGB')
    rows = []
    for panel, cfg in PANELS.items():
        # Conservative 3 px marker placement + 2 px axis calibration allowance.
        error = 5 * cfg['upper_value'] / (cfg['zero']-cfg['upper_y'])
        draw = ImageDraw.Draw(images[cfg['image']])
        for concentration, ys in cfg['values'].items():
            assert len(ys) == 9
            for cycle, (x,y) in enumerate(zip(cfg['x'],ys),1):
                value = (cfg['zero']-y)*cfg['upper_value']/(cfg['zero']-cfg['upper_y'])
                value = float(f'{value:.2g}')
                resolved = value > error
                rows.append(dict(panel=panel, material=cfg['composition'],
                    RE_element_cat=cfg['re'], KOH_mol_L=concentration,
                    polarization_cycle=cycle, marker_x_px=x, marker_y_px=y,
                    axis_zero_y_px=cfg['zero'], axis_upper_y_px=cfg['upper_y'],
                    axis_upper_value_mA_cm2=cfg['upper_value'], native_image_xref=cfg['image'],
                    graph_icorr_mA_cm2=value, graph_reading_error_mA_cm2=error,
                    graph_lower_A_cm2=max(0,value-error)*1e-3,
                    graph_upper_A_cm2=(value+error)*1e-3,
                    icorr_A_cm2=value*1e-3 if resolved else np.nan,
                    reading_status='approximate_marker_reading' if resolved else 'near_zero_below_graph_resolution',
                    source_sha256=sha, doi=DOI, source_locator=f'page:4;Figure 2({panel});curve:{concentration};cycle:{cycle}',
                    dependent_series_id=f'dytb2015_{panel}_KOH{concentration}M',
                    uncertainty_type='graph_reading_tolerance_not_statistical_confidence_interval'))
                draw.ellipse((x-6,y-6,x+6,y+6),outline=COLORS[concentration],width=1)
    data=pd.DataFrame(rows)
    assert len(data)==126 and data.dependent_series_id.nunique()==14
    assert not data.duplicated(['dependent_series_id','polarization_cycle']).any()
    for xref, im in images.items():im.save(OUT/f'figure2_{xref}_digitization_overlay.png')
    data.to_csv(OUT/'dy_tb_all_cycles_digitized.csv',index=False)
    terminal=data[data.polarization_cycle.eq(9)].copy()
    assert len(terminal)==14 and terminal.icorr_A_cm2.notna().all()
    terminal.to_csv(OUT/'dy_tb_terminal_cycle_digitized.csv',index=False)
    return terminal


def main():
    terminal=digitize()
    current=pd.read_csv(MASTER)
    backup=OUT/'before_graph_append.csv'
    if not backup.exists():current.to_csv(backup,index=False)
    records=[]
    for _,r in terminal.iterrows():
        locator=r.source_locator
        rid='graph_'+hashlib.sha256((DOI+'|'+locator).encode()).hexdigest()[:16]
        records.append(dict(record_id=rid,paper_id=DOI,doi=DOI,paper_title=TITLE,
            sample_id=r.dependent_series_id+'_cycle9',
            original_icorr_value=r.graph_icorr_mA_cm2,original_icorr_unit='mA/cm2',
            icorr_value=r.graph_icorr_mA_cm2,icorr_unit='mA/cm2',icorr_A_cm2=r.icorr_A_cm2,
            graph_reading_error_A_cm2=r.graph_reading_error_mA_cm2*1e-3,
            graph_lower_A_cm2=r.graph_lower_A_cm2,graph_upper_A_cm2=r.graph_upper_A_cm2,
            value_origin='graph_digitized',target_precision='approximate_2_significant_digits',
            polarization_cycle=9,dependent_series_id=r.dependent_series_id,
            KOH_mol_L=r.KOH_mol_L,temperature_C=19.85,scan_rate_mV_s=20,
            reference_electrode_cat='Ag/AgCl',RE_element_cat=r.RE_element_cat,
            matrix_family_reported='amorphous',matrix_phase_reported='amorphous metallic alloy',
            phase_evidence_type='pre_corrosion_characterization',phase_source_locator='page:2;Materials and Experimental Procedure',
            product_form_cat='melt_spun_ribbon',nominal_composition_atpct=r.material,
            composition_basis='source_formula_atpct_not_verified_bulk_wtpct',
            source_locator=locator,source_sha256=r.source_sha256,
            source_file=str((SOURCE/'source.pdf').relative_to(ROOT)),
            evidence_quote='Behavior of icorr for nine cycles of potential scanning',
            extraction_source='target400_dy_tb_graph_digitization',extraction_method='manual_native_image_marker_digitization',
            icorr_method_cat='cyclic_voltammetry_reported_icorr',
            review_status='pending',review_flag='graph_digitization_requires_independent_review',
            hold_reason='graph_reading_cyclic_voltammetry_method_and_nominal_composition_require_review',
            quality_hold_reason='graph_reading_cyclic_voltammetry_method_and_nominal_composition_require_review',
            notes='Terminal observed cycle only; 9 dependent cycles retained separately. NOT nine independent specimens. Figure b curve 2 absent, not inferred. Source labels current as icorr; equivalence to Tafel corrosion current not established. No measured wt.% chemistry inferred. Reading error is a conservative 5-native-pixel tolerance, not experimental SD or confidence interval.'))
    batch=pd.DataFrame(records)
    new=batch[~batch.record_id.isin(current.record_id)]
    if new.doi.str.lower().isin(current.doi.str.lower()).any():
        raise ValueError('Existing DOI needs specimen/condition deduplication')
    merged=pd.concat([current,new],ignore_index=True)
    pd.testing.assert_frame_equal(current,merged.iloc[:len(current)][current.columns].reset_index(drop=True),check_dtype=False)
    # Add a missing source pointer on reruns without overwriting reviewed values.
    mask=merged.record_id.isin(batch.record_id)&merged.source_file.isna()
    merged.loc[mask,'source_file']=str((SOURCE/'source.pdf').relative_to(ROOT))
    merged=normalize(merged)
    assert merged.record_id.is_unique
    eligible=merged[merged.hold_reason.isna()|merged.hold_reason.eq('')].copy()
    features=prepare(eligible,('pending',))
    held=merged[~merged.record_id.isin(eligible.record_id)]
    report=dict(target_records=400,total_records=len(merged),total_papers=int(merged.paper_id.nunique()),
        newly_appended=len(new),graph_terminal_records=14,graph_trajectory_readings=126,
        graph_distinct_material_solution_series=14,graph_materials=3,
        graph_records_held=14,provisional_records=len(features),held_records=len(held),
        normalized_target_present=int(merged.icorr_A_cm2.notna().sum()),
        unresolved_target_records=int(merged.icorr_A_cm2.isna().sum()),
        shortfall_to_400=max(0,400-len(merged)),human_verified=0,
        note='126 trajectory readings are NOT added to the master count; only 14 final-cycle series representatives are included. All graph representatives held from modeling.')
    batch.to_csv(OUT/'new_graph_observations.csv',index=False)
    merged.to_csv(OUT/'llm_pending_all.csv',index=False)
    (OUT/'status.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    merged.to_csv(MASTER,index=False)
    features.to_csv(ROOT/'01_논문원문과데이터/processed/pilot100/provisional_for_model.csv',index=False)
    held.to_csv(ROOT/'01_논문원문과데이터/processed/pilot100/held_for_review.csv',index=False)
    status_path=ROOT/'01_논문원문과데이터/processed/pilot100/current_status.json'
    status=json.loads(status_path.read_text(encoding='utf8'))
    status.update(target_rows=400,extracted_rows=len(merged),extracted_papers=int(merged.paper_id.nunique()),
        held_rows=len(held),provisional_rows=len(features),shortfall_to_target=report['shortfall_to_400'],
        normalized_target_present_rows=report['normalized_target_present'],latest_target400=report)
    status_path.write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
