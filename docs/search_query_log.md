# 저장된 실제 API 검색식 목록

2026-10-16 로컬 응답 감사. 같은 서비스·동일 문자열의 페이지 응답은 한 검색식으로 묶었습니다.
조회한 응답만 포함합니다. 전체 적합 문헌 수, 전체 웹 검색 목록 또는 PRISMA 집계가 아닙니다.
정확한 개별 요청 시각은 응답에 없으면 미기록으로 유지했습니다. 파일 수정 시각으로 대체하지 않았습니다.

## S01 — Elsevier Scopus

```text
TITLE(cerium OR lanthanum OR yttrium OR "rare earth" OR mischmetal) AND TITLE(corrosion) AND TITLE(steel OR iron) AND NOT TITLE(inhibition OR inhibitor OR coating OR coatings OR conversion OR synergism OR nanoparticles OR deposited)
```

저장 응답 10개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 184개.

- `data/raw/round300/scopus_bulk_0.json`: API 전체 hit=226; 시작점=0; 실제 저장 레코드=25
- `data/raw/round300/scopus_bulk_100.json`: API 전체 hit=226; 시작점=100; 실제 저장 레코드=25
- `data/raw/round300/scopus_bulk_125.json`: API 전체 hit=226; 시작점=125; 실제 저장 레코드=25
- `data/raw/round300/scopus_bulk_150.json`: API 전체 hit=226; 시작점=150; 실제 저장 레코드=25
- `data/raw/round300/scopus_bulk_175.json`: API 전체 hit=226; 시작점=175; 실제 저장 레코드=25
- `data/raw/round300/scopus_bulk_200.json`: API 전체 hit=226; 시작점=200; 실제 저장 레코드=25
- `data/raw/round300/scopus_bulk_225.json`: API 전체 hit=226; 시작점=225; 실제 저장 레코드=1
- `data/raw/round300/scopus_bulk_25.json`: API 전체 hit=226; 시작점=25; 실제 저장 레코드=25
- `data/raw/round300/scopus_bulk_50.json`: API 전체 hit=226; 시작점=50; 실제 저장 레코드=25
- `data/raw/round300/scopus_bulk_75.json`: API 전체 hit=226; 시작점=75; 실제 저장 레코드=25

## S02 — Elsevier Scopus

```text
TITLE(cerium OR lanthanum OR yttrium OR "rare earth") AND TITLE(corrosion) AND TITLE(steel OR iron)
```

저장 응답 4개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 77개.

- `data/raw/round300/scopus_targeted_0_0.json`: API 전체 hit=372; 시작점=0; 실제 저장 레코드=25
- `data/raw/round300/scopus_targeted_0_25.json`: API 전체 hit=372; 시작점=25; 실제 저장 레코드=25
- `data/raw/round300/scopus_targeted_0_50.json`: API 전체 hit=372; 시작점=50; 실제 저장 레코드=25
- `data/raw/round300/scopus_targeted_0_75.json`: API 전체 hit=372; 시작점=75; 실제 저장 레코드=25

## S03 — Elsevier Scopus

```text
TITLE-ABS-KEY(("rare earth" OR cerium OR lanthanum) AND "corrosion current density" AND steel)
```

저장 응답 4개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 91개.

- `data/raw/round300/scopus_targeted_1_0.json`: API 전체 hit=128; 시작점=0; 실제 저장 레코드=25
- `data/raw/round300/scopus_targeted_1_25.json`: API 전체 hit=128; 시작점=25; 실제 저장 레코드=25
- `data/raw/round300/scopus_targeted_1_50.json`: API 전체 hit=128; 시작점=50; 실제 저장 레코드=25
- `data/raw/round300/scopus_targeted_1_75.json`: API 전체 hit=128; 시작점=75; 실제 저장 레코드=25

## S04 — Elsevier Scopus

```text
TITLE-ABS-KEY((cerium OR lanthanum OR "rare earth") AND (steel OR iron) AND corrosion) AND PUBYEAR > 2024
```

저장 응답 1개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 25개.

- `data/raw/round300/query_3.json`: API 전체 hit=417; 시작점=0; 실제 저장 레코드=25

## S05 — Elsevier Scopus

```text
TITLE-ABS-KEY((cerium OR lanthanum OR "rare earth") AND (steel OR steels OR "pure iron") AND corrosion AND (addition OR microalloying OR inclusion OR alloying)) AND PUBYEAR < 2020
```

