"""
Cedar Grove Cemetery — H-Number Decoder  (v2)
================================================
Sections A, B, C, D — updated to include Section B's irregular north strip.

TWO PASSES:
  PASS 1 — B + A  (H000001 … H000696)
  PASS 2 — D + C  (H000697 … H001392)

FORMULA
-------
  SWEEP  = N_B + N_A  =  2 + 22  =  24
  ROWS   = 29  (19 main-grid rows + 10 strip-only rows above)
  OFFSET = SWEEP × ROWS  =  24 × 29  =  696

  H( B_strip, lot ) =          SWEEP × (r−1)  +  1
  H( B_main,  lot ) =          SWEEP × (r−1)  +  2
  H( A,       lot ) =          SWEEP × (r−1)  +  2  +  c_A
  H( D_strip, lot ) = OFFSET + SWEEP × (r−1)  +  1
  H( D_main,  lot ) = OFFSET + SWEEP × (r−1)  +  2
  H( C,       lot ) = OFFSET + SWEEP × (r−1)  +  2  +  c_C

  H_grave = H_lot × 10 + g

SWEEP COLUMNS PER LEVEL r
  c=1  : B strip lot  (373, 374, 375, …, 394)   or D strip lot (1U, 1T, …, 1)
  c=2  : B main lot   (20H, 40H, …)              or D main lot (40H, 60H, …)
           [c=2 is empty for r=20..29 — main grid only has 19 rows]
  c=3..24: A (or C) columns 1..22

SECTION B STRIP — 29 base columns (right to left, bottom to top):
  r=1:  373   r=2:  374   r=3:  375   r=4:  376H  r=5:  376
  r=6:  377   r=7:  378   r=8:  379   r=9:  380   r=10: 380H
  r=11: 381   r=12: 381B  r=13: 382   r=14: 383   r=15: 384
  r=16: 384H  r=17: 385   r=18: 386   r=19: 387   r=20: 388
  r=21: 388H  r=22: 389   r=23: 390H  r=24: 390   r=25: 391
  r=26: 392   r=27: 393   r=28: 394 ← wait, need 29 levels
  
  NOTE: Sub-lots (384HA, 385A, 386A, 387A/B, 388A/B, 388HA/HB, 389A, 390A/B/C)
  share their base lot's H-number (same H_lot, different grave within the lot).

KEY ANCHORS
  B-373  = H000001  (first lot ever, strip r=1)
  A-1    = H000024  (last of sweep level 1)
  B-394  = H000673  (strip r=29)  
  D-1U   = H000697  (first D/C lot)
  C-417  = H001392  (last C lot)
"""

import csv, os

# ─────────────────────────────────────────────────────────────────────
N_B    = 2    # c=1: strip, c=2: main H-lot
N_A    = 22
N_D    = 2    # mirrors B
N_C    = 22
SWEEP  = N_B + N_A   # 24
ROWS   = 29           # 19 main-grid rows + rows 20-29 from strip sub-lots / extras
OFFSET = SWEEP * ROWS # 696

# ─────────────────────────────────────────────────────────────────────
# SECTION B STRIP — lot label → row r (r=1..29)
# Right-to-left order = r=1 (rightmost/east) to r=29 (leftmost/west)
# Sub-lots share the base lot's r value (same H_lot number)
# ─────────────────────────────────────────────────────────────────────
B_STRIP = {
    # 29 base columns, right (east) to left (west) = r=1..29
    # Sub-lots (lettered suffixes) share their base column's r value (same H_lot)
    '373':1,   '374':2,   '375H':3,  '375':4,   '376H':5,
    '376':6,   '377':7,   '378':8,   '379':9,   '380':10,
    '380H':11, '381':12,  '381A':13, '382':14,  '383':15,
    '384':16,  '384H':17, '384HA':17,            # 384HA shares r=17
    '385':18,  '385A':18,                         # 385A shares r=18
    '386':19,  '386A':19,
    '387':20,  '387A':20, '387B':20,
    '388':21,  '388A':21, '388B':21,
    '388H':22, '388HA':22,'388HB':22,
    '389':23,  '389A':23,
    '390H':24,
    '390':25,  '390A':25, '390B':25, '390C':25,
    '391':26,  '392':27,  '393':28,  '394':29,
}

