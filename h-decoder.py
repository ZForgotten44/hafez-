"""
Cedar Grove Cemetery — H-Number Decoder
========================================
Sections A, B, C, D combined sweep.

TWO PASSES — each pass interleaves two sections column by column:

  PASS 1 — B + A   H000001 … H000836
    col 1-B → col 1-A → col 2-B → col 2-A → … → col 22-B → col 22-A
    (D is behind B;  C is behind A in the cemetery)

  PASS 2 — D + C   H000837 … H001672
    col 1-D → col 1-C → col 2-D → col 2-C → … → col 22-D → col 22-C

Within each column:  lots BOTTOM → TOP   (r=1 = bottom row)
Within each lot:     graves TOP → BOTTOM (grave 1 = top of lot)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FORMULA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PASS 1 (B / A):
  H(B, lot) =          SWEEP × (r−1)  +  c
  H(A, lot) =          SWEEP × (r−1)  +  N_B  +  c

PASS 2 (D / C):
  H(D, lot) = OFFSET + SWEEP × (r−1)  +  c
  H(C, lot) = OFFSET + SWEEP × (r−1)  +  N_D  +  c

GRAVE:
  H_grave   = H_lot × 10 + grave_number

CONSTANTS:
  N_B = N_A = N_D = N_C = 22          (columns per section)
  SWEEP  = N_B + N_A = N_D + N_C = 44
  ROWS   = 19                          (rows per section, bottom→top)
  OFFSET = SWEEP × ROWS = 836         (H-number offset for D/C pass)

KEY ANCHORS:
  B-20H  = H000001   (first lot: rightmost column of B, bottom row)
  A-1    = H000044   (last lot of pass 1)
  D-1U   = H000837   (first lot of pass 2)
  C-417  = H001672   (last lot of pass 2)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COLUMN DECODER STRUCTURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
c = 1  →  rightmost column (Notre Dame Ave / east side)
c = 22 →  leftmost column  (west side)
r = 1  →  bottom row
r = 19 →  top row

Section B (22 cols, 19 rows, row-increment = 20):
  c=1       : H-lots   20H, 40H, …, 380H
  c=2       : 19A (r=1);  39, 59, … (r≥2)
  c=3…21    : lot = (r−1)×20 + (22−c)
  c=22      : leftmost strip  12, 31, 50, … = 12+19×(r−1)

Section A (22 cols, 19 rows, row-increment = 19):
  Right sub-block (c=1…11): 19,18,…14 + base;  c=7 → (13+base)H
  Left sub-block (c=12…22): 9,8,…2 + base; c=16 → (5+base)H; c=21 → (1+base)H; c=22 → 1+base
  base = 19×(r−1)

Section D (22 cols, 19 rows, row-increment = 20  — mirrors B):
  r=1 (bottom): lettered sub-lots of lot 1
    c=1→"1U"  c=2→"1T" … c=15→"1G"  c=16→"F1"  c=17→"1E" … c=21→"1A"  c=22→"1"
  c=1  r≥2  : H-lots  40H, 60H, …, 380H  (= 20×r H)
  c=2  r=2  : "29H";  c=2 r≥3 → 19+20×(r−1)
  c=3…21 r≥2: lot = (r−1)×20 + (22−c)
  c=22 r≥2  : lot = 20×(r−1) + 1   i.e. 21, 41, 61, …

Section C (22 cols, 19 rows, row-increment = 23):
  General: lot = 2 + (r−1)×23 + (23−c)
  c=22 r=1  → lot  3  (leftmost bottom)
  c=1  r=1  → lot 24  (rightmost bottom)
  c=22 r=19 → lot 417 (leftmost top — last regular lot)  ✓
  c=1  r=19 → lot 438 (rightmost top — beyond range, labeled 438H)
  Lots 1 and 2 ("1C","2C") are special entries outside the main grid formula.
"""

import csv
import os