저장 응답 1개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 25개.

- `data/raw/discovery/ferrous_before2020.json`: API 전체 hit=520; 시작점=0; 실제 저장 레코드=25

## S06 — Elsevier Scopus

```text
TITLE-ABS-KEY((cerium OR lanthanum OR "rare earth") AND (steel OR steels OR "pure iron") AND corrosion AND (addition OR microalloying OR inclusion OR alloying)) AND PUBYEAR > 2019 AND PUBYEAR < 2026
```

저장 응답 1개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 24개.

- `data/raw/discovery/ferrous_2020_2025.json`: API 전체 hit=324; 시작점=0; 실제 저장 레코드=25

## S07 — Elsevier Scopus

```text
TITLE-ABS-KEY((cerium OR lanthanum OR "rare earth") AND (steel OR steels) AND (polarization OR "current density" OR Tafel))
```

저장 응답 1개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 25개.

- `data/raw/discovery/ferrous_electrochemical.json`: API 전체 hit=770; 시작점=0; 실제 저장 레코드=25

## S08 — Elsevier Scopus

```text
TITLE-ABS-KEY((cerium OR lanthanum OR "rare earth") AND (steel OR steels) AND corrosion AND (addition OR microalloying OR inclusion OR alloying))
```

저장 응답 1개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 25개.

- `data/raw/discovery/ferrous_bulk.json`: API 전체 hit=907; 시작점=0; 실제 저장 레코드=25

## S09 — Elsevier Scopus

```text
TITLE-ABS-KEY((cerium OR lanthanum OR "rare earth") AND steel AND corrosion) AND PUBYEAR < 2015
```

저장 응답 1개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 21개.

- `data/raw/round300/query_1.json`: API 전체 hit=1087; 시작점=0; 실제 저장 레코드=25

## S10 — Elsevier Scopus

```text
TITLE-ABS-KEY((cerium OR lanthanum OR yttrium OR "rare earth") AND (steel OR iron) AND ("corrosion current" OR Tafel))
```

저장 응답 1개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 25개.

- `data/raw/round300/query_0.json`: API 전체 hit=452; 시작점=0; 실제 저장 레코드=25

## S11 — Elsevier Scopus

```text
TITLE-ABS-KEY((cerium OR lanthanum OR yttrium) AND steel AND "corrosion current")
```

저장 응답 1개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 25개.

- `data/raw/add30_20261016/api_search.json`: API 전체 hit=136; 시작점=0; 실제 저장 레코드=25

## S12 — Elsevier Scopus

```text
TITLE-ABS-KEY((yttrium OR praseodymium OR neodymium) AND steel AND corrosion)
```

저장 응답 1개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 25개.

- `data/raw/round300/query_2.json`: API 전체 hit=815; 시작점=0; 실제 저장 레코드=25

## S13 — Elsevier Scopus

```text
TITLE-ABS-KEY(cerium AND corrosion AND steel)
```

저장 응답 1개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 3개.

- `data/raw/elsevier_search.json`: API 전체 hit=1351; 시작점=0; 실제 저장 레코드=3

## S14 — Europe PMC

```text
(DOI:10.1007/978-3-030-05861-6_53 OR DOI:10.1007/s11663-025-03792-5 OR DOI:10.1007/s11663-025-03817-z OR DOI:10.1007/s11665-019-04112-0 OR DOI:10.1016/j.corcom.2025.11.001 OR DOI:10.1016/j.corsci.2026.114050 OR DOI:10.1016/j.corsci.2026.114142 OR DOI:10.1016/j.jallcom.2026.189103 OR DOI:10.1016/j.jmrt.2025.11.079 OR DOI:10.1016/j.jmrt.2026.03.287 OR DOI:10.1016/j.jobe.2025.114528 OR DOI:10.1016/j.physb.2019.01.027 OR DOI:10.2355/isijinternational.isijint-2019-248 OR DOI:10.3390/ma12203359 OR DOI:10.3390/ma19122685 OR DOI:10.7449/2019/mst_2019_122_129 OR DOI:10.1002/maco.202514828 OR DOI:10.1007/s11664-026-13249-3 OR DOI:10.1007/s11665-026-15283-y OR DOI:10.1007/s42243-025-01553-x OR DOI:10.1016/j.apsusc.2017.11.041 OR DOI:10.1016/j.apsusc.2018.12.164 OR DOI:10.1016/j.apsusc.2018.12.243 OR DOI:10.1016/j.corsci.2025.113266 OR DOI:10.1016/j.corsci.2026.114238 OR DOI:10.1016/j.envres.2019.03.069 OR DOI:10.1016/j.isci.2025.113319 OR DOI:10.1016/j.jmrt.2026.09.183 OR DOI:10.1016/j.jre.2024.12.025 OR DOI:10.1016/j.jscs.2018.03.005 OR DOI:10.1016/j.mtcomm.2026.116157 OR DOI:10.1016/j.rineng.2026.112876 OR DOI:10.11785/s1000-4343.20260805 OR DOI:10.11896/cldb.17070037 OR DOI:10.13251/j.issn.0254-6051.2019.04.004 OR DOI:10.20964/2019.03.31 OR DOI:10.3390/met15090935 OR DOI:10.3390/met15121289 OR DOI:10.3724/s1004-0277.202604006 OR DOI:10.3724/s1004-0277.202604012) AND OPEN_ACCESS:Y
```