# ─────────────────────────────────────────────────────────────────────
# SECTION D STRIP — mirrors B (r=1..29 equivalent)
# Row 1: lettered sub-lots of lot 1 (1U=r=1, 1T=r=2, … 1=r=22)
# Rows 2..19: same arithmetic as old B main grid
# ─────────────────────────────────────────────────────────────────────
_D_ROW1 = {
    1:'1U',2:'1T',3:'1S',4:'1R',5:'1Q',6:'1P',7:'1O',8:'1N',9:'1M',
    10:'1L',11:'1K',12:'1J',13:'1I',14:'1H',15:'1G',16:'F1',17:'1E',
    18:'1D',19:'1C',20:'1B',21:'1A',22:'1'
}
D_STRIP = {v: k for k, v in _D_ROW1.items()}  # label → r

# ─────────────────────────────────────────────────────────────────────
# SECTION B MAIN GRID — lot → (col_in_main, row_in_main)
# main col 1 = H-lot (20H, 40H, …) for rows 1..19
# main col 2 = 19A (r=1), then 39,59,… (r=2..19)
# … same structure as old B decoder but ROWS capped at 19
# ─────────────────────────────────────────────────────────────────────
def build_B_main():
    d = {}
    for r in range(1, 20):   # rows 1..19 only
        d[f"{20*r}H"] = r    # col=1 (the single main-grid H-lot column)
    d["19A"] = 1             # special r=1 position
    # Regular lots mapped by row (20 per row, cols 3..22 in old system)
    # Now we encode just the row — column within main grid handled separately
    for r in range(2, 20):
        d[str(19 + 20*(r-1))] = r
    for r in range(1, 20):
        for c in range(3, 22):
            lot = (r-1)*20 + (22-c)
            d[str(lot)] = r
    for r in range(1, 20):
        d[str(12 + 19*(r-1))] = r
    return d

# ─────────────────────────────────────────────────────────────────────
# SECTION A DECODER — lot → (c, r)  (unchanged from v1)
# ─────────────────────────────────────────────────────────────────────
def build_A_decoder():
    d = {}
    for r in range(1, ROWS+1):
        b = 19*(r-1)
        if r > 19: break  # A only has 19 rows
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
# SECTION D MAIN GRID — mirrors B main  (rows 2..19)
# ─────────────────────────────────────────────────────────────────────
def build_D_main():
    d = {}
    for r in range(2, 20):
        d[f"{20*r}H"] = r
        if r == 2:
            d["29H"] = 2
        else:
            d[str(19 + 20*(r-1))] = r
        for c in range(3, 22):
            d[str((r-1)*20 + (22-c))] = r
        d[str(20*(r-1)+1)] = r
    return d

# ─────────────────────────────────────────────────────────────────────
# SECTION C DECODER — lot → (c, r)  (unchanged, inc=23)
# ─────────────────────────────────────────────────────────────────────
def build_C_decoder():
    d = {}
    d['1C'] = (22, 0); d['2C'] = (21, 0)
    for r in range(1, ROWS+1):
        for c in range(1, N_C+1):
            lot_num = 2 + (r-1)*23 + (23-c)
            if c == 1 and r == ROWS:
                d['438H'] = (c, r)
            else:
                d[str(lot_num)] = (c, r)
    return d

B_MAIN    = build_B_main()
A_DECODER = build_A_decoder()
D_MAIN    = build_D_main()
C_DECODER = build_C_decoder()


# ─────────────────────────────────────────────────────────────────────
# HASH FUNCTIONS
# ─────────────────────────────────────────────────────────────────────

