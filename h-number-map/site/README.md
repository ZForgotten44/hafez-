# Cedar Grove Cemetery — site

`index.html` is a single self-contained HTML file (no server, no build step — open it directly, or publish it as a
Claude Artifact) built around one job: **find a place in the cemetery, and see what's on record for it.** Search
and the map work in any browser; holding records, importing a spreadsheet, and exporting a PDF need the hosting
platform's capabilities (see below).

## Layout

A compact app bar (brand, search, connection status, **Print list**, **Manage data**) sits above a 320px sidebar and
a map that fills the rest of the screen. The sidebar scrolls on its own, so a long result never pushes the map
off-screen. Everything administrative — coverage stats, import — lives behind **Manage data**; export lives with
whatever's selected, not in a separate panel.

**Search** — type a legacy label (`B 20H`), an H-number (`H001871`, `1871`, `1690A`), a grave position (`H0016901`),
or a recorded name. Results are typed (**Lot** / **Grave position** / **Person record**) and show the legacy and
modern identifier together. A cataloged lot with no map position still comes back, marked **Map location not
assigned**, so its notes and records are reachable even without a location. Arrow keys move through results, Enter
selects, Escape closes; selecting a result does exactly what clicking that place on the map does.

**The map** — the cemetery's actual Overall Map, panned and zoomed by moving the SVG's own coordinate system (not a
scaled picture of it), so it's sharp at any zoom with no blur-then-clear delay. Zoomed out, individual lot numbers
stay hidden — only the original section labels and roads show (dimmed slightly so they don't dominate), and a whole
section is clickable. Choosing a section eases the view to fit its actual bounds, outlines it, and fades the rest of
the cemetery. Zoom into a section and each lot becomes its own clickable shape with a legible H-number; selecting one
draws a strong outline around its actual footprint and keeps neighbors in view. A breadcrumb
(**Cemetery › Section B › Lot 20H › Grave 3**) tracks where you are and each level is clickable; **Map layers**
(top right) toggles lot/section labels and the handful of drawing labels that match nothing in the catalog. On
touch, a real drag pans the map — it won't also register as a tap on whatever's underneath.

**Section detail** (sidebar, after choosing a section) — the section name, an **Export section** button, a search
scoped to that section, and a scrollable list of every one of its lots with its H-number, click any to select it.

**Lot detail** (sidebar) — status (**Mapped** / **Map location not assigned**), the lot's H-number, an editable
note, and its nine **possible grave positions** as a plain numbered list — deliberately not a spatial diagram, since
the real layout within a lot hasn't been verified. Each position shows a name if one's on record. Actions: back to
results, back to section, copy details, add to the print list, print a location sheet.

**Grave position** (click a position) — opens to a plain read view: a filled-in record shows the name, dates and
notes; an empty one says plainly **"No burial information recorded for this position"** with an **Add record**
button. Editing is a separate step (**Edit record**) with its own **Save**/**Cancel** — cancelling or closing with
unsaved text asks first, and a failed save keeps what you typed rather than clearing the form.

**Manage data** — three tabs: **Mapping coverage** (per-section stats, plus a searchable table of every cataloged
lot and its status), **Import records**, and **Export** (an explainer — the actual export buttons live with the
section or print list they act on). The two "something's off" categories are kept distinct: a *cataloged lot
without map coordinates* (in the records, no position yet) is not the same problem as a *label on the original
drawing with no catalog match*, and the panel never merges them.

## Where the H-numbers come from

The section/lot ↔ H-number mapping is **computed**, not looked up: it comes from `s4/s4decoder1.py`'s documented
sweep of the cemetery (`H_lot`) and its grave formula `H_grave = H_lot × 10 + grave_position (1–9)`. Coverage is
currently 3,033 of 3,147 cataloged lots mapped (96%) — see Manage data for the rest. **There is no burial register
behind any of this.** A lot's nine grave positions are the nine the formula allows, not nine known graves, and a
blank position is never presented as "vacant." The record feature exists to attach real information once someone
has it, and starts empty everywhere.

## Records: import, edit, export

**Editing in place.** Every grave position's Name/Birth/Death/Notes and every lot's Note live in a database shared
by this page's viewers, not in your browser — someone else opening the link sees what you saved. Dates are free
text on purpose (`1912`, `Mar 1912`, `c. 1900` are all fine) — nothing is validated, parsed, or completed for you.

**Import** (Manage data → Import records). Upload a `.csv` or `.xlsx`:

| Column | Meaning |
|---|---|
| `section` | Section letter (paired with `lot`) |
| `lot` | The legacy lot label, e.g. `20H` |
| `h_number` | Alternative to `section`+`lot` — e.g. `H001871` |
| `grave` | 1–9. Blank = the row is a **lot-level** note, not a person record |
| `name`, `birth`, `death`, `notes` | Record fields |

Nothing is written on upload. The file is parsed and every row is matched, then shown in a **preview** — matched,
no-match, or conflicting/invalid, with a reason — before anything touches the shared store; you confirm before it
commits. A row with a name or date but no grave position is flagged rather than silently folded into a lot note. A
blank cell never erases a value that's already there. If a row gives both `section`+`lot` and `h_number` and they
disagree, it's held out as a conflict, not guessed at. After import, a **downloadable error report (.csv)** lists
exactly what didn't go in and why. Matching is exact — no fuzzy matching, ever.

**Export**, always a real file-save through the platform's own dialog (never a browser print-to-PDF):
- **Export section** (once a section is selected) opens one menu with three outputs: **Save section map · PDF** — a
  vector-drawn, to-scale map of just that section with readable H-numbers (and legacy labels alongside, if you want
  them), paper size and orientation selectable, previewed before you download; **Export section data · PDF** — two
  tables, every cataloged lot (mapped or not, your choice) and every grave position with a name on record;
  **Export section data · Excel** — a real `.xlsx` with separate **Lots** and **Grave positions** sheets, frozen
  header row, autofilter, and H-numbers kept as text so nothing reformats them.
- **Print location sheet** (on a lot's own detail) — that one lot, its identifiers, and nearby lots for orientation.
- **Record list** — whatever's on the **print list** (any mix of lots and specific grave positions across the whole
  cemetery), with recorded details. Review and dedupe from the print list button before exporting.

## Requires a Claude Artifact host

Read-only search and browsing work anywhere. Saving a record, importing, and exporting a PDF call three Claude
Artifact **runtime capabilities**:

| Capability | Used for |
|---|---|
| `db` | The shared record store — collection `lots`, one document per lot (its note plus a `graves` map keyed 1–9) |
| `downloads` | The save dialog for PDFs, the `.xlsx` export, and the import error report |
| `user` | Checking whether the current viewer may write shared records |

The page states its own connection status up front — near the map, not discovered by filling out a form — as one of
**Shared records connected**, **Read-only access**, or **Shared records unavailable in this view**; Save/Add-record
controls are disabled to match rather than failing after the fact.

## Known gaps

- ~114 lots (of 3,147 cataloged) have no position on the map yet — see Manage data for the list and, where known, why.
- Section boundaries — both on the overview and drawn on the section-map PDF — are the bounding box around that
  section's lots, not its true irregular outline. Close, not exact. Lot click targets are likewise an estimated
  rectangle around each label, not the drawing's own lot lines (the source artwork isn't broken into per-lot shapes
  to click precisely).
- The section-map PDF's north arrow and its "nearby roads/landmarks" are not drawn — the source artwork's roads
  aren't separable from its other line work (see the next point), so the map shows lots only. North is assumed to
  match the source drawing's own orientation but wasn't independently verified.
- Every section fits on one printed page; very dense sections (D, C) print small H-numbers rather than splitting
  across multiple detail pages with an index.
- The PDF preview is a best-effort embed — if a given browser or host won't render an embedded PDF, the file is
  already built and **Download PDF** still works from the same dialog.
- The zoomed-out view relies on the original drawing's own printed labels for section names and roads; the small
  original lot numbers that are part of that same artwork can't be separated out and hidden without re-doing the
  character-extraction pipeline against the overall map specifically (a project on the scale of the one already done
  for the individual section pages).
- No conflict check yet if two people edit the same record at once — last save wins. A record shows when it was last
  updated, but doesn't warn if someone else changed it in between.
- The database caps an artifact at 5,000 documents; one document per *lot* (not per grave) keeps the cemetery's
  ~3,150 lots well under that even at full coverage.