저장 응답 1개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 3개.

- `data/raw/europepmc/doi_lookup.json`: API 전체 hit=3; 시작점=*; 실제 저장 레코드=3

## S15 — Europe PMC

```text
(TITLE:steel OR TITLE:steels OR TITLE:iron) AND (TITLE:cerium OR TITLE:lanthanum OR TITLE:"rare earth" OR TITLE:Ce OR TITLE:La) AND TITLE:corrosion AND OPEN_ACCESS:Y
```

저장 응답 1개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 8개.

- `data/raw/europepmc/targeted_search.json`: API 전체 hit=8; 시작점=*; 실제 저장 레코드=8

## S16 — Europe PMC

```text
(TITLE:steel OR TITLE:steels OR TITLE:iron) AND TITLE:corrosion AND (yttrium OR neodymium OR scandium OR microalloying) AND OPEN_ACCESS:Y
```

저장 응답 1개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 41개.

- `data/raw/europepmc/extended_search.json`: API 전체 hit=41; 시작점=*; 실제 저장 레코드=41

## S17 — Europe PMC

```text
(TITLE:steel OR TITLE:steels) AND TITLE:corrosion AND ("rare earth" OR cerium OR lanthanum) AND OPEN_ACCESS:Y NOT (TITLE:coating OR TITLE:inhibitor OR TITLE:review)
```

저장 응답 1개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 40개.

- `data/raw/europepmc/expansion_search.json`: API 전체 hit=40; 시작점=*; 실제 저장 레코드=40

## S18 — Europe PMC

```text
(TITLE_ABS:"cerium" OR TITLE_ABS:"lanthanum" OR TITLE_ABS:"rare earth" OR TITLE_ABS:"yttrium") AND (TITLE_ABS:"steel" OR TITLE_ABS:"iron") AND TITLE_ABS:"corrosion" AND OPEN_ACCESS:Y
```

저장 응답 1개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 45개.

- `data/raw/round300/pmc_search.json`: API 전체 hit=45; 시작점=*; 실제 저장 레코드=45

## S19 — Europe PMC

```text
(cerium OR lanthanum OR "rare earth") AND (steel OR steels OR "pure iron") AND corrosion AND OPEN_ACCESS:Y
```

저장 응답 1개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 99개.

- `data/raw/europepmc/search.json`: API 전체 hit=1800; 시작점=*; 실제 저장 레코드=100

## S20 — Europe PMC

```text
(cerium OR lanthanum OR yttrium OR "rare earth") AND (steel OR ferrous OR "Fe-based") AND corrosion AND DOI:10.1016* AND OPEN_ACCESS:Y
```

저장 응답 1개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 99개.

- `data/raw/elsevier_expansion/search.json`: API 전체 hit=184; 시작점=*; 실제 저장 레코드=100

## S21 — Springer Nature Metadata

```text
"rare earth" corrosion steel
```

저장 응답 1개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 25개.

- `data/raw/round300/query_4.json`: API 전체 hit=16766; 시작점=1; 실제 저장 레코드=25

## S22 — Springer Nature Metadata

```text
"rare earth" rebar corrosion
```

저장 응답 1개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 25개.

- `data/raw/round300/query_9.json`: API 전체 hit=135; 시작점=1; 실제 저장 레코드=25

## S23 — Springer Nature Metadata

