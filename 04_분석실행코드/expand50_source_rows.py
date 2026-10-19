"""Append source-supported observations without promoting them to verified data.

All coordinates refer to a saved 1.5x PDF rendering. Unresolved printed units
remain unresolved; graph reading tolerances are not experimental uncertainties.
"""
import csv
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import pandas as pd
import pymupdf
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '01_논문원문과데이터/processed/expand50'
MASTER = ROOT / '01_논문원문과데이터/processed/pilot100/llm_pending_all.csv'
ROWS = []


def add(doi, title, sample, value, unit, factor, source, locator, **fields):
    path = ROOT / source
    assert path.is_file(), path
    row = dict(record_id=hashlib.sha256(f'{doi}|{locator}|{sample}'.encode()).hexdigest()[:20],
               paper_id=doi, doi=doi, paper_title=title, sample_id=sample,
               review_status='pending', review_flag='needs_independent_source_review',
               source_file=str(path), source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
               source_url='https://doi.org/'+doi, source_locator=locator,
               original_icorr_value=value, original_icorr_unit=unit,
               original_icorr_printed=str(value)+' '+unit,
               icorr_A_cm2=value*factor if factor is not None else None,
               icorr_value=value*factor if factor is not None else value,
               icorr_unit='A/cm2' if factor is not None else unit,
               unit_conversion_factor_to_A_cm2=factor,
               extraction_source='expand50_20261019',
               extraction_method='source_table_transcription', value_origin='reported_table',
               evidence_quote=f'{locator}: {sample}; reported central value {value} {unit}',
               evidence_match='table_cell_transcription',
               target_unit_status='explicit_density_unit_pending_review' if factor is not None else 'unresolved_printed_unit',
               hold_reason='new_batch_requires_independent_source_and_method_review',
               quality_hold_reason='new_batch_requires_independent_source_and_method_review')
    row.update(fields)
    ROWS.append(row)


