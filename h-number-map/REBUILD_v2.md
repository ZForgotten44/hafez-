# Numbering v2: what changed and where to find it

| What | Where |
|---|---|
| Production decoder v2 (H000001 to H003218) | `s4/s4decoder1.py` (v1 frozen as `s4/s4decoder_v1.py`) |
| East-tip switch (M 11, 12, 16) | `M_EASTTIP_STATUS` in `s4/s4decoder1.py`: `'active'` (shipped) or `'withdrawn'` |
| Section tables | `H-Tables/cedar_grove_section_{M,K,J,I,L}_h_table.csv` regenerated |
| Formula, explainer | `math/hformula.py`, `giant_formula.js` (3,203 of 3,203 labels match the decoder), `Cedar_Grove_Numbering_Explained.html` |
| Before/after list, one line per affected grave | `crosswalk/crosswalk_v1_to_v2.csv` (2,681 graves, 574 lots); if M 11, 12, 16 are withdrawn: `crosswalk_v1_to_v2_if_east_tip_withdrawn.csv` |
| Search by old or new ID, in either map version | `crosswalk/crosswalk_search.html` (single file) |
| Burial-workbook graves with old and new H-ID, no names | `crosswalk/records_h_ids_v2.csv` |
| Label aliases (B 318H = 320H ...) | `crosswalk/label_aliases.csv` |
| What was verified | `crosswalk/crosswalk_checks.txt`, `crosswalk/verification_report.txt` |
| Maps | `site/pdf/Cedar_Grove_H-Number_Map_overall.pdf`, `Cedar_Grove_Tree_Map_overall.pdf`, `Cedar_Grove_H-Map_area_*.pdf`, `Cedar_Grove_Crypts_and_Cremains_detail.pdf`, the atlas `site/index.html`, the 3D page `site/3d.html` |
| Crypts and cremains niches, own numbering | `special_locations.csv` (148 rows), the atlas search ("crypt 12", "niche 12") |
| Tree inventory | `trees.json` (415, frozen), `trees_reconciliation.md` |
| Grave-level sheets (every grave of J, K, M with its 7-digit ID, vacant included) | `site/pdf/Cedar_Grove_Grave_IDs_{J,K,M}.pdf`, `grave_positions_JKM.csv` |
| Inventory of the 139 grey shapes | `grey_inventory.csv` (class, identity, sources, status), `pipeline2/refresh_inventory.py` |
| Section B and D corrections (v2) | B: last-column rule removed, plain lots 40 to 360 numbered; D 293; see `crosswalk/crosswalk_v1_to_v2.csv` column `reason` |
| Questions for Jon with annotated images | `jon_questions/QUESTIONS.md` |
| Evidence and route for Section M | `section_M_check.md`, `old_map_check.md` |

Rebuild after a decoder change: `python3 pipeline2/run_all.py --no-qa` then `python3 pipeline2/crosswalk.py`, `python3 pipeline2/build_overall.py`, `python3 pipeline2/build_overall.py --trees`, `python3 pipeline2/verify_final.py`, and in `math/`: `extract_decoder.py`, `gen_giant.py`, `build_data.py`, `build_explainer.py`, `build_3d_data.py`, `build_3d.py public`.

Not updated: the slide decks in `deck/` and `deck-local/` and the published artifact pages still show 3,185 and the v1 Section M ranges.

## Review status of the overall H-number map (REVIEW COPY)

Two-way check, run by `pipeline2/verify_map.py` and `pipeline2/verify_grave_sheets.py` (results in `crosswalk/map_verification.txt` and `crosswalk/grave_sheets_verification.txt`):

| Total | Count |
|---|---|
| Confirmed graves or lots missing a visible ID (3,167 numbered lots on the overview; 2,173 workbook graves of J, K, M on the grave sheets) | **0** |
| Visible IDs pointing to the wrong place (printed numbers not at the lot they name, leaders ending elsewhere) | **0** |
| Outlines still awaiting a number or an identification | **69** (47 lot identified, route position undecided; 22 identity not settled) |

The 139 grey shapes of the earlier export are in `grey_inventory.csv`, one row each: native numbering (crypt) 50, awaiting identification 22, awaiting a number (lot identified) 47, not a grave 4, numbered 16. The 69 awaiting outlines are drawn amber with their old label in amber (not an H-number); `jon_questions/QUESTIONS.md` (Q8 to Q17) has an image and the evidence needed for each cluster. Individual grave IDs exist only for J, K and M (burial workbooks); for A to I and L no grave is confirmed by a record, so lots are numbered and a grave is that number plus a digit 1 to 9.
