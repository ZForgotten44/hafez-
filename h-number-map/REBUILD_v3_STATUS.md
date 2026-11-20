# Route-order rebuild v3: what is done and what is not (state at this commit)

Done and checked
- `s4/s4decoder1.py` (production decoder): B 20 inserted (H000002; 19A…1 move one place later inside row 1), D row heads relabelled to the printed lots (20H…300H, plus 20H and 9H in row 1), plain D 311/322/333, nine C H-twins, L strip 1-13 (between M and K). Self-test 50/50.
- Formula layer (`math/hformula.py`, `gen_giant.py`, `verify.py` 3250/3250, `test_giant.js` 3248/3248) and the explainer rebuilt for the new totals (3,218 route positions).
- `crosswalk/shift_table_lots.csv` (every physical lot: section, label, review-commit H, new H, shift, reason), `shift_runs.csv` (first/last lot of each continuous run), `shift_boundaries.csv` (net shift at each section boundary), `shift_focus_B20.csv` (20H, 20, 19A and neighbours). Built by `pipeline2/shift_table.py` against commit d990927. Result: 28 lots inserted, 2,360 shifted (+1 within B row 1, +2…+14 through pass 5, +14 for M, +27 for K, J, I, L 69-107).
- Pipeline rerun with decoder v3 (identify → finalize → fit): `data/registry.json` now has 3,193 numbered lots; 111 outlines unnumbered (64 mausoleum crypts, 10 cremains niches, 47 outlines without a table number).
- `deck-jon/`: the 22-slide Jon deck (`Cedar_Grove_Questions_for_Jon.pptx` and `.pdf`) with its image generators.

Not done yet
- B 395-414 (20 lots): analysis only (candidate (a) after H000836 adds 13 route units, candidate (b) before H000001 adds 275); not applied, pending Jon (deck slide Q15).
- Remaining unnumbered identified outlines (B 308H/326H/344H/362H, A361/A362, A-suffix strips, L 14-19/21, c371) are not in the table.
- H-Tables, crosswalk_v1_to_v2, search page, grave sheets, maps (PDF/site/3D/poster), the physical-lot/grave-first verification and the overview-sheet design corrections are NOT regenerated in this commit; those files still show the review-commit numbering.