# ─────────────────────────────────────────────────────────────────────
N_B = N_A = N_D = N_C = 22
SWEEP  = N_B + N_A          # 44
ROWS   = 19
OFFSET = SWEEP * ROWS       # 836


# ─────────────────────────────────────────────────────────────────────
# SECTION B  (22 cols × 19 rows, row-increment 20)
# ─────────────────────────────────────────────────────────────────────
def build_B_decoder():
    d = {}
    for r in range(1, ROWS+1):
        d[f"{20*r}H"] = (1, r)
    d["19A"] = (2, 1)
    for r in range(2, ROWS+1):
        d[str(19 + 20*(r-1))] = (2, r)
    for r in range(1, ROWS+1):
        for c in range(3, 22):
            d[str((r-1)*20 + (22-c))] = (c, r)
    for r in range(1, ROWS+1):
        d[str(12 + 19*(r-1))] = (22, r)
    return d


# ─────────────────────────────────────────────────────────────────────
# SECTION A  (22 cols × 19 rows, row-increment 19)
# ─────────────────────────────────────────────────────────────────────
def build_A_decoder():
    d = {}
    for r in range(1, ROWS+1):
        b = 19*(r-1)
        d[str(19+b)]=(1,r);  d[str(18+b)]=(2,r);  d[str(17+b)]=(3,r)
        d[str(16+b)]=(4,r);  d[str(15+b)]=(5,r);  d[str(14+b)]=(6,r)
        d[f"{13+b}H"]=(7,r); d[str(13+b)]=(8,r);  d[str(12+b)]=(9,r)
        d[str(11+b)]=(10,r); d[str(10+b)]=(11,r)
        d[str(9+b)] =(12,r); d[str(8+b)] =(13,r); d[str(7+b)] =(14,r)
        d[str(6+b)] =(15,r); d[f"{5+b}H"]=(16,r); d[str(5+b)] =(17,r)
        d[str(4+b)] =(18,r); d[str(3+b)] =(19,r); d[str(2+b)] =(20,r)
        d[f"{1+b}H"]=(21,r); d[str(1+b)] =(22,r)
    return d


# ─────────────────────────────────────────────────────────────────────
# SECTION D  (22 cols × 19 rows, row-increment 20 — mirrors B)
# ─────────────────────────────────────────────────────────────────────
# Row 1: unique lettered sub-lots  1U, 1T, … 1A, 1
# Row 2: 29H is the special c=2 position (like 19A in B)
# Rows 2-19: same arithmetic as B
_D_ROW1 = {
    1:"1U", 2:"1T", 3:"1S", 4:"1R", 5:"1Q", 6:"1P",
    7:"1O", 8:"1N", 9:"1M", 10:"1L", 11:"1K", 12:"1J",
    13:"1I", 14:"1H", 15:"1G", 16:"F1", 17:"1E", 18:"1D",
    19:"1C", 20:"1B", 21:"1A", 22:"1"
}
def build_D_decoder():
    d = {}
    for c, label in _D_ROW1.items():
        d[label] = (c, 1)
    for r in range(2, ROWS+1):
        d[f"{20*r}H"] = (1, r)
        if r == 2:
            d["29H"] = (2, 2)
        else:
            d[str(19 + 20*(r-1))] = (2, r)
        for c in range(3, 22):
            d[str((r-1)*20 + (22-c))] = (c, r)
        d[str(20*(r-1) + 1)] = (22, r)
    return d


# ─────────────────────────────────────────────────────────────────────
# SECTION C  (22 cols × 19 rows, row-increment 23)
# ─────────────────────────────────────────────────────────────────────
# General formula:  lot = 2 + (r−1)×23 + (23−c)
# c=22, r=19 → lot 417  (last regular lot, leftmost top)
# c=1,  r=19 → lot 438  (rightmost top — labeled 438H)
# Lots 1C and 2C are special entries outside the main formula grid.
def build_C_decoder():
    d = {}
    # Special entries for lots 1 and 2 (outside main formula)
    d["1C"] = (22, 0)   # virtual position (before row 1)
    d["2C"] = (21, 0)   # virtual position
    for r in range(1, ROWS+1):
        for c in range(1, N_C+1):
            lot_num = 2 + (r-1)*23 + (23-c)
            if c == 1 and r == ROWS:   # lot 438 → H-lot
                d["438H"] = (c, r)
            else:
                d[str(lot_num)] = (c, r)
    return d