```text
cerium corrosion stainless
```

저장 응답 1개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 25개.

- `data/raw/round300/query_5.json`: API 전체 hit=3334; 시작점=1; 실제 저장 레코드=25

## S24 — Springer Nature Metadata

```text
cerium corrosion steel
```

저장 응답 2개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 25개.

- `data/raw/add30_20261016/springer_search_0.json`: API 전체 hit=8143; 시작점=1; 실제 저장 레코드=25
- `data/raw/springer_meta_search.json`: API 전체 hit=8141; 시작점=1; 실제 저장 레코드=3

## S25 — Springer Nature Metadata

```text
cerium steel corrosion
```

저장 응답 1개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 25개.

- `data/raw/discovery/cerium_steel.json`: API 전체 hit=8141; 시작점=1; 실제 저장 레코드=25

## S26 — Springer Nature Metadata

```text
lanthanum corrosion stainless
```

저장 응답 1개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 25개.

- `data/raw/add30_20261016/springer_search_1.json`: API 전체 hit=2019; 시작점=1; 실제 저장 레코드=25

## S27 — Springer Nature Metadata

```text
lanthanum corrosion steel
```

저장 응답 1개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 25개.

- `data/raw/round300/query_6.json`: API 전체 hit=5077; 시작점=1; 실제 저장 레코드=25

## S28 — Springer Nature Metadata

```text
praseodymium corrosion steel
```

저장 응답 1개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 25개.

- `data/raw/round300/query_8.json`: API 전체 hit=915; 시작점=1; 실제 저장 레코드=25

## S29 — Springer Nature Metadata

```text
yttrium corrosion steel
```

저장 응답 2개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 29개.

- `data/raw/add30_20261016/springer_search_2.json`: API 전체 hit=6821; 시작점=1; 실제 저장 레코드=25
- `data/raw/round300/query_7.json`: API 전체 hit=6816; 시작점=1; 실제 저장 레코드=25

## S30 — Springer Nature Open Access

```text
"cerium" "steel" "corrosion"
```

저장 응답 1개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 25개.

- `data/raw/round300/query_10.json`: API 전체 hit=811; 시작점=1; 실제 저장 레코드=25

## S31 — Springer Nature Open Access

```text
"lanthanum" "steel" "corrosion"
```

저장 응답 1개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 25개.

- `data/raw/round300/query_11.json`: API 전체 hit=470; 시작점=1; 실제 저장 레코드=25

## S32 — Springer Nature Open Access

```text
"rare earth" "steel" "corrosion"
```

저장 응답 1개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 25개.

- `data/raw/discovery/ree_steel.json`: API 전체 hit=1337; 시작점=1; 실제 저장 레코드=25

## S33 — Springer Nature Open Access

```text
"rare earth" AND "corrosion current"
```

저장 응답 1개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 25개.

- `data/raw/springer_round/search_5.json`: API 전체 hit=207; 시작점=1; 실제 저장 레코드=25

## S34 — Springer Nature Open Access

```text
"rare earth" AND corrosion AND iron
```

저장 응답 1개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 25개.

- `data/raw/springer_round/search_4.json`: API 전체 hit=1192; 시작점=1; 실제 저장 레코드=25

## S35 — Springer Nature Open Access

```text
"rare earth" AND corrosion AND steel
```

저장 응답 1개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 25개.

- `data/raw/springer_round/search_0.json`: API 전체 hit=1337; 시작점=1; 실제 저장 레코드=25

## S36 — Springer Nature Open Access

```text
"rare earth" corrosion steel
```

저장 응답 54개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 1337개.