def build_rows():
    doi='10.1007/s11665-015-1651-6'
    title='Effects of Ce on Inclusions, Microstructure, Mechanical Properties, and Corrosion Behavior of AISI 202 Stainless Steel'
    chem=[(.071,.115,6.014,.0048,.0061,17.4,5.05,0),
          (.073,.126,6.019,.0046,.0058,17.2,5.04,50),
          (.071,.118,6.015,.0043,.0057,17.3,5.02,110),
          (.072,.124,6.013,.0042,.0055,17.1,5.03,160),
          (.074,.119,6.015,.0042,.0054,17.2,5.04,220)]
    for day,tab,page,vals in [(1,5,16,[5.6116e-3,7.9742e-4,5.8152e-4,1.6956e-4,2.1288e-4]),
                              (15,6,17,[2.8329e-3,4.0511e-4,3.9324e-4,7.2352e-5,7.5342e-5]),
                              (45,7,17,[3.2769e-3,8.2327e-4,6.2915e-4,5.3264e-4,7.8571e-4])]:
        for sample,v,c in zip(['A','A1','A2','A3','A4'],vals,chem):
            add(doi,title,f'{sample}_{day}d',v,'Amp/cm (as printed)',None,
                '01_논문원문과데이터/raw/springer_round2/s11665-015-1651-6/article.pdf',f'page:{page};Table {tab}',
                **dict(zip(['C','N','Mn','P','S','Cr','Ni','RE_ppm'],c)),
                RE_element_cat='none' if sample=='A' else 'Ce',exposure_h=day*24,
                electrolyte_condition_cat='H2SO4_5wtpct',composition_locator='page:2;Table 1',
                icorr_method_cat='author_Tafel_fit',
                hold_reason='printed_Amp_per_cm_not_density_unit_requires_resolution',
                quality_hold_reason='printed_Amp_per_cm_not_density_unit_requires_resolution',
                notes='Table heading is Amp/cm, not A/cm2. Exposed area is 1 cm2 but does not repair a dimensionally ambiguous printed unit. Original values retained; normalized target deliberately blank. Different immersion times are dependent within a paper; do not split randomly.')

    doi='10.3390/ma16020876'
    title='Local Corrosion Behaviors in the Coarse-Grained Heat-Affected Zone in a Newly Developed Zr-Ti-Al-RE Deoxidized High-Strength Low-Alloy Steel'
    for sample,v in [('Base metal',9.31e-6),('CGHAZ',1.02e-5)]:
        add(doi,title,sample,v,'A cm2 (as printed)',None,
            '01_논문원문과데이터/raw/europepmc/PMC9864991/article.xml','Table 4',
            C=.05,Si=.17,Mn=1.55,Nb=.034,RE_element_cat='La+Ce',nacl_wt_pct=3.5,
            reference_electrode_cat='SCE',scan_rate_mV_s=.333,
            composition_locator='Table 1',condition_locator='section 2.3',
            hold_reason='printed_A_times_cm2_unit_requires_density_unit_confirmation',
            quality_hold_reason='printed_A_times_cm2_unit_requires_density_unit_confirmation',
            notes='Table 4 prints A cm2 rather than A/cm2. Preserve without silently fixing exponent. Table 1 combines Al+Ca+Zr+Ti+RE as 0.04 wt%; do not assign to individual elements. Text claims an order-of-magnitude difference but listed currents differ by about 1.10x; preserve table.')

    doi='10.3969/j.issn.1674-165x.2024.02.015'
    title='Effect of rare earth elements on microstructure and properties of superferritic stainless steel'
    source='01_논문원문과데이터/raw/additional/superferritic_re_2024/article.pdf'
    img=ROOT/'01_논문원문과데이터/processed/expand50/superferritic_p10.png'
    doc=pymupdf.open(ROOT/source)
    doc[9].get_pixmap(matrix=pymupdf.Matrix(1.5,1.5)).save(img)
    im=Image.open(img).convert('RGB');draw=ImageDraw.Draw(im)
    zero,upper,upper_value=795,657,.35
    audit=[]
    for temp,x,y in [(30,209,761),(50,281,682),(70,353,659)]:
        raw=(zero-y)/(zero-upper)*upper_value
        v=float(f'{raw:.2g}');err=5/(zero-upper)*upper_value
        draw.line((190,y,365,y),fill='magenta',width=2)
        draw.ellipse((x-4,y-4,x+4,y+4),outline='black',width=2)
        add(doi,title,f'No.2_{temp}C',v,'uA/cm2',1e-6,source,'page:10;Figure 16b',
            temperature_C=temp,nacl_wt_pct=3.5,RE_element_cat='RE_unspecified',
            matrix_family_reported='superferritic_stainless',reference_electrode_cat='SCE',
            heat_treatment_temperature_C=1030,heat_treatment_duration_h=.5,
            extraction_method='calibrated_bar_top_digitization',value_origin='graph_estimate',
            graph_reading_error_A_cm2=err*1e-6,
            graph_lower_A_cm2=max(0,raw-err)*1e-6,graph_upper_A_cm2=(raw+err)*1e-6,
            source_image_file=str(img),target_precision='2 significant figures',
            composition_locator='page:2;Table 1 (design targets only)',
            notes='Author-derived icorr bar, not minimum current at Ecorr. 1.5x PDF rendering; y=795 is zero and y=657 is 0.35 uA/cm2. Conservative +/-5 rendered pixels combines bar/axis reading; not an experimental SD or statistical CI. Final measured bulk chemistry and individual retained RE content not recovered; nominal design values not promoted to measured features.')
        audit.append(dict(doi=doi,sample=f'No.2_{temp}C',image=str(img),x_px=x,top_y_px=y,
                          zero_y_px=zero,upper_y_px=upper,upper_value=upper_value,
                          axis_unit='uA/cm2',axis_scale='linear',pixel_tolerance=5,
                          unrounded_value=raw,reported_estimate=v))
    im.save(OUT/'superferritic_figure16b_overlay.png')
    pd.DataFrame(audit).to_csv(OUT/'graph_coordinates.csv',index=False)

    title='Corrosion performances in simulated body fluids and cytotoxicity evaluation of Fe-based bulk metallic glasses'
    compositions={'BMG1':'Fe41 Co7 Cr15 Mo14 C15 B6 Y2',
                  'BMG2':'(Fe44 Cr5 Co5 Mo13 Mn11 C16 B6)98 Y2',
                  'BMG3':'Fe48 Cr15 Mo14 C15 B6 Er2'}
    data={'316L SS':[(4.54,.70),(1.76,.41)],'BMG1':[(2.34,.53),(.48,.16)],
          'BMG2':[(2.880,1.19),(.71,.39)],'BMG3':[(.90,.17),(.03,.01)]}
    for sample,values in data.items():
        for fluid,(v,sd),ph in zip(['Hanks','artificial_saliva'],values,[7.4,6.3]):
            add('10.1016/j.msec.2011.12.018',title,sample+'_'+fluid,v,'1e-7 A/cm2',1e-7,
                '01_논문원문과데이터/raw/expand50/bodyfluid2012/article.pdf','page:4;Table 1',
                temperature_C=37,pH=ph,electrolyte_condition_cat=fluid,reference_electrode_cat='SCE',
                scan_rate_mV_s=1,ocp_stabilization_min=120,
                reported_icorr_uncertainty_A_cm2=sd*1e-7,
                RE_element_cat='none' if sample=='316L SS' else ('Er' if sample=='BMG3' else 'Y'),
                nominal_composition_atpct=compositions.get(sample,''),composition_basis='nominal_atpct' if sample!='316L SS' else 'unreported',
                related_publication_group='Wang_Zheng_FeY_bodyfluids_2009_2012',
                notes='Primary author-hosted published PDF; table central values and printed +/- terms retained separately. Nominal at.% is not measured wt.%. BMG1/control results resemble 2009 paper; related-publication grouping is mandatory and reused baselines need source review. All held.')
    for fluid,v,sd,ph in [('Hanks',3.591,3.189,7.4),('artificial_saliva',1.461,.778,6.3)]:
        add('10.1016/j.elecom.2009.09.027','Corrosion performances of a Nickel-free Fe-based bulk metallic glass in simulated body fluids',
            'annealed_FeY_'+fluid,v,'1e-7 A/cm2',1e-7,
            '01_논문원문과데이터/raw/expand50/bodyfluid2009/article.pdf','page:4;Table 1',
            pH=ph,RE_element_cat='Y',electrolyte_condition_cat=fluid,reference_electrode_cat='SCE',
            nominal_composition_atpct='Fe41 Co7 Cr15 Mo14 C15 B6 Y2',composition_basis='nominal_atpct',
            heat_treatment_cat='annealed',reported_icorr_uncertainty_A_cm2=sd*1e-7,
            related_publication_group='Wang_Zheng_FeY_bodyfluids_2009_2012',
            notes='Only annealed rows appended. As-cast and 316L rows omitted because they closely match 2012 baselines. Two papers do not establish independent experiments for shared materials. Do not infer temperature from a review; verify original conditions.')

    doi='10.3390/ma14040929'
    for sample,v,sd in [('A0',.21,.12),('A1',.34,.15),('A2',.54,.11)]:
        add(doi,'Investigation of the Structural Heterogeneity and Corrosion Performance of the Annealed Fe-Based Metallic Glasses',
            sample,v,'uA/cm2',1e-6,'01_논문원문과데이터/raw/expand50/PMC7919831/article.xml','Table 1',
            RE_element_cat='Y',nominal_composition_atpct='Fe43 Cr20 Mo10 W4 C15 B6 Y2',
            composition_basis='nominal_atpct',electrolyte_condition_cat='HCl_1mol_L',
            reference_electrode_cat='SCE',scan_rate_mV_s=.5,ocp_stabilization_min=30,
            reported_icorr_uncertainty_A_cm2=sd*1e-6,
            heat_treatment_cat='as_spun' if sample=='A0' else 'annealed',
            notes='Table 1 icorr values preserved even though ipass and EIS rankings differ. Do not replace icorr by passive current. Room temperature remains unquantified; nominal atomic chemistry remains separate from wt.% features.')
    for sample,v in [('Fe-B9 BAS',9.82e-8),('316 SS',5.96e-8),('304 SS',7.83e-8)]:
        add('10.1016/j.jallcom.2013.09.186','Prominent Fe-based bulk amorphous steel alloy with large supercooled liquid region and superior corrosion resistance',
            sample,v,'A/cm2',1.,'01_논문원문과데이터/raw/expand50/bas2014/article.pdf','page:3;Table 2',
            RE_element_cat='Y' if sample=='Fe-B9 BAS' else 'none',electrolyte_condition_cat='Hanks_balanced_salt_solution',
            nominal_composition_atpct='Fe41 Cr15 Co7 Mo14 C12 B9 Y2' if sample=='Fe-B9 BAS' else '',
            composition_basis='nominal_atpct' if sample=='Fe-B9 BAS' else 'unreported',
            notes='Experimental Table 2, not an introductory literature value. Original abstract has Ce/Cr typographical inconsistency; body alloy series identifies Cr15. Do not convert nominal at.% into measured wt.%.')


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    build_rows()
    new=pd.DataFrame(ROWS)
    assert new.record_id.is_unique
    assert new.doi.nunique()==7
    current=pd.read_csv(MASTER,dtype=str)
    backup=OUT/'baseline_before_append.csv'
    if not backup.exists():
        backup.write_bytes(MASTER.read_bytes())
    fresh=new[~new.record_id.isin(current.record_id)]
    assert not fresh.doi.str.lower().isin(current.doi.str.lower()).any(), 'New paper already present; inspect before append'
    merged=pd.concat([current,fresh],ignore_index=True)
    assert merged.record_id.is_unique
    pd.testing.assert_frame_equal(current,merged.iloc[:len(current)][current.columns].reset_index(drop=True),check_dtype=False)
    new.to_csv(OUT/'new_observations.csv',index=False)
    merged.to_csv(MASTER,index=False)
    held_path=ROOT/'01_논문원문과데이터/processed/pilot100/held_for_review.csv'
    held=pd.read_csv(held_path,dtype=str)
    pd.concat([held,new[~new.record_id.isin(held.record_id)]],ignore_index=True).to_csv(held_path,index=False)
    status=dict(total_papers=int(merged.doi.nunique()),total_records=len(merged),
                new_papers=int(new.doi.nunique()),new_records=len(new),
                normalized_target_present=int(merged.icorr_A_cm2.notna().sum()),
                unresolved_targets=int(merged.icorr_A_cm2.isna().sum()),
                new_graph_estimates=int(new.value_origin.eq('graph_estimate').sum()),
                new_normalized_targets=int(new.icorr_A_cm2.notna().sum()),
                target_papers=50,paper_shortfall=max(0,50-merged.doi.nunique()),
                human_verified=int(merged.review_status.eq('verified').sum()),
                all_new_rows_held=True)
    (OUT/'status.json').write_text(json.dumps(status,indent=2),encoding='utf8')
    print(json.dumps(status,indent=2))


if __name__=='__main__':
    main()
