# Audit notes: completed version with the election analysis

## Checks performed
| Check | Result |
|---|---|
| The analysis file rebuilt from the processed core file reproduces the stored results of the previous version | Speed sample 3,055,485 (phone 1,541,417; web/app 1,224,608; aldermanic 289,460); Black-share interaction -0.1232 (SE 0.0176) and Black-share coefficient 0.1689, both equal to the stored values; comparable-closure sample 2,896,497 with within-tract aldermanic gap 0.1299 (SE 0.0130) and Black-share interaction -0.0779, equal to the stored values |
| Official proclamations parsed (`02_parse_official.py`) | 12 of 12 checks pass: contests parsed equal the wards named on each cover (15 in 2019, 14 in 2023); each contest has two candidates whose votes sum to the printed total; printed percentages equal votes/total (largest gap 0.005); ballots cast reported for all 50 wards and equal to the printed turnout (526,886; 613,795); mayoral totals sum to the printed totals (523,804; 612,514) |
| Compiled tables against the proclamations (`05_verify_compiled.py`) | 6 of 6 checks pass: all 58 runoff candidates, their vote totals, the 29 winners and the 29 margins are identical; the compiled 2019 ward-level mayoral votes sum to the official citywide totals (386,039; 137,765); no ward's mayoral votes exceed its official ballots cast (difference 15 to 232 ballots; 3,082 in all, 0.58 percent) |
| Compiled aldermanic tables (`03_parse_aldermanic.py`) | 11 of 11 checks pass (flagged winner is the top vote-getter and runoff pairs are the first-round top two; stated percentages equal votes/total; one general-election box per ward; two candidates per runoff; a runoff occurs exactly when no first-round majority; five unopposed wards and seven defeated incumbents in 2019 as stated on the page; twelve new aldermen in 2019; 14 runoffs and one defeated incumbent in 2023) |
| Compiled mayoral tables (`04_parse_mayoral.py`) | 6 of 6 checks pass (2019 ward table has 50 wards; ward votes sum to the citywide totals; Lightfoot won all wards with shares of 54.4 to 87.5 percent, equal to the page's map legend; percentages equal votes/total; 2023 endorsements by sitting aldermen: Vallas 22, equal to the page's legend, and Johnson 13 against the legend's 14) |
| Models and text | `results/S19_election.json` holds all election models; `doc/build_content3.py` asserts every qualitative statement of the new text against those results (for example, the number of significant aldermanic coefficients: 1 of 10 at 5 percent, 2 of 10 at 10 percent; none of the 10 web/app placebo coefficients at 10 percent) and stops if one fails |
| 2023 turnover, full speed sample | aldermanic -0.131 (SE 0.056) and web/app -0.073 (SE 0.028), close to the corresponding estimates of the earlier election analysis (-0.125 and -0.066) |
| Document | 15 pages in a LibreOffice rendering; Word file checked against an Office Open XML schema validator; no dangling references to removed tables or figures (asserted in the builder) |

## Test from this package folder
The package was unpacked next to a Paper 1 work folder (tract measures and boundaries) with the processed core request file in `work/`, and run from its own folder with the default folder settings.
* Steps 2 to 5: 12, 11, 6 and 6 checks pass (35 of 35).
* Step 6 rebuilt the analysis file: 4,232,673 resident requests in the 789 tracts, of which 3,055,485 are in the speed sample (phone 1,541,417; web/app 1,224,608; aldermanic 289,460), the same counts as the stored results.
* Step 7 was run from scratch with the stored model results removed and was stopped after seven minutes. The six results it had produced (the two replication checks and the seat-safety, runoff and new-office-holder, combined, and official-runoff-margin models) were identical to the stored ones. Step 8 (full-sample turnover) ran to completion and was identical to the stored result. The alignment models, the robustness runs and the comparable-closure turnover model were not recomputed in this test.
* Steps 9 and 10: `doc/content2.json` regenerated identical to the shipped file; the manuscript rebuilt from the package has the same text as the delivered Word file (10,406 words) and renders at 15 pages.
* Earlier analysis scripts: `desc.py`, `m8b.py`, `m13.py`, `m14.py`, `figs.py` and `figs3.py` ran to completion (the quintile shares printed by `desc.py` are those of Table 2); `m3c.py`, `m4.py`, `m6.py`, `m8.py`, `m9.py`, `m10.py`, `m11.py` and `m12.py` got past loading and were stopped after 30 to 70 seconds (the usage estimates printed by `m3c.py` match Section 5.1). Scripts that need inputs outside the package stop at the first missing input: `m7.py` (`work/quality_flags.parquet`), `diag2.py`, `build_quality.py` and `build_core.py` (`work/core_raw.parquet`), `make_s9.py` (`work/repeat_flags.parquet`), `build_p2.py` (`core_locations.parquet` from the Paper 1 package), `make_core_raw.py` (the raw 311 extracts), and `make_ward_maps.py`, `make_ward_assign.py` and `make_ca_gpkg.py` (their downloads).

## Data problems found in the compiled tables
* Three result boxes on the 2019 aldermanic page carry the wrong ward in their titles (ward 19's box is titled 16th, ward 42's 43rd, and the ward 15 runoff 39th). Boxes were assigned to wards by the page section they sit in and checked against candidate names.
* The same page states 14 runoff wards in 2019, while its boxes and the official proclamation show 15 (the ward 15 runoff is the one the prose omits).
* The 2023 page states that five incumbents won runoffs; its boxes show six (one of them an appointee flagged as incumbent).

## Limits of the verification
* First-round returns, the identity of sitting aldermen, endorsements, and the 2019 ward-level mayoral vote are not in the official files supplied. They come from compiled public tables that agree with the proclamations wherever the two overlap but could not be checked against the Board's first-round canvass. The 2023 ward-level mayoral vote is not available.
* The endorsement lists are validated only against the page's own legend.
* Alignment by endorsement is defined for aldermen who held their ward before and after the election; 100 ward-periods (29 runoff contests; 70 classified aldermen) allow only large effects to be ruled out.
* The new interaction models were not cross-validated with a second software package.
* Checks on the earlier results (spatial re-assignment of 3,000 requests, a cross-check of the fixed-effects estimator, a number ledger) are documented with the previous version and were not repeated.

## Changes from the previous version
Added: Sections 2.1 (electoral incentives), 3.4, 4 (Equation 3), 5.7, discussion, limitations and conclusion text; Tables 6 and 7; five references (two proclamations, Cain et al., Christensen and Ejdemyr, four Wikipedia pages). Removed to stay within 15 pages: Figures 2, 3, 4 and 5; the previous Tables 6 and 7; the appendix of request types; a paragraph of the declarations.

## Corrections to the code in this version
* All scripts use paths relative to the package folder. Six older scripts that loaded a bare `p2_data.parquet` (`desc.py`, `diag2.py`, `m3c.py`, `m7.py`, `m9.py`, `make_s9.py`) now read `work/p2_data.parquet`. Four scripts that read a separate main-paper `core.parquet` (`build_p2.py`, `build_quality.py`, `m14.py`, `m7.py`) now read `work/core_request_file.parquet`, the file step 6 uses. The raw-extract scripts and the files they pass on (`core_raw.parquet`, `ward_*.gpkg`, `ward_assign.parquet`, `quality_flags.parquet`, `repeat_flags.parquet`, `ca.gpkg`) are kept in `work/`, and the raw 311 extracts are read from `raw_data/raw311/`.
* `figs.py` skips a robustness row (excluding wards with a mid-term change of alderman) that is not in the stored results; the script stopped on it before.