# Build all four decoders once at import time
B_DECODER = build_B_decoder()
A_DECODER = build_A_decoder()
D_DECODER = build_D_decoder()
C_DECODER = build_C_decoder()

_DECODERS = {'A': A_DECODER, 'B': B_DECODER, 'C': C_DECODER, 'D': D_DECODER}


# ─────────────────────────────────────────────────────────────────────
# HASH FUNCTIONS
# ─────────────────────────────────────────────────────────────────────

def h_lot(section, lot_label):
    """
    Return (h_number, 'H000001') for a section + legacy lot label.

    section   : 'A', 'B', 'C', or 'D'  (case-insensitive)
    lot_label : string, e.g. '20H', '1U', '100', '1C', '417'

    Examples
    --------
    h_lot('B', '20H')  ->  (1,    'H000001')
    h_lot('A', '1')    ->  (44,   'H000044')
    h_lot('D', '1U')   ->  (837,  'H000837')
    h_lot('C', '417')  ->  (1672, 'H001672')
    """
    sec = section.upper().strip()
    lot = str(lot_label).strip()

    dec = _DECODERS.get(sec)
    if dec is None:
        return None, f"Unknown section '{section}'. Use A, B, C, or D."
    if lot not in dec:
        return None, f"Lot '{lot}' not found in Section {sec}."

    c, r = dec[lot]

    if sec == 'B':
        h = SWEEP * (r-1) + c
    elif sec == 'A':
        h = SWEEP * (r-1) + N_B + c
    elif sec == 'D':
        h = OFFSET + SWEEP * (r-1) + c
    elif sec == 'C':
        if r == 0:   # virtual lots 1C / 2C — assign H numbers just before H837
            virtual = {'1C': OFFSET - 1, '2C': OFFSET - 2}
            h = virtual.get(lot, OFFSET - 1)
        else:
            h = OFFSET + SWEEP * (r-1) + N_D + c

    return h, f"H{h:06d}"


def h_grave(section, lot_label, grave_number):
    """
    Return (h_grave_number, 'H0000011') for a section + lot + grave.
    H_grave = H_lot × 10 + grave_number  (grave_number 1-9)
    """
    h, msg = h_lot(section, lot_label)
    if h is None:
        return None, msg
    g = int(grave_number)
    if not (1 <= g <= 9):
        return None, f"Grave number must be 1-9, got {g}."
    hg = h * 10 + g
    return hg, f"H{hg:07d}"


def decode_h(h_number):
    """
    Reverse lookup: H lot number → section + legacy lot label.
    Returns a dict or None if out of range.
    """
    max_h = OFFSET * 2   # 1672
    if h_number < 1 or h_number > max_h:
        return None

    if h_number <= OFFSET:                  # B / A pass
        level = (h_number - 1) // SWEEP
        pos   = (h_number - 1) % SWEEP + 1
        r = level + 1
        if pos <= N_B:
            c, sec, dec = pos, 'B', B_DECODER
        else:
            c, sec, dec = pos - N_B, 'A', A_DECODER
    else:                                   # D / C pass
        adj   = h_number - OFFSET
        level = (adj - 1) // SWEEP
        pos   = (adj - 1) % SWEEP + 1
        r = level + 1
        if pos <= N_D:
            c, sec, dec = pos, 'D', D_DECODER
        else:
            c, sec, dec = pos - N_D, 'C', C_DECODER

    tgt  = (c, r)
    lot  = next((k for k, v in dec.items() if v == tgt), None)
    return {"section": sec, "lot_label": lot, "c": c, "r": r,
            "h_number": h_number, "h_formatted": f"H{h_number:06d}"}