def h_lot(section, lot_label):
    """
    Return (h_number, 'H000001') for a section + legacy lot label.

    B/D strip lots: section='B', lot='373' or '384HA' etc.
    B/D main lots:  section='B', lot='20H' or '19A' etc.
    A/C lots:       section='A', lot='100' etc.

    Sub-lots (384HA, 385A, etc.) return the SAME H as their base lot.
    """
    sec = section.upper().strip()
    lot = str(lot_label).strip()

    if sec == 'B':
        # Check strip first
        if lot in B_STRIP:
            r = B_STRIP[lot]
            h = SWEEP * (r-1) + 1
            return h, f"H{h:06d}"
        # Check main grid
        if lot in B_MAIN:
            r = B_MAIN[lot]
            h = SWEEP * (r-1) + 2
            return h, f"H{h:06d}"
        return None, f"Lot '{lot}' not found in Section B."

    elif sec == 'A':
        if lot not in A_DECODER:
            return None, f"Lot '{lot}' not found in Section A."
        c, r = A_DECODER[lot]
        h = SWEEP*(r-1) + N_B + c
        return h, f"H{h:06d}"

    elif sec == 'D':
        # Check strip first
        if lot in D_STRIP:
            r = D_STRIP[lot]
            h = OFFSET + SWEEP*(r-1) + 1
            return h, f"H{h:06d}"
        # Check main grid
        if lot in D_MAIN:
            r = D_MAIN[lot]
            h = OFFSET + SWEEP*(r-1) + 2
            return h, f"H{h:06d}"
        return None, f"Lot '{lot}' not found in Section D."

    elif sec == 'C':
        if lot not in C_DECODER:
            return None, f"Lot '{lot}' not found in Section C."
        c, r = C_DECODER[lot]
        if r == 0: return None, f"Lot '{lot}' is a virtual entry."
        h = OFFSET + SWEEP*(r-1) + N_D + c
        return h, f"H{h:06d}"

    return None, f"Unknown section '{section}'."


def h_grave(section, lot_label, grave_number):
    h, msg = h_lot(section, lot_label)
    if h is None: return None, msg
    g = int(grave_number)
    if not (1 <= g <= 9): return None, f"Grave {g} out of range 1-9."
    hg = h*10 + g
    return hg, f"H{hg:07d}"


def decode_h(h_number):
    n = int(h_number)
    if n < 1 or n > OFFSET*2: return None
    if n <= OFFSET:
        level = (n-1)//SWEEP; pos = (n-1)%SWEEP+1; r = level+1
        if pos == 1:
            # B strip
            lot = next((k for k,v in B_STRIP.items() if v==r and k==min(
                (k2 for k2,v2 in B_STRIP.items() if v2==r), key=len)), None)
            return {'section':'B','lot':lot,'col':1,'r':r,'type':'strip','h_formatted':f"H{n:06d}"}
        elif pos == 2:
            lot = next((k for k,v in B_MAIN.items() if v==r), None)
            return {'section':'B','lot':lot,'col':2,'r':r,'type':'main','h_formatted':f"H{n:06d}"}
        else:
            c = pos-2
            lot = next((k for k,(cv,rv) in A_DECODER.items() if cv==c and rv==r), None)
            return {'section':'A','lot':lot,'col':c,'r':r,'type':'main','h_formatted':f"H{n:06d}"}
    else:
        adj = n-OFFSET; level=(adj-1)//SWEEP; pos=(adj-1)%SWEEP+1; r=level+1
        if pos == 1:
            lot = next((k for k,v in D_STRIP.items() if v==r), None)
            return {'section':'D','lot':lot,'col':1,'r':r,'type':'strip','h_formatted':f"H{n:06d}"}
        elif pos == 2:
            lot = next((k for k,v in D_MAIN.items() if v==r), None)
            return {'section':'D','lot':lot,'col':2,'r':r,'type':'main','h_formatted':f"H{n:06d}"}
        else:
            c = pos-2
            lot = next((k for k,(cv,rv) in C_DECODER.items() if cv==c and rv==r), None)
            return {'section':'C','lot':lot,'col':c,'r':r,'type':'main','h_formatted':f"H{n:06d}"}


# ─────────────────────────────────────────────────────────────────────
# TABLE EXPORT
# ─────────────────────────────────────────────────────────────────────

