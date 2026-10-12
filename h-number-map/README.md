# Cedar Grove Cemetery - H-Number Map

An interactive map and printable PDFs that show every lot with its **H-number**, built from the cemetery's CAD drawing
(`Ground Maps/Cedar Grove 2022 with CR.ai`) and the decoder (`s4/s4decoder1.py`).

* **`site/index.html`** - the interactive map (one file). Search by H-number, legacy lot or recorded name; click any lot.
* **`site/pdf/`** - PDFs drawn from the same data: `Cedar_Grove_H-Map_full.pdf` (42 x 24 in overview + 14 tabloid detail pages +
  unresolved-locations appendix), `..._overview.pdf`, and one PDF per legacy area.
* **`verified_lots.csv`**, **`unresolved_locations.csv`** - plain lists.
* **`pipeline2/`** - the build. `python3 pipeline2/run_all.py` regenerates everything from the repo (about 6 minutes). See `pipeline2/README.md`.
* `pipeline/`, `placed_lots.csv`, `lots_not_placed_on_map.csv`, `map_labels_not_in_decoder.csv`, the 44x34in and letter-tile PDFs -
  the earlier OCR-based build. Superseded; kept for reference. (Its scripts need two source PDFs that are not in the repo.)

## What changed in this version

The old map was redrawn from a PDF whose lot numbers were vector strokes, so old numbers sat under the new ones and
labels sat off-centre. The CAD drawing keeps lot numbers as **real text** and lot outlines as separate lines, so:

* No legacy annotation is part of the map. Section titles, chapel/parking/office notes and the mausoleum legend are text in the
  source and are simply not drawn. Roads, curbs, building and mausoleum footprints and every lot outline are kept.
  Original text can be switched on in **Layers > Original drawing annotations** (road names, building names, mausoleum legend from the CAD file).
  The old overall map's maroon "SECTION X" blocks are not in the CAD file, so that layer does not reproduce them.
* Nothing is erased or covered, so nothing can be erased by mistake. There are no white patches.
* Each number is fitted inside its own outline: centred, aligned, inset by a clear margin, never clipped, never overlapping.

## Result

| | lots |
|---|---|
| Verified H-number and verified outline | **3,103** (3,102 drawn outlines + 1 label whose outline is not drawn) |
| - section confirmed by two independent readings | 2,709 |
| - section inferred from surrounding lots | 394 |
| Visible on the map, identity unresolved ("needs review") | **218** |
| Known to the decoder, no position on the map | **68** |

Needs-review lots are tinted with a dashed amber outline and carry **no** number. Their decoder candidate (when there is one) is
shown only in the details panel, marked as a candidate. Reasons: label not in the legacy section this part of the map belongs to (77),
label exists in many sections and the area has no region evidence, mostly the mausoleum garden rows (72), the same legacy label twice
in one section (28), H-number far from its neighbours (20), label unknown to the decoder (12), outline with no label (9).
All of them are in `unresolved_locations.csv`, the site's **To review** tab and the last PDF pages.

Open human decisions (unchanged from before, now visible as concrete lots): Section B 373-380H collision (the margin-strip
numbers sit in the main grid), Section G duplicate `19`, Section A `20H, 39H ... 343H` (map shows plain `20`, `39`), the B/C/D
labels 395-414 and 320/340/360/344H/362H/308H/326H on the Section B side, the mausoleum-garden rows, and the per-lot grave capacity.
Three lots are verified but too small to carry a legible number (E 195A, E 195B, H 21): they are clickable and listed.

## Checks that ran (pipeline2/qa.py)

1. Every number's measured text box lies inside its own lot with clearance, clear of every drawn lot line, and overlaps no other number: **3,103 / 3,103**.
2. Traced lot outlines versus the drawn lines: worst deviation 0.62 drawing units (line half-width is 0.36).
3. Pixel test in a real browser: of 773,021 number pixels, **0** touch a lot line.
4. The same test on the rendered PDF pages: **0** of 1.74 million number pixels touch a lot line; every number is in the PDF text layer.
Detail pages overlap by 36 units (more than the largest lot) and each lot and its number are placed on a page that shows the lot whole.

## Using the site

* Click a lot: the map zooms to it, highlights it and opens its panel (H-number, legacy reference, how it was verified, grave information).
  Grave information starts empty ("Grave count not verified", "No grave records entered yet"). Nine positions are never generated.
* Search accepts `H001914`, `1914`, `H0019141` (grave id, shows the lot), `F 34`, `B 20H`, or part of a recorded name.
* **Browse map**: legacy areas with H-number ranges (the legacy letters are cross-reference only; no new numbered sections are used),
  and the **To review** list. **Back** returns to the previous view, **Fit map** shows the whole cemetery.
* Editing and import: signed-in viewers with edit access only. This is enforced by the shared data service
  (`db` rule `read: view, write: admin`), not only by hiding the buttons.

### Record format (collection `lots`, one document per H-number, e.g. `H002589`)

`capacity` (number or null), `capacityVerified`, `notes`, `source`, `updated`, and `records[]` with
`name, birth, death, position, positionVerified, notes, source`.
**Import** (CSV or Excel, first row = headers): `h_number` *or* `section` + `lot`; optional `name, birth, death, position,
position_verified, notes, source`. Unmatched rows are skipped and listed; imported rows are added to existing records.

## Not decided here

The decoder README describes four "H-number sections" (H000001-H002331 grid, margins, M, K/J/I/L). They are decoder passes, not an
approved public grouping, so the site does not use them. Navigation uses neutral area names (legacy letter plus H range) until an approved grouping exists.