# ─────────────────────────────────────────────────────────────────────
# TABLE EXPORT
# ─────────────────────────────────────────────────────────────────────

def full_table(section):
    """Return list of dicts (sorted by H number) for a section."""
    sec = section.upper()
    dec = _DECODERS[sec]
    rows = []
    for lot_label, (c, r) in dec.items():
        if r == 0:      # skip virtual entries
            continue
        h, hfmt = h_lot(sec, lot_label)
        row = {"section": sec, "lot_label": lot_label,
               "col_c": c, "row_r": r,
               "h_lot_number": h, "h_lot": hfmt}
        for g in range(1, 7):
            hg, hgfmt = h_grave(sec, lot_label, g)
            row[f"h_grave_{g}"] = hgfmt
        rows.append(row)
    rows.sort(key=lambda x: x["h_lot_number"])
    return rows


def export_csv(section, filepath):
    rows = full_table(section)
    if not rows:
        return 0
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return len(rows)


def export_all_csv(out_dir="."):
    os.makedirs(out_dir, exist_ok=True)
    for sec in ("B", "A", "D", "C"):
        path = os.path.join(out_dir, f"cedar_grove_section_{sec}_h_table.csv")
        n = export_csv(sec, path)
        print(f"  Section {sec}: {n:4d} lots  →  {path}")


# ─────────────────────────────────────────────────────────────────────
# SELF-TEST
# ─────────────────────────────────────────────────────────────────────

def self_test():
    sep = "=" * 62
    print(sep)
    print("  Cedar Grove H-Number Decoder — Self-test")
    print(sep)
    tests = [
        ("B", "20H",  1,    "H000001"),
        ("B", "40H",  45,   "H000045"),
        ("A", "1",    44,   "H000044"),
        ("D", "1U",   837,  "H000837"),
        ("D", "40H",  881,  "H000881"),
        ("C", "417",  1672, "H001672"),
    ]
    all_ok = True
    for sec, lot, exp_h, exp_fmt in tests:
        h, hfmt = h_lot(sec, lot)
        ok = (h == exp_h)
        all_ok = all_ok and ok
        tag = "PASS" if ok else f"FAIL  expected H{exp_h:06d} got {hfmt}"
        print(f"  H('{sec}', '{lot:>5}')  =  {hfmt}   [{tag}]")
    print()

    # Reverse lookups
    for h_in, exp_sec, exp_lot in [(1,"B","20H"),(44,"A","1"),(837,"D","1U"),(1672,"C","417")]:
        r = decode_h(h_in)
        ok = r and r["section"] == exp_sec and r["lot_label"] == exp_lot
        all_ok = all_ok and ok
        found = f"Section {r['section']} Lot {r['lot_label']}" if r else "None"
        tag = "PASS" if ok else "FAIL"
        print(f"  decode_h({h_in:4d})  →  {found:<24}  [{tag}]")
    print()

    for sec, dec in [("B",B_DECODER),("A",A_DECODER),("D",D_DECODER),("C",C_DECODER)]:
        real = sum(1 for v in dec.values() if v[1] > 0)
        print(f"  Section {sec}: {real:4d} lots mapped  (expected {ROWS * 22} = {ROWS*22})")
    print()
    print(f"  H range:  H000001  …  H{OFFSET*2:06d}")
    print(f"  Overall:  {'ALL PASSED ✓' if all_ok else 'FAILURES — see above ✗'}")
    print(sep)


# ─────────────────────────────────────────────────────────────────────
# INTERACTIVE CLI
# ─────────────────────────────────────────────────────────────────────