def full_table(section):
    sec = section.upper()
    rows = []
    if sec == 'B':
        # Strip lots
        seen_r = {}
        for lot, r in B_STRIP.items():
            if r not in seen_r:  # only base lots for the table
                seen_r[r] = lot
        for lot, r in sorted(seen_r.items(), key=lambda x: x[0]):
            h, hfmt = h_lot('B', lot)
            rows.append({'section':'B','lot_label':lot,'type':'strip',
                'row_r':r,'col_c':1,'h_lot_number':h,'h_lot':hfmt,
                **{f'h_grave_{g}': (h_grave('B',lot,g) or (None,'—'))[1] for g in range(1,7)}})
        # Main lots (H-lots only as representative)
        for lot, r in B_MAIN.items():
            if lot.endswith('H') or lot == '19A':
                h, hfmt = h_lot('B', lot)
                rows.append({'section':'B','lot_label':lot,'type':'main',
                    'row_r':r,'col_c':2,'h_lot_number':h,'h_lot':hfmt,
                    **{f'h_grave_{g}': (h_grave('B',lot,g) or (None,'—'))[1] for g in range(1,7)}})
    elif sec == 'A':
        for lot,(c,r) in A_DECODER.items():
            h,hfmt=h_lot('A',lot)
            rows.append({'section':'A','lot_label':lot,'type':'main',
                'row_r':r,'col_c':c,'h_lot_number':h,'h_lot':hfmt,
                **{f'h_grave_{g}': (h_grave('A',lot,g) or (None,'—'))[1] for g in range(1,7)}})
    elif sec == 'D':
        for lot,r in D_STRIP.items():
            h,hfmt=h_lot('D',lot)
            rows.append({'section':'D','lot_label':lot,'type':'strip',
                'row_r':r,'col_c':1,'h_lot_number':h,'h_lot':hfmt,
                **{f'h_grave_{g}': (h_grave('D',lot,g) or (None,'—'))[1] for g in range(1,7)}})
        for lot,r in D_MAIN.items():
            if lot.endswith('H') or lot == '29H':
                h,hfmt=h_lot('D',lot)
                rows.append({'section':'D','lot_label':lot,'type':'main',
                    'row_r':r,'col_c':2,'h_lot_number':h,'h_lot':hfmt,
                    **{f'h_grave_{g}': (h_grave('D',lot,g) or (None,'—'))[1] for g in range(1,7)}})
    elif sec == 'C':
        for lot,(c,r) in C_DECODER.items():
            if r == 0: continue
            h,hfmt=h_lot('C',lot)
            rows.append({'section':'C','lot_label':lot,'type':'main',
                'row_r':r,'col_c':c,'h_lot_number':h,'h_lot':hfmt,
                **{f'h_grave_{g}': (h_grave('C',lot,g) or (None,'—'))[1] for g in range(1,7)}})
    rows = [r for r in rows if r['h_lot_number'] is not None]
    rows.sort(key=lambda x: x['h_lot_number'])
    return rows


