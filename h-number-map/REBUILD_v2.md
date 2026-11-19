# Numbering v2: what changed and where to find it

| What | Where |
|---|---|
| Production decoder v2 (H000001 to H003191) | `s4/s4decoder1.py` (v1 frozen as `s4/s4decoder_v1.py`) |
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
| Questions for Jon with annotated images | `jon_questions/QUESTIONS.md` |
| Evidence and route for Section M | `section_M_check.md`, `old_map_check.md` |

Rebuild after a decoder change: `python3 pipeline2/run_all.py --no-qa` then `python3 pipeline2/crosswalk.py`, `python3 pipeline2/build_overall.py`, `python3 pipeline2/build_overall.py --trees`, `python3 pipeline2/verify_final.py`, and in `math/`: `extract_decoder.py`, `gen_giant.py`, `build_data.py`, `build_explainer.py`, `build_3d_data.py`, `build_3d.py public`.

Not updated: the slide decks in `deck/` and `deck-local/` and the published artifact pages still show 3,185 and the v1 Section M ranges.
