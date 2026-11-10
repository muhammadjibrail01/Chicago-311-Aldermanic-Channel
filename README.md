# Replication package: "Who Calls the Alderman? The Aldermanic Channel and the Racial Gradient in Chicago's 311 Queue"

This package reproduces the analyses and the manuscript, including the election analysis of Section 5.7. Run every script from this folder (`python code/NN_name.py`); all paths are relative to it.

## Inputs
| Input | Where | Notes |
|---|---|---|
| Processed core request file `core_request_file.parquet` (4,648,843 requests) | `work/`, or set `CORE_ZIP` to the Paper 3 package zip, which holds it at `p3pkg/data/core_request_file.parquet` | built from the 311 service-request extracts by the companion studies' pipeline |
| Tract measures and boundaries (`tract.csv`, `data/tracts/cb_2023_17_tract_500k.shp`) | `../paper1_replication/work/`, or set `P1_WORK` | steps 00 and 02 of the Paper 1 package |
| Ward boundaries, 2015 map and 2023 map | downloaded by step 6 | github.com/paulsmith/chicago_wards_and_precincts (Board of Elections files); github.com/PaulPrice1/ChicagoWardGeoJSON (copy of the City data set) |
| Official canvass proclamations, April 2, 2019 and April 4, 2023 runoff elections | `data/official/` (included) | Board of Election Commissioners for the City of Chicago |
| Wikipedia pages for the 2019 and 2023 aldermanic and mayoral elections | `data/wiki/` (included; wikitext as retrieved in November 2026) | first-round returns, sitting aldermen, endorsements, 2019 ward-level mayoral vote |

## Election analysis: run order
| Step | Script | Produces |
|---|---|---|
| 1 (optional) | `code/01_fetch_wiki.py` | re-downloads the four Wikipedia pages into `data/wiki/` (archived copies are included; re-fetching returns the current revision) |
| 2 | `code/02_parse_official.py` | `data/official_runoff_results.csv`, `data/official_ballots_by_ward.csv`; 12 consistency checks |
| 3 | `code/03_parse_aldermanic.py` | `data/ward_elections.csv` (100 ward-periods); 11 integrity checks |
| 4 | `code/04_parse_mayoral.py` | `data/mayor2019_runoff_by_ward.csv`, `data/ward_alignment.csv`; 6 checks |
| 5 | `code/05_verify_compiled.py` | comparison of the compiled tables with the official proclamations; 6 checks |
| 6 | `code/06_build_data.py` | `work/p2_data.parquet`: resident requests located in tracts and in wards under both maps |
| 7 | `code/07_election_models.py` | `results/S19_election.json`: replication checks, Table 6, 2023 turnover |
| 8 | `code/08_turnover_full.py` | full-sample turnover model (Table 7) |
| 9 | `doc/build_content2.py`, `doc/build_content3.py` | `doc/content3.json`: text and tables of the paper |
| 10 | `node doc/render.js doc/content3.json Paper2.docx` | Word file |

`python run_all.py` runs steps 2 to 10 (steps 6 to 8 take about 25 minutes on one core with 4 GB). The typography used for the 15-page version is set by environment variables (`BODY_SZ=21 LINE_SP=252 PARA_AFTER=100 NOTE_SZ=15 MARGIN_TOP=1200 MARGIN_BOT=1100 TBL_SZ=16 FIG_SCALE=90`), which `run_all.py` sets.

## Earlier analyses (results S0 to S18)
Every analysis reads `work/p2_data.parquet`, which can be built in two ways.
* Route B (used for the election analysis): step 6 above builds it from the processed core request file.
* Route A (from the raw 311 extracts): put the 311 CSV extracts in `raw_data/raw311/` and run `make_core_raw.py` (writes `work/core_raw.parquet`), `build_core.py` (writes `work/core_request_file.parquet`), `make_ward_maps.py` and `make_ward_assign.py` (they read the two ward-map repositories unpacked into `work/` and write `work/ward_assign.parquet`), `build_p2.py` (also needs `tract.csv` and `core_locations.parquet` from the Paper 1 package) and `build_quality.py`. `make_ca_gpkg.py` builds the community-area polygon file (`work/ca.gpkg`) that the Paper 1 pipeline expects.

The analyses are `desc.py`, `m3c.py`, `m4.py`, `m6.py`, `diag2.py`, `make_s9.py`, `m7.py`, `m8.py`, `m8b.py`, `m9.py`, `m13.py`, `m10.py`, `m11.py`, `m12.py` and `m14.py`, followed by `figs.py` and `figs3.py` (long runs take 5 to 15 minutes each on one core with 4 GB). Route B's output reproduces the stored results of `m4.py` and `m12.py`. `p2lib.py` holds the loader and the clustered fixed-effects regression, which uses `fe.py`.

## Known features of the data
* The November 2019 break in the aldermanic series and the December 2022 overwrite of the recorded ward are features of the raw data and are not corrected.
* Five speed-sample records ("Budget Town Hall Meeting", "FY25 Budget Engagement", "Mayor's Office") are coded aldermanic because that reproduces the main paper's channel counts exactly; dropping them changes nothing material.
* The re-report means are within 0.04 percentage points of the main paper's, not identical.
* The paper's figures and tables 6 and 7 of the previous version (resolution outcomes; robustness) were removed from the text to fit the page limit; their results remain in `results/` (S10, S16, S5) and `doc/content2.json`.
