# Route-order rebuild v3 (decoder `s4/s4decoder1.py`, H000001 to H003218)

Done and checked
- Decoder: B 20 inserted (H000002), D row heads relabelled to the printed lots (20H, 9H, 40H … 300H) and plain D 311/322/333, nine C H-twins, L strip 1-13 between M and K. Self-test passes; formula layer, explainer and tables agree (verify.py 3250/3250, test_giant.js 3248/3248).
- Shift tables against the review commit d990927: `crosswalk/shift_table_lots.csv`, `shift_runs.csv`, `shift_boundaries.csv`, `shift_focus_B20.csv` (`pipeline2/shift_table.py`). 28 lots inserted, 2,360 shifted.
- H-Tables (all 13 sections) regenerated from the decoder (`pipeline2/export_tables.py`); crosswalk to every section (`crosswalk_v1_to_v2.csv`, `records_h_ids_v2.csv` with v1, review-commit and current IDs per workbook grave, search page); 0 failures.
- Pipeline rerun with the decoder; L-strip fix (labels 1-13 inside the L boundary decode in Section L; five cells had carried the wrong lot's number). 3,196 numbered lots.
- Grave sheets J, K, M regenerated from verified lot, row and grave: 2,173 workbook graves, each printed once, 0 missing or wrong.
- Inventory-first verification (`pipeline2/verify_inventory.py`): blank H fails, workbook grave without a readable ID fails, no grave count is claimed for sections without a workbook or plat.
- Overview sheet design corrections (`pipeline2/build_overall.py`): single section letters in clear lanes with leaders that cross no number, enlarged framed details (crypt court, cremains strip) in the open south-west with references on the map, displaced M numbers in one straight row per run with the boundary broken behind each label, grid letters in opaque bands, opaque clear band before the footer, status line "Review copy · N outlines under review" with the amber-outline meaning, dark historical lot labels. Print-size crop checks: `pipeline2/verify_crops.py` (F/M, crypt court, B chapel, E/C bottom edge) -> `crosswalk/crop_checks.txt`, `crosswalk/crops/`.

Not done
- B 395-414 (20 lots) is analysed, not applied (deck slide Q15). Other identified outlines without a table number (B 308H/326H/344H/362H, A361/A362, A-suffix strips, L 14-19/21, c371, …) wait for Jon.
- The 3D view and tree map reuse the same base; the tree map was rebuilt, the 3D view was not touched.