def export_csv(section, filepath):
    rows = full_table(section)
    if not rows: return 0
    with open(filepath,'w',newline='',encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    return len(rows)


def export_all_csv(out_dir='.'):
    os.makedirs(out_dir, exist_ok=True)
    for sec in ('B','A','D','C'):
        path = os.path.join(out_dir, f"cedar_grove_section_{sec}_h_table.csv")
        n = export_csv(sec, path)
        print(f"  Section {sec}: {n:4d} rows → {path}")


# ─────────────────────────────────────────────────────────────────────
# SELF-TEST
# ─────────────────────────────────────────────────────────────────────

def self_test():
    sep = "="*62
    print(sep)
    print("  Cedar Grove H-Number Decoder v2 — Self-test")
    print(f"  SWEEP={SWEEP}  ROWS={ROWS}  OFFSET={OFFSET}")
    print(sep)
    tests = [
        # Pass 1 anchors
        ('B','373',    1,   'H000001'),  # first lot ever
        ('B','20H',    2,   'H000002'),  # first B main lot
        ('A','19',     3,   'H000003'),  # first A lot
        ('A','1',      24,  'H000024'),  # last of sweep level 1
        ('B','374',    25,  'H000025'),  # strip r=2
        ('B','40H',    26,  'H000026'),  # main r=2
        ('B','394',    673, 'H000673'),  # strip r=29
        # Pass 2 anchors
        ('D','1U',     697, 'H000697'),  # first D/C lot
        ('C','417',    1152,'H001152'),  # C lot 417 at c=22 r=19
    ]
    all_ok = True
    for sec,lot,exp,expf in tests:
        h,hfmt = h_lot(sec,lot)
        ok = (h == exp)
        all_ok = all_ok and ok
        tag = 'PASS' if ok else f'FAIL expected H{exp:06d} got {hfmt}'
        print(f"  H('{sec}','{lot:6s}') = {hfmt}   [{tag}]")
    print()
    print(f"  Max H number: H{OFFSET*2:06d}")
    print(f"  Overall: {'ALL PASSED ✓' if all_ok else 'FAILURES ✗'}")
    print(sep)


# ─────────────────────────────────────────────────────────────────────
# INTERACTIVE CLI
# ─────────────────────────────────────────────────────────────────────

def _show(section, lot_label, grave=None):
    h, hfmt = h_lot(section, lot_label)
    if h is None: print(f"\n  ERROR: {hfmt}\n"); return
    print(f"\n  Section {section.upper()}  ·  Lot {lot_label}")
    print(f"  H Lot:   {hfmt}")
    if grave:
        hg, hgfmt = h_grave(section, lot_label, grave)
        print(f"  H Grave: {hgfmt}  (grave {grave})")
    print()


def interactive():
    sep = "="*62
    print(sep)
    print("  Cedar Grove H-Number Decoder v2  (A B C D)")
    print(f"  SWEEP={SWEEP}  ROWS={ROWS}  OFFSET={OFFSET}  MAX=H{OFFSET*2:06d}")
    print(sep)
    print("  lookup B 373          → H000001 (first strip lot)")
    print("  lookup B 394          → H000673 (last strip lot)")
    print("  lookup D 1U           → H000697 (first D/C)")
    print("  lookup A 100 3        → grave H number")
    print("  reverse 1             → which lot is H000001")
    print("  export [dir]          → save all 4 CSVs")
    print("  test                  → run self-test")
    print("  quit                  → exit")
    print("-"*62)
    while True:
        try: raw = input("  > ").strip()
        except (EOFError, KeyboardInterrupt): print("\n  Bye."); break
        if not raw: continue
        parts = raw.split(); cmd = parts[0].lower()
        if cmd in ('quit','exit','q'): print("  Bye."); break
        elif cmd == 'lookup':
            if len(parts)<3: print("  Usage: lookup <section> <lot> [grave]"); continue
            grv = int(parts[3]) if len(parts)>=4 else None
            _show(parts[1], parts[2], grv)
        elif cmd == 'reverse':
            if len(parts)<2: print("  Usage: reverse <h_number>"); continue
            res = decode_h(int(parts[1]))
            if res is None: print(f"  Out of range (max H{OFFSET*2:06d})")
            else: print(f"\n  {res['h_formatted']}  →  Section {res['section']}  Lot {res['lot']}  (r={res['r']})\n")
        elif cmd == 'export':
            out = parts[1] if len(parts)>=2 else '.'
            export_all_csv(out)
        elif cmd == 'test': self_test()
        else: print(f"  Unknown command '{cmd}'.")


if __name__ == '__main__':
    import sys
    if len(sys.argv)>1 and sys.argv[1]=='--test': self_test(); sys.exit(0)
    if len(sys.argv)>1 and sys.argv[1]=='--export':
        export_all_csv(sys.argv[2] if len(sys.argv)>2 else '.'); sys.exit(0)
    if len(sys.argv)>=3 and sys.argv[1] not in ('--test','--export'):
        grv = int(sys.argv[3]) if len(sys.argv)>3 else None
        _show(sys.argv[1], sys.argv[2], grv); sys.exit(0)
    self_test()
    interactive()
