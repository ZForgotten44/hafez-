# Tree inventory: 415 versus 414

**Result: the earlier 415-tree list is recoverable and is the inventory.** `trees.json` (T001 to T415) equals the `trees` list embedded in the shipped `site/3d.html` exactly, coordinate for coordinate (315 detected crowns, 100 woods-fill trees; 7 evergreen).

## The one difference

| Tree | x | y | radius | origin | Missing from |
|---|---|---|---|---|---|
| (old index 275, now T275 again) | 710.7 | 325.7 | 9.6 | detected, leafy | the regenerated 414 list |

Matching by coordinates (within 1.5 units and 1.5 radius) left exactly one unmatched tree and no duplicates or additions.

## Cause

Not the random fill (it is seeded: `default_rng(7)`) and not the road mask. `extract_buildings.py` kept footprints that are not within 16 units of a lot centre, and took the lot centres from `lots_fit.json`, which only holds *numbered* lots. After the review cases were closed, two Section I lots (labels 18 and 19, at x 695 and 686, y 338, left without an H-number) were no longer in that list, so their outlines were read as two extra "houses" (31 vs 30 buildings after the hand corrections). The drop-near-building rule (8 + 0.8 r) then removed the tree at (710.7, 325.7).

## Fix (no other behaviour changed)

- `math/extract_buildings.py` now takes lot centres from every drawn cell (`cells.json`), numbered or not, so the building list no longer depends on numbering decisions. Result: the original 30 buildings, and 415 trees identical to the old list.
- `math/build_3d_data.py` records where the woods fill starts and calls `math/export_trees.py`, which writes `trees.json` (stable ids, x, y, crown radius, leafy or evergreen, detected or woods fill).
- Verified: two consecutive runs give byte-identical `trees.json`.

Maps should read `trees.json`, not regenerate trees.

## Restroom

No evidence in the repository: no facilities plan, and the word does not occur in any CSV, markdown, HTML, PDF text or in the drawing's text objects (only "Cemetery maintenance building" and "Cottage (office)"). The only source naming it is the old overall sheet, where a RESTROOM label with a leader stands beside a MAINTENANCE BUILDING label near the parking, but the leaders end at different small objects and the sheet predates the 2022 drawing. The label at (1330, 341) is therefore unconfirmed; it should be dropped from published maps until grounds staff confirm.
