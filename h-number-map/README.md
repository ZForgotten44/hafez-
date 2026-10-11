# Cedar Grove Cemetery — H-Number Map

The Cemetery **Overall Map**, redrawn with every lot's new **H-number** in place of its old lot label.
Built from `Cemetery - Overall Map.pdf` (base drawing) and `Cemetery Map - All Sections on Individual Pages.pdf`
(where the old lot labels can be read), translated with `s4/s4decoder1.py`.

## Start here: the interactive site

**`site/index.html`** — *Cedar Grove Cemetery* — is the primary way to use this; see **[site/README.md](site/README.md)**
for the full writeup. In short: search by old lot label, H-number, or a recorded name; tap any number on the map for
a record card (name, dates, notes — shared across viewers, editable in place, blank until filled in); import a
spreadsheet of records; export a section or a hand-picked list of graves to PDF. ND navy-and-gold, light theme.

It replaces the letter-tile PDF below, whose fixed print crops routinely landed a lot's number under the big maroon
"SECTION X" title or cut a cluster of numbers across a page seam. The site pans/zooms a native SVG viewBox (not a
scaled bitmap), so it stays sharp immediately at any zoom — no blur-then-clear delay.

## Files

| File | Use |
|------|-----|
| `site/index.html` | **The interactive map + full usage docs.** Open directly in a browser. |
| `Cedar_Grove_H-Number_Map_44x34in.pdf` | The map at 4x the original size (ANSI E, 44 x 34 in), for plotting. Vector, so it zooms and plots without blur. |
| `Cedar_Grove_H-Number_Map_letter_tiles.pdf` | *Superseded by the site above* — the same map cut into 25 fixed letter-size pages for a home printer. Kept only for printing a paper copy; several tiles crop a number cluster awkwardly or run it under a section title. Print at **100 % / actual size** and butt the edges together if you use it. |
| `placed_lots.csv` | Every lot that got a number on the map: section, old label, H-number, position on the map. |
| `lots_not_placed_on_map.csv` | Lots the decoder knows about that could not be matched to a label on the old maps (see below). |
| `map_labels_not_in_decoder.csv` | Labels read from the old maps that the decoder has no lot for. |
| `pipeline/` | The scripts used to build both the PDFs and the site (reference; paths are hard-coded to this machine). |

## How to read the map

* Numbers are the H-number **without the leading `H` and zeros**: `1871` = `H001871`. This is what makes them legible at print size
  (a lot is only ~6 map-units wide on the original sheet).
* `A` / `B` after a number = the two rows of a double-row lot (`1690A` = `H001690A`).
* A lot that still shows a small black original label has **no new number yet** (see "Coverage").

## Coverage

3,063 of the decoder's 3,147 lots (97 %) were matched and numbered.

Sanity check on the result: for every section, each lot's H-number was compared with the median of its six nearest
neighbours. Sections I–L stay within 9. In A–H the only large gaps are the margin strips (B, D, F), where the sweep
jumps by design, plus four numbers that
stand out and are worth a quick look on the printed map: **M lot 18** (H002592), **C lots 51H and 9H** (H000972, H000890) and
**F lot 1** (H001889).

### What did not get a number (`lots_not_placed_on_map.csv`)

* **30 rows are not real lots**: the shared base of a double-row lot (D 367–384, E 190–199) and the internal `152dr`/`169dr` keys.
  The maps only draw the `A`/`B` rows, and those were placed.
* **~106 lots** have no matching label on the old maps, or the label could not be read. Two groups stand out and look like
  decoder/map disagreements worth checking rather than reading failures:
  * **Section A** — `20H, 39H, 58H, 77H, 96H, 115H, 134H, 153H, 172H, 191H, 210H, 229H, 248H, 267H, 286H, 305H, 324H, 343H`
    (H-numbers 87, 131, 175 …). Where these should be, the map shows plain `20` and `39` (checked) and, I assume, the rest of the run.
  * **Section B** — labels `373–380H` exist in both the main grid and the margin strip in the decoder (the known B collision); the numbers on the map use the margin-strip lots.
* Labels such as `400`–`414`, `A362`, `B362`, `C344`, `B308`, `C326` are read inside Section B on the old map but are not in the decoder (`map_labels_not_in_decoder.csv`).

## Method (short)

1. The old lot labels are drawn as outlined single-stroke glyphs, not text. I recognised each character by template matching
   (with rotation), rebuilt the labels, and checked each against the decoder for its section.
2. Each source page was registered onto the Overall Map by matching line segments (residual < 0.05 map units), so a label's
   position transfers exactly.
3. The tiny original labels were erased and the H-number was written in the same lot at the same orientation.