- `data/raw/springer_round/query6_start1.json`: API 전체 hit=1337; 시작점=1; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start1001.json`: API 전체 hit=1337; 시작점=1001; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start101.json`: API 전체 hit=1337; 시작점=101; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start1026.json`: API 전체 hit=1337; 시작점=1026; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start1051.json`: API 전체 hit=1337; 시작점=1051; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start1076.json`: API 전체 hit=1337; 시작점=1076; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start1101.json`: API 전체 hit=1337; 시작점=1101; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start1126.json`: API 전체 hit=1337; 시작점=1126; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start1151.json`: API 전체 hit=1337; 시작점=1151; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start1176.json`: API 전체 hit=1337; 시작점=1176; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start1201.json`: API 전체 hit=1337; 시작점=1201; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start1226.json`: API 전체 hit=1337; 시작점=1226; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start1251.json`: API 전체 hit=1337; 시작점=1251; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start126.json`: API 전체 hit=1337; 시작점=126; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start1276.json`: API 전체 hit=1337; 시작점=1276; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start1301.json`: API 전체 hit=1337; 시작점=1301; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start1326.json`: API 전체 hit=1337; 시작점=1326; 실제 저장 레코드=12
- `data/raw/springer_round/query6_start151.json`: API 전체 hit=1337; 시작점=151; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start176.json`: API 전체 hit=1337; 시작점=176; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start201.json`: API 전체 hit=1337; 시작점=201; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start226.json`: API 전체 hit=1337; 시작점=226; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start251.json`: API 전체 hit=1337; 시작점=251; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start26.json`: API 전체 hit=1337; 시작점=26; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start276.json`: API 전체 hit=1337; 시작점=276; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start301.json`: API 전체 hit=1337; 시작점=301; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start326.json`: API 전체 hit=1337; 시작점=326; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start351.json`: API 전체 hit=1337; 시작점=351; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start376.json`: API 전체 hit=1337; 시작점=376; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start401.json`: API 전체 hit=1337; 시작점=401; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start426.json`: API 전체 hit=1337; 시작점=426; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start451.json`: API 전체 hit=1337; 시작점=451; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start476.json`: API 전체 hit=1337; 시작점=476; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start501.json`: API 전체 hit=1337; 시작점=501; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start51.json`: API 전체 hit=1337; 시작점=51; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start526.json`: API 전체 hit=1337; 시작점=526; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start551.json`: API 전체 hit=1337; 시작점=551; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start576.json`: API 전체 hit=1337; 시작점=576; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start601.json`: API 전체 hit=1337; 시작점=601; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start626.json`: API 전체 hit=1337; 시작점=626; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start651.json`: API 전체 hit=1337; 시작점=651; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start676.json`: API 전체 hit=1337; 시작점=676; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start701.json`: API 전체 hit=1337; 시작점=701; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start726.json`: API 전체 hit=1337; 시작점=726; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start751.json`: API 전체 hit=1337; 시작점=751; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start76.json`: API 전체 hit=1337; 시작점=76; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start776.json`: API 전체 hit=1337; 시작점=776; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start801.json`: API 전체 hit=1337; 시작점=801; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start826.json`: API 전체 hit=1337; 시작점=826; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start851.json`: API 전체 hit=1337; 시작점=851; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start876.json`: API 전체 hit=1337; 시작점=876; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start901.json`: API 전체 hit=1337; 시작점=901; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start926.json`: API 전체 hit=1337; 시작점=926; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start951.json`: API 전체 hit=1337; 시작점=951; 실제 저장 레코드=25
- `data/raw/springer_round/query6_start976.json`: API 전체 hit=1337; 시작점=976; 실제 저장 레코드=25

## S37 — Springer Nature Open Access

```text
"rare earth" corrosion steel microalloying
```

저장 응답 4개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 82개.

- `data/raw/springer_round/query2_start1.json`: API 전체 hit=82; 시작점=1; 실제 저장 레코드=25
- `data/raw/springer_round/query2_start26.json`: API 전체 hit=82; 시작점=26; 실제 저장 레코드=25
- `data/raw/springer_round/query2_start51.json`: API 전체 hit=82; 시작점=51; 실제 저장 레코드=25
- `data/raw/springer_round/query2_start76.json`: API 전체 hit=82; 시작점=76; 실제 저장 레코드=7

## S38 — Springer Nature Open Access

```text
cerium AND corrosion AND steel
```

저장 응답 1개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 25개.

- `data/raw/springer_round/search_1.json`: API 전체 hit=811; 시작점=1; 실제 저장 레코드=25

## S39 — Springer Nature Open Access

```text
cerium corrosion stainless
```

저장 응답 18개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 450개.

- `data/raw/springer_round/query4_start1.json`: API 전체 hit=450; 시작점=1; 실제 저장 레코드=25
- `data/raw/springer_round/query4_start101.json`: API 전체 hit=450; 시작점=101; 실제 저장 레코드=25
- `data/raw/springer_round/query4_start126.json`: API 전체 hit=450; 시작점=126; 실제 저장 레코드=25
- `data/raw/springer_round/query4_start151.json`: API 전체 hit=450; 시작점=151; 실제 저장 레코드=25
- `data/raw/springer_round/query4_start176.json`: API 전체 hit=450; 시작점=176; 실제 저장 레코드=25
- `data/raw/springer_round/query4_start201.json`: API 전체 hit=450; 시작점=201; 실제 저장 레코드=25
- `data/raw/springer_round/query4_start226.json`: API 전체 hit=450; 시작점=226; 실제 저장 레코드=25
- `data/raw/springer_round/query4_start251.json`: API 전체 hit=450; 시작점=251; 실제 저장 레코드=25
- `data/raw/springer_round/query4_start26.json`: API 전체 hit=450; 시작점=26; 실제 저장 레코드=25
- `data/raw/springer_round/query4_start276.json`: API 전체 hit=450; 시작점=276; 실제 저장 레코드=25
- `data/raw/springer_round/query4_start301.json`: API 전체 hit=450; 시작점=301; 실제 저장 레코드=25
- `data/raw/springer_round/query4_start326.json`: API 전체 hit=450; 시작점=326; 실제 저장 레코드=25
- `data/raw/springer_round/query4_start351.json`: API 전체 hit=450; 시작점=351; 실제 저장 레코드=25
- `data/raw/springer_round/query4_start376.json`: API 전체 hit=450; 시작점=376; 실제 저장 레코드=25
- `data/raw/springer_round/query4_start401.json`: API 전체 hit=450; 시작점=401; 실제 저장 레코드=25
- `data/raw/springer_round/query4_start426.json`: API 전체 hit=450; 시작점=426; 실제 저장 레코드=25
- `data/raw/springer_round/query4_start51.json`: API 전체 hit=450; 시작점=51; 실제 저장 레코드=25
- `data/raw/springer_round/query4_start76.json`: API 전체 hit=450; 시작점=76; 실제 저장 레코드=25

## S40 — Springer Nature Open Access

```text
cerium corrosion steel
```

저장 응답 1개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 3개.

- `data/raw/springer_oa_search.json`: API 전체 hit=811; 시작점=1; 실제 저장 레코드=3

## S41 — Springer Nature Open Access

```text
cerium corrosion steel microalloying
```

저장 응답 2개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 37개.

- `data/raw/springer_round/query0_start1.json`: API 전체 hit=37; 시작점=1; 실제 저장 레코드=25
- `data/raw/springer_round/query0_start26.json`: API 전체 hit=37; 시작점=26; 실제 저장 레코드=12

## S42 — Springer Nature Open Access

```text
lanthanum AND corrosion AND steel
```

저장 응답 1개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 25개.

- `data/raw/springer_round/search_2.json`: API 전체 hit=470; 시작점=1; 실제 저장 레코드=25

## S43 — Springer Nature Open Access

```text
lanthanum corrosion steel
```

저장 응답 19개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 470개.

- `data/raw/springer_round/query5_start1.json`: API 전체 hit=470; 시작점=1; 실제 저장 레코드=25
- `data/raw/springer_round/query5_start101.json`: API 전체 hit=470; 시작점=101; 실제 저장 레코드=25
- `data/raw/springer_round/query5_start126.json`: API 전체 hit=470; 시작점=126; 실제 저장 레코드=25
- `data/raw/springer_round/query5_start151.json`: API 전체 hit=470; 시작점=151; 실제 저장 레코드=25
- `data/raw/springer_round/query5_start176.json`: API 전체 hit=470; 시작점=176; 실제 저장 레코드=25
- `data/raw/springer_round/query5_start201.json`: API 전체 hit=470; 시작점=201; 실제 저장 레코드=25
- `data/raw/springer_round/query5_start226.json`: API 전체 hit=470; 시작점=226; 실제 저장 레코드=25
- `data/raw/springer_round/query5_start251.json`: API 전체 hit=470; 시작점=251; 실제 저장 레코드=25
- `data/raw/springer_round/query5_start26.json`: API 전체 hit=470; 시작점=26; 실제 저장 레코드=25
- `data/raw/springer_round/query5_start276.json`: API 전체 hit=470; 시작점=276; 실제 저장 레코드=25
- `data/raw/springer_round/query5_start301.json`: API 전체 hit=470; 시작점=301; 실제 저장 레코드=25
- `data/raw/springer_round/query5_start326.json`: API 전체 hit=470; 시작점=326; 실제 저장 레코드=25
- `data/raw/springer_round/query5_start351.json`: API 전체 hit=470; 시작점=351; 실제 저장 레코드=25
- `data/raw/springer_round/query5_start376.json`: API 전체 hit=470; 시작점=376; 실제 저장 레코드=25
- `data/raw/springer_round/query5_start401.json`: API 전체 hit=470; 시작점=401; 실제 저장 레코드=25
- `data/raw/springer_round/query5_start426.json`: API 전체 hit=470; 시작점=426; 실제 저장 레코드=25
- `data/raw/springer_round/query5_start451.json`: API 전체 hit=470; 시작점=451; 실제 저장 레코드=20
- `data/raw/springer_round/query5_start51.json`: API 전체 hit=470; 시작점=51; 실제 저장 레코드=25
- `data/raw/springer_round/query5_start76.json`: API 전체 hit=470; 시작점=76; 실제 저장 레코드=25

## S44 — Springer Nature Open Access

```text
lanthanum corrosion steel microalloying
```

저장 응답 1개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 21개.

- `data/raw/springer_round/query1_start1.json`: API 전체 hit=21; 시작점=1; 실제 저장 레코드=21

## S45 — Springer Nature Open Access

```text
yttrium AND corrosion AND steel
```

저장 응답 1개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 25개.

- `data/raw/springer_round/search_3.json`: API 전체 hit=548; 시작점=1; 실제 저장 레코드=25

## S46 — Springer Nature Open Access

```text
yttrium corrosion steel
```

저장 응답 22개; 이 검색식의 저장 응답 안에서 확인된 고유 DOI 548개.

- `data/raw/springer_round/query3_start1.json`: API 전체 hit=548; 시작점=1; 실제 저장 레코드=25
- `data/raw/springer_round/query3_start101.json`: API 전체 hit=548; 시작점=101; 실제 저장 레코드=25
- `data/raw/springer_round/query3_start126.json`: API 전체 hit=548; 시작점=126; 실제 저장 레코드=25
- `data/raw/springer_round/query3_start151.json`: API 전체 hit=548; 시작점=151; 실제 저장 레코드=25
- `data/raw/springer_round/query3_start176.json`: API 전체 hit=548; 시작점=176; 실제 저장 레코드=25
- `data/raw/springer_round/query3_start201.json`: API 전체 hit=548; 시작점=201; 실제 저장 레코드=25
- `data/raw/springer_round/query3_start226.json`: API 전체 hit=548; 시작점=226; 실제 저장 레코드=25
- `data/raw/springer_round/query3_start251.json`: API 전체 hit=548; 시작점=251; 실제 저장 레코드=25
- `data/raw/springer_round/query3_start26.json`: API 전체 hit=548; 시작점=26; 실제 저장 레코드=25
- `data/raw/springer_round/query3_start276.json`: API 전체 hit=548; 시작점=276; 실제 저장 레코드=25
- `data/raw/springer_round/query3_start301.json`: API 전체 hit=548; 시작점=301; 실제 저장 레코드=25
- `data/raw/springer_round/query3_start326.json`: API 전체 hit=548; 시작점=326; 실제 저장 레코드=25
- `data/raw/springer_round/query3_start351.json`: API 전체 hit=548; 시작점=351; 실제 저장 레코드=25
- `data/raw/springer_round/query3_start376.json`: API 전체 hit=548; 시작점=376; 실제 저장 레코드=25
- `data/raw/springer_round/query3_start401.json`: API 전체 hit=548; 시작점=401; 실제 저장 레코드=25
- `data/raw/springer_round/query3_start426.json`: API 전체 hit=548; 시작점=426; 실제 저장 레코드=25
- `data/raw/springer_round/query3_start451.json`: API 전체 hit=548; 시작점=451; 실제 저장 레코드=25
- `data/raw/springer_round/query3_start476.json`: API 전체 hit=548; 시작점=476; 실제 저장 레코드=25
- `data/raw/springer_round/query3_start501.json`: API 전체 hit=548; 시작점=501; 실제 저장 레코드=25
- `data/raw/springer_round/query3_start51.json`: API 전체 hit=548; 시작점=51; 실제 저장 레코드=25
- `data/raw/springer_round/query3_start526.json`: API 전체 hit=548; 시작점=526; 실제 저장 레코드=23
- `data/raw/springer_round/query3_start76.json`: API 전체 hit=548; 시작점=76; 실제 저장 레코드=25

