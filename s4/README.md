# Cedar Grove Cemetery — H-Number Decoder

A single-file Python tool that translates between **legacy plot labels**
(section + lot, e.g. `B-20H`, `D-384A`, `M-122`) and the cemetery's
sequential **H-numbering scheme** (`H000001` … `H003185`), in both directions,
for all of Cedar Grove Cemetery at the University of Notre Dame.

Everything lives in one script — **`s4decoder1.py`** (the latest version) —
with no third-party dependencies. It runs as an interactive command-line
tool, a one-shot lookup, a test runner, or a CSV exporter.

> Verified against `s4/s4decoder1.py`: all H-range boundaries, section
> totals, and lookups below were checked by running the code.
> Sections **K, J, I, L are fully implemented** (Section 4), even though a few
> banner/help strings in the script still say the system ends at M
> (see [Known issues](#13-known-issues)).

---

## Table of Contents

1. [What problem this solves](#1-what-problem-this-solves)
2. [Quick start](#2-quick-start)
3. [Core concepts & vocabulary](#3-core-concepts--vocabulary)
4. [The H-number system, section by section](#4-the-h-number-system-section-by-section)
5. [The four "H-number sections"](#5-the-four-h-number-sections)
6. [Special lot types](#6-special-lot-types)
7. [Public functions (API)](#7-public-functions-api)
8. [Interactive commands](#8-interactive-commands)
9. [Command-line flags](#9-command-line-flags)
10. [CSV export format](#10-csv-export-format)
11. [The test suite](#11-the-test-suite)
12. [How the code is organized](#12-how-the-code-is-organized)
13. [Known issues](#13-known-issues)
14. [Extending the decoder](#14-extending-the-decoder)
15. [Glossary of internal names](#15-glossary-of-internal-names)

---

## 1. What problem this solves

Cedar Grove Cemetery historically identifies each grave plot by a
**section letter + lot number** (e.g. lot `20H` in Section B). These labels
are irregular: lot numbers restart in every section, some lots carry `H`
suffixes, some sit in "double rows" that share a footprint, and some lots
appear in curved margin strips that don't follow the main grid.

The cemetery's modern records use a single flat **H-number** — a
zero-padded sequential ID from `H000001` upward — that walks the whole
cemetery in one continuous **sweep**. This tool is the bridge:

- **Forward:** `Section B, lot 20H` → `H000001`
- **Reverse:** `H000001` → `Section B, lot 20H`
- **Graves:** each lot holds up to 9 graves; a grave gets
  `H_lot × 10 + grave_number` → `H0000011`, `H0000012`, …

The system spans **H000001 – H003185** across **13 sections**
(A, B, C, D, E, F, G, H, I, J, K, L, M) and **3,147 lots**.

---

## 2. Quick start

```bash
cd s4

# Interactive mode (recommended first run)
python3 s4decoder1.py

# One-shot lookup
python3 s4decoder1.py B 20H        # -> H000001
python3 s4decoder1.py A 100 3      # lot 100, grave 3

# Run the validation suite
python3 s4decoder1.py --test

# Export every section to CSV
python3 s4decoder1.py --export ./out
```

Requires **Python 3.6+**. No `pip install` — the only import is `csv`/`os`
from the standard library.

Inside interactive mode:

```
> lookup M 122
> reverse H003185
> test K
> stats
> help
> quit
```

---

## 3. Core concepts & vocabulary

| Term | Meaning |
|------|---------|
| **Section** | A named region of the cemetery: A–M. |
| **Lot** | A plot within a section, identified by a label like `20H`, `384A`, `1U`, `263C`. |
| **Grave** | A single burial position within a lot (1–9). |
| **H-number** | The flat sequential ID: `H` + 6 digits, e.g. `H001871`. |
| **Sweep** | The fixed path that visits every lot in order, assigning H-numbers. |
| **Pass** | A stage of the Section-1 sweep that interleaves two sections column-by-column. |
| **H-lot** | A lot whose label ends in `H` (e.g. `20H`). A real, distinct lot — the `H` is part of the historical label. |
| **Double-row** | Two lots stacked in one grid cell that **share one H-number**, distinguished only by an `A`/`B` suffix. |
| **Margin** | A curved edge strip of lots outside a section's main rectangular grid. |

### The grave formula (universal)

```
H_grave = H_lot × 10 + grave_number        (grave_number ∈ 1..9)
```

For double-row lots the `A`/`B` suffix is preserved between the lot number and
the grave digit:

```
h_grave('D', '376A', 3)  ->  H001698A3
h_grave('E', '199B', 2)  ->  H002260B2
```

Sweep direction inside the grid: **columns run bottom → top** (`r = 1` is the
bottom row); **graves within a lot run top → bottom** (grave 1 = top).

---

## 4. The H-number system, section by section

```
H000001 ┬─ SECTION 1 · THE GRID ──────────────────── H002331
        │    Pass 1:  B + A     H000001 – H000836
        │    Pass 2:  D + C     H000837 – H001871
        │    Pass 3:  F + E     H001872 – H002331
        │
H002332 ┼─ SECTION 2 · THE MARGINS ────────────────── H002586
        │    B margins          H002332 – H002372
        │    D margins          H002373 – H002401
        │    F margins          H002402 – H002413
        │    G + H (alternating rows)   H002414 – H002586
        │
H002587 ┼─ SECTION 3 · SECTION M ───────────────────── H002835
        │
H002836 ┼─ SECTION 4 · K J I L ─────────────────────── H003185
        │    K                  H002836 – H002950
        │    J                  H002951 – H003082
        │    I                  H003083 – H003146
        │    L                  H003147 – H003185
        │
H003185 ┴─ SYSTEM MAXIMUM
```

### Exact figures per lettered section (from `full_table()`)

| Section | Part | Lots | H-range (min–max) | Notes |
|---------|------|-----:|-------------------|-------|
| **A** | grid | 418 | H000023 – H000836 | Interleaved with B |
| **B** | grid + margin | 423 rows | H000001 – H002372 | See label collision, §13 |
| **C** | grid | 519 | H000880 – H001871 | Interleaved with D; A/B/C suffix lots |
| **D** | grid + margin | 544 | H000837 – H002401 | Grid ends H001827; double-rows; margin 542–563H |
| **E** | grid | 262 | H001890 – H002331 | Interleaved with F; double-rows |
| **F** | grid + margin | 210 | H001872 – H002413 | Grid ends H002287; margin lots 199–210 |
| **G** | S2 | 80 | H002414 – H002563 | 4 rows, alternates with H |
| **H** | S2 | 92 | H002436 – H002586 | 4 rows, alternates with G |
| **M** | S3 | 249 | H002587 – H002835 | 54 rows, lots 11–279 |
| **K** | S4 | 115 | H002836 – H002950 | 44 rows |
| **J** | S4 | 132 | H002951 – H003082 | 28 rows |
| **I** | S4 | 64 | H003083 – H003146 | 32 rows, 2 lots each |
| **L** | S4 | 39 | H003147 – H003185 | 7 rows |

Interleaved ranges overlap because two sections are woven together
column-by-column in that pass; the range shown is each section's own min/max,
not a contiguous block. Totals add to **3,147**.

---

## 5. The four "H-number sections"

Each H-number section picks up exactly where the previous one ended. (This is
a bookkeeping concept — not the same as the cemetery's *lettered* sections.)

### Section 1 · The Grid (H000001 – H002331)

Three passes, each interleaving two adjacent sections **column by column**:

```
PASS 1 — B + A      column-1-B, column-1-A, column-2-B, column-2-A, …
PASS 2 — D + C
PASS 3 — F + E
```

- **Pass 1 (B + A)** is *formula*-driven: `SWEEP = 44`, `ROWS = 19`,
  `OFFSET = 836`. `H(B,lot) = 44×(r−1) + c`; `H(A,lot) = 44×(r−1) + 22 + c`.
- **Pass 2 (D + C)** and **Pass 3 (F + E)** are *table-driven*: rows have
  irregular widths, so the sweep order is stored row-by-row in `_D_ROWS`,
  `_C_ROWS`, `_F_ROWS`, `_E_ROWS`. Pass 3 constants: `N_F = 18`, `N_E = 22`,
  `SWEEP_EF = 40`, `ROWS_EF = 12` (F has only 11 rows).

```
OFFSET     = 836     # last H of Pass 1  (H000836 = A·343)
_DC_MAX_H  = 1871    # last H of Pass 2  (H001871 = C·417)
_EF_MAX_H  = 2331    # last H of Pass 3  (H002331 = E·214)
```

### Section 2 · The Margins (H002332 – H002586)

1. **B margins** — 27 rows, lots 373–394 with lettered sub-lots
   (`384HA`, `385A`, `387B`, `390C`, …). Each sub-lot gets its **own** H-number
   — these are *not* double-rows.
2. **D margins** — 29 rows, lots 542–563H, one lot per row.
3. **F margins** — 12 rows, lots 199–210.
4. **G and H, alternating by row** — G row 1, H row 1, G row 2, H row 2, …
   Each has 4 rows. G lists 81 positions but 80 distinct lots (duplicate `19`).

```
_S2_MAX_H = 2586    # H002586 = H·70
```

### Section 3 · Section M (H002587 – H002835)

54 rows, 249 lots (11–279), no double-rows, no suffixes. Some lot numbers are
skipped (the map has gaps) but H-numbers stay sequential.

```
_S3_MAX_H = 2835    # H002835 = M·279
```

### Section 4 · K J I L (H002836 – H003185)

Swept one after another: **all of K, then J, then I, then L.**

- **K** — 44 rows, 115 lots
- **J** — 28 rows, 132 lots
- **I** — 32 rows, 64 lots (exactly 2 per row: `2r−1`, `2r`)
- **L** — 7 rows, 39 lots

```
_S4_MAX_H = 3185    # last H in the system  (H003185 = L·107)
```

---

## 6. Special lot types

### H-lots
`20H`, `355H`, `380H` … The trailing `H` is part of the historical label. They
have their own sweep position and H-number. Not to be confused with a
double-row or a grave.

### Double-row lots — shared H-number + `A`/`B` suffix

In **Section D rows 20–21** and **Section E rows 9–10**, two physical rows are
stacked in one grid footprint and share one H-number.

```
lookup D 384      ->  H001690      (shared base)
lookup D 384A     ->  H001690A     (inner / A-row)
lookup D 384B     ->  H001690B     (outer / B-row)
lookup E 199A     ->  H002260A
lookup E 199B     ->  H002260B
```

- **D** (`_D_DR_PAIRS`): lots 367–384 (18 pairs).
- **E** (`_E_DR_PAIRS` / `_E_DR_SUFFIX_MAP`): lots 190–199 plus 152 and 169
  (12 pairs). 152 and 169 are stored under internal keys `152dr` / `169dr` so
  they don't clash with the *single* lots 152 and 169 elsewhere in E.

> **Contrast with the B margins:** `390A`, `390B`, `390C`, … each get their own
> H-number. Only D rows 20/21 and E rows 9/10 use the shared-H rule.

### Suffix lots in Section C — `A`/`B`/`C`
Section C rows 14–24 contain `263C`, `263B`, `263A`, `263` in sequence — four
**distinct** lots with separate H-numbers, read right-to-left in the sweep.

---

## 7. Public functions (API)

```python
import importlib.util
spec = importlib.util.spec_from_file_location("d", "s4/s4decoder1.py")
d = importlib.util.module_from_spec(spec); spec.loader.exec_module(d)
```

### `h_lot(section, lot_label) -> (h_number, formatted)`

```python
d.h_lot('B', '20H')    # (1, 'H000001')
d.h_lot('D', '384A')   # (1690, 'H001690A')
d.h_lot('M', '122')    # (2678, 'H002678')
d.h_lot('L', '107')    # (3185, 'H003185')
d.h_lot('Z', '1')      # (None, "Unknown section …")
```

Returns `(None, error_message)` on failure. Section letter is
case-insensitive; the letter part of a lot label is case-sensitive.

### `h_grave(section, lot_label, grave_number) -> (h_number, formatted)`

`grave_number` must be 1–9.

```python
d.h_grave('B', '20H', 1)    # (11, 'H0000011')
d.h_grave('D', '376A', 3)   # (16983, 'H001698A3')
```

### `decode_h(h_number) -> dict | None`

```python
d.decode_h(1)      # {'section':'B','lot_label':'20H','c':1,'r':1,…}
d.decode_h(3185)   # {'section':'L','lot_label':'107',…}
d.decode_h(3186)   # None (above system max)
```

Always returns `section`, `lot_label`, `h_number`, `h_formatted`; the
formula-based grids (B/A/F/E) also include `c` and `r`.

### `full_table(section)` / `export_csv(section, path)` / `export_all_csv(out_dir=".")`

`full_table` lists every lot in a section sorted by H-number, with the first
six grave H-numbers. The export functions write it to CSV.

---

## 8. Interactive commands

| Command | What it does |
|---------|--------------|
| `lookup <sec> <lot>` | Forward lookup, framed result panel. |
| `lookup <sec> <lot> <g>` | Same, plus the grave H-number. |
| `reverse <H>` | Reverse lookup. Accepts `H003185`, `003185`, or `3185`. |
| `test` | Global validation suite (47 checks). |
| `test <sec>` | Per-section anchor tests (e.g. `test K`, `test M`). |
| `table <sec>` | Print every lot in a section. |
| `export [dir]` | Write all 13 section CSVs. |
| `stats` | Coverage breakdown across all four H-number sections. |
| `info` | Constants and range reference. |
| `help` | Command reference. |
| `quit` / `exit` / `q` | Leave. |

---

## 9. Command-line flags

| Invocation | Effect |
|------------|--------|
| `python3 s4decoder1.py` | Interactive mode. |
| `python3 s4decoder1.py --test` | Run the global suite and exit. |
| `python3 s4decoder1.py --export [dir]` | Export all CSVs and exit. |
| `python3 s4decoder1.py <sec> <lot> [grave]` | One-shot lookup and exit. |

---

## 10. CSV export format

One file per section: `cedar_grove_section_<X>_h_table.csv` (A–M). A
pre-generated set is in `s4/J/`.

| Column | Meaning |
|--------|---------|
| `section` | Section letter. |
| `lot_label` | Legacy lot label. |
| `col_c`, `row_r` | Grid coordinates (formula-based sections only). |
| `h_lot_number` | Integer H-number. |
| `h_lot` | Formatted H-number. |
| `h_grave_1` … `h_grave_6` | Grave H-numbers for graves 1–6. |

Rows are sorted by `h_lot_number`.

---

## 11. The test suite

`s4decoder1.py` has two levels of testing:

1. **`--test` / `test`** — 47 hand-verified checks (last run: **47/47, 100%**)
   grouped into panels: double-row D and E lookups, grave H-numbers, and
   anchor lookups across sections.
2. **`test <sec>`** — 7–9 anchor checks per section (B, A, K, M, …), defined
   in `_do_test_section()`.

Last run: `test K` 7/7, `test M` 9/9, **`test B` 6/7** (the one failure is the
`380H` label collision described below).

> The exhaustive property-based suite (round-trip for every lot, continuity
> for every H from 1…3185, ~5,600 checks) is **not present in this version**.
> If wanted, it would be the natural next addition.

---

## 12. How the code is organized

```
1.  Docstring + constants              N_B…, SWEEP, ROWS, OFFSET, N_F/N_E, SWEEP_EF, ROWS_EF
2.  Pass-1 formula decoders            build_B_decoder / build_A_decoder
3.  Pass-2 tables + builder            _D_ROWS, _C_ROWS -> _build_dc_tables()
4.  Pass-3 tables + builder            _F_ROWS, _E_ROWS -> _build_ef_tables()
5.  Section-2 tables + builder         _B/_D/_F_MARGIN_ROWS, _G_ROWS, _H_ROWS -> _build_s2_tables()
6.  Section-3 table + builder          _M_ROWS -> _build_m_tables()
7.  Section-4 tables + builder         _K/_J/_I/_L_ROWS -> _build_s4_tables()
8.  F/E formula decoders               build_F_decoder / build_E_decoder
9.  h_lot()  h_grave()  decode_h()
10. full_table() / export_csv() / export_all_csv()
11. self_test()                        the 47-check global suite
12. Display helpers                     _box, _show, _section_block, _stats, _help, _info
13. _do_test_section()                  per-section anchor tests
14. interactive() + __main__ dispatch
```

**Design principle:** each H-number section walks an ordered list of rows and
hands out consecutive integers, starting from the previous section's maximum —
which is why the whole system is one gap-free sweep.

---

## 13. Known issues

### Section B label collision (open data question)

Labels `373, 374, 375, 376, 377, 378, 379, 380H` exist in **both** the B main
grid (row 19, bottom-left) **and** the B margin strip. The margin lookup wins:

```
h_lot('B','380H')  -> H002341   (margin)
decode_h(793)      -> B · 380H  (grid; forward lookup can't reach this)
```

So the round trip `H000793 → 380H → H002341` is broken, and `test B` fails
its `380H` anchor (expects `H000793`). Resolution needs a decision:
(a) the margins are authoritative and the grid shouldn't extend to those lots,
or (b) both are real and need distinguishing labels.

### Duplicate `19` in Section G
Row 1 lists `19` twice; the builder keeps the first, giving 80 distinct lots
from 81 positions.

### Stale strings in `s4decoder1.py` (cosmetic, not logic)
The K/J/I/L data and lookups work, but these were not updated:

- **Module docstring** (lines 1–30) still describes only "Sections A, B, C, D"
  and "two passes".
- **Interactive banner** says `H000001 – H002835 · Sections: A B C D E F G H M`.
- **`reverse` out-of-range message** reports `System max: H002835`
  (uses `_S3_MAX_H`; should be `_S4_MAX_H` = `H003185`).
- **`table` usage text** lists `A B C D E F G H M` (omits I J K L).
- `_box()` is defined twice (lines ~1100 and ~1466); the later one wins.

---

## 14. Extending the decoder

To add a new section:

1. Add its rows as an ordered dict `_X_ROWS = {1: [...], 2: [...], …}` in sweep
   order.
2. Add a `_build_*_tables()` that starts from `_S4_MAX_H` and assigns
   consecutive H-numbers.
3. Register the lookup in `h_lot()` and the reverse-map range check in
   `decode_h()`.
4. Add it to `full_table()`, the export loop, and `_do_test_section()`.
5. Update `_stats()`, `_info()`, the interactive banner, and the
   out-of-range message.

If the section has double-rows, follow the D/E pattern: one base lot per shared
position, with a suffix-resolution branch in `h_lot()`.

---

## 15. Glossary of internal names

| Name | Meaning |
|------|---------|
| `OFFSET` | 836 — last H of Pass 1 / start offset for Pass 2. |
| `_DC_MAX_H` | 1871 — last H of Pass 2 (D+C). |
| `_EF_MAX_H` | 2331 — last H of Pass 3 and of Section 1. |
| `_S2_MAX_H` | 2586 — last H of Section 2. |
| `_S3_MAX_H` | 2835 — last H of Section 3 (M). |
| `_S4_MAX_H` | 3185 — last H of Section 4 and of the whole system. |
| `B_DECODER`, `A_DECODER`, `F_DECODER`, `E_DECODER` | Formula-based `lot -> (col, row)` maps. |
| `_D_ROWS`, `_C_ROWS`, `_F_ROWS`, `_E_ROWS` | Row data for the table-driven grids. |
| `_D_LOT_H`, `_C_LOT_H`, `_F_LOT_H`, `_E_LOT_H` | `lot -> H` maps built from those rows. |
| `_B_MARGIN_ROWS`, `_D_MARGIN_ROWS`, `_F_MARGIN_ROWS`, `_G_ROWS`, `_H_ROWS` | Section-2 row data. |
| `_M_ROWS` / `_M_LOT_H` | Section-3 row data / lookup. |
| `_K_ROWS`…`_L_ROWS` / `_K_LOT_H`…`_L_LOT_H` | Section-4 row data / lookups. |
| `_D_DR_PAIRS` | Section-D double-row bases (367–384). |
| `_E_DR_PAIRS`, `_E_DR_SUFFIX_MAP` | Section-E double-row bases and suffix map (`199A`, `152B`, …). |
| `_DC_H_LOT`, `_EF_H_LOT`, `_S2_H_LOT`, `_M_H_LOT`, `_S4_H_LOT` | Reverse maps `H -> (section, lot)`. |

---

*Cedar Grove Cemetery · University of Notre Dame · Notre Dame, Indiana*