def _show(section, lot_label, grave=None):
    h, hfmt = h_lot(section, lot_label)
    if h is None:
        print(f"\n  ERROR: {hfmt}\n"); return
    dec = _DECODERS[section.upper()]
    c, r = dec[lot_label.strip()]
    is_dc = section.upper() in ('C', 'D')
    off_str = f"{OFFSET}+" if is_dc else ""
    c_str = str(c) if section.upper() in ('B','D') else f"{N_B}+{c}"
    print(f"\n  Section {section.upper()}  ·  Lot {lot_label}")
    print(f"  Column from right (c) : {c}")
    print(f"  Row from bottom   (r) : {r}")
    print(f"  Formula : {off_str}{SWEEP}×{r-1}+{c_str}  =  {h}")
    print(f"  ┌─────────────────────────────────┐")
    print(f"  │  H Lot :   {hfmt}          │")
    if grave:
        hg, hgfmt = h_grave(section, lot_label, grave)
        print(f"  │  H Grave:  {hgfmt}         │")
    print(f"  └─────────────────────────────────┘\n")


def interactive():
    sep = "=" * 62
    print(sep)
    print("  Cedar Grove H-Number Decoder   (Sections A B C D)")
    print(f"  SWEEP={SWEEP}  ROWS={ROWS}  OFFSET(D/C)={OFFSET}  MAX=H{OFFSET*2:06d}")
    print(sep)
    print("  lookup B 20H          → lot H number")
    print("  lookup D 1U           → D/C pass start")
    print("  lookup C 417          → D/C pass end")
    print("  lookup A 100 3        → grave H number  (lot 100, grave 3)")
    print("  reverse 837           → which lot is H000837")
    print("  table A               → print full section table")
    print("  export [dir]          → save all 4 CSV files")
    print("  test                  → run self-test")
    print("  quit                  → exit")
    print("-" * 62)

    while True:
        try:
            raw = input("  > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Bye."); break
        if not raw:
            continue
        parts = raw.split()
        cmd = parts[0].lower()

        if cmd in ("quit", "exit", "q"):
            print("  Bye."); break

        elif cmd == "lookup":
            if len(parts) < 3:
                print("  Usage: lookup <section> <lot> [grave]"); continue
            grv = int(parts[3]) if len(parts) >= 4 else None
            _show(parts[1], parts[2], grv)

        elif cmd == "reverse":
            if len(parts) < 2:
                print("  Usage: reverse <h_number>"); continue
            res = decode_h(int(parts[1]))
            if res is None:
                print(f"  H{int(parts[1]):06d} out of range (max H{OFFSET*2:06d})")
            else:
                print(f"\n  {res['h_formatted']}  →  "
                      f"Section {res['section']}  Lot {res['lot_label']}  "
                      f"(c={res['c']}, r={res['r']})\n")

        elif cmd == "table":
            if len(parts) < 2:
                print("  Usage: table <A|B|C|D>"); continue
            rows = full_table(parts[1])
            print(f"\n  Section {parts[1].upper()} — {len(rows)} lots")
            print(f"  {'H Lot':<10} {'Lot':<8} {'c':>3} {'r':>3}  "
                  f"{'Grave 1':<11} {'Grave 2':<11} {'Grave 3'}")
            print("  " + "─"*58)
            for row in rows:
                print(f"  {row['h_lot']:<10} {row['lot_label']:<8} "
                      f"{row['col_c']:>3} {row['row_r']:>3}  "
                      f"{row['h_grave_1']}  {row['h_grave_2']}  {row['h_grave_3']}")
            print()

        elif cmd == "export":
            out = parts[1] if len(parts) >= 2 else "."
            print(f"\n  Exporting to: {os.path.abspath(out)}")
            export_all_csv(out)
            print()

        elif cmd == "test":
            self_test()

        else:
            print(f"  Unknown command '{cmd}'.")


# ─────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        self_test(); sys.exit(0)

    if len(sys.argv) > 1 and sys.argv[1] == "--export":
        out = sys.argv[2] if len(sys.argv) > 2 else "."
        export_all_csv(out); sys.exit(0)

    if len(sys.argv) >= 3 and sys.argv[1] not in ("--test", "--export"):
        grv = int(sys.argv[3]) if len(sys.argv) > 3 else None
        _show(sys.argv[1], sys.argv[2], grv); sys.exit(0)

    self_test()
    interactive()
