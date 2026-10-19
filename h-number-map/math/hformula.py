"""
hformula.py - the H-number rebuilt as arithmetic.

H(section, lot-label) is computed WITHOUT looking anything up in the decoder's lot tables.  Every H-number is
        H = O  +  (lots in all earlier rows of the same pass)  +  (lots in the same row that come first)  +  k
i.e. the position of the lot along ONE fixed sweep through the cemetery.  The pieces that are regular are closed-form;
the pieces the map made irregular are given as small constant tables (row widths, twin lists, ordered lists).
Each function returns (H, tier):  'closed' = pure arithmetic, 'rows' = arithmetic + per-row constants, 'list' = ordered list.
"""
import re

# ---------------------------------------------------------------- constants
N, SW, ROWS = 22, 44, 19           # pass 1: 22 columns per section, 44 lots per level, 19 levels
O1 = SW * ROWS                     # 836 = lots in pass 1 (B + A)
WD = [43] + [22] * 14 + [20, 20, 20, 21, 21, 21, 21, 21]                                     # D row widths, rows 1..23
WC = [21, 21, 22, 21, 21, 22, 22, 22, 20, 22, 22, 20, 21, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22]   # C row widths, rows 1..24
WF = [18] * 11 + [0]                                                                         # F row widths (F has 11 rows)
WE = [22] * 8 + [21, 21, 22, 22]                                                             # E row widths, rows 1..12
WG = [22, 22, 22, 15]; WH = [23, 23, 23, 23]                                                 # G, H row widths
CT = [19, 38, 57, 76, 95, 114, 133, 152, 171, 190, 209, 228, 247, 263, 279, 295, 311, 330, 349, 368, 384, 400, 416, 432]  # C: top lot of each row
CTRIO = {14, 15, 16, 17, 21, 22, 23, 24}                                                      # C rows that start with  nC, nB, nA
# C twins (the 'H' lots), per row: (number, 'b' = H-lot sits before the plain lot, 'a' = after).  Row 8 uses 142 (the decoder has the typo 124H).
CTW = {1: [(9, 'b'), (5, 'b')], 2: [(32, 'b'), (24, 'b')], 3: [(51, 'b'), (47, 'b'), (43, 'b')], 4: [(66, 'b'), (62, 'b')], 5: [(85, 'b'), (81, 'b')],
       6: [(108, 'b'), (104, 'b'), (100, 'b')], 7: [(127, 'b'), (123, 'b'), (119, 'b')], 8: [(146, 'b'), (142, 'b'), (138, 'b')], 9: [(165, 'b')],
       10: [(184, 'b'), (180, 'b'), (176, 'b')], 11: [(203, 'b'), (199, 'b'), (195, 'b')], 12: [(222, 'b')], 13: [(241, 'a'), (233, 'b')],
       14: [(260, 'b'), (256, 'b'), (252, 'b')], 15: [(276, 'a'), (272, 'b'), (268, 'b')], 16: [(292, 'b'), (288, 'b'), (284, 'b')], 17: [(308, 'b'), (304, 'b'), (300, 'b')],
       18: [(324, 'b'), (320, 'b'), (316, 'a')], 19: [(343, 'a'), (339, 'b'), (335, 'a')], 20: [(362, 'b'), (358, 'b'), (354, 'a')], 21: [(381, 'b'), (377, 'b'), (373, 'a')],
       22: [(397, 'a'), (393, 'b'), (389, 'a')], 23: [(413, 'b'), (409, 'b'), (405, 'a')], 24: [(429, 'a'), (425, 'b'), (421, 'a')]}
DM_TW = (545, 549, 556, 559, 560, 562, 563)       # D margin lots that have an H twin (twin comes after the plain lot)
BMARGIN = ['373', '374', '375', '376', '376H', '377', '378', '379', '380', '380H', '381', '382', '383', '384', '384HA', '384H', '385A', '385', '386A', '386', '387B', '387A', '387',
           '388B', '388A', '388', '388HB', '388HA', '388H', '389B', '389A', '389', '390C', '390B', '390A', '390', '390H', '391', '392', '393', '394']
MFIRST = ['11', '12', '14', '15', '16', '18', '19', '20', '23', '24', '25', '28', '29', '30', '31', '34', '35', '36', '37', '40', '41', '42', '43', '46', '47', '48', '49', '52', '53', '54', '55', '61',
          '58', '59', '60', '66', '67', '64', '65', '71', '72', '73', '74', '75', '70', '76', '77', '78', '79', '80', '81']      # the 51 lots of M rows 1-12
KORDER = ['1', '2', '3', '6', '7', '8', '9', '13', '14', '15', '16', '22', '5', '11', '12', '18', '19', '25', '26', '31', '32', '36', '37', '38', '42', '43', '44', '45', '50', '51', '52', '57', '58', '59',
          '64', '65', '66', '72', '73', '79', '80', '86', '87', '93', '94', '101', '102', '109', '110', '117', '118', '125', '126', '133', '134', '141', '142', '149', '150', '158', '159', '167', '168', '176',
          '177', '185', '186', '195', '196', '205', '206', '215', '216', '225', '226', '235', '236', '246', '247', '256', '257', '258', '259', '268', '269', '270', '271', '280', '281', '282', '283', '293',
          '294', '295', '296', '306', '307', '308', '309', '319', '320', '321', '322', '332', '333', '334', '335', '345', '346', '347', '348', '358', '359', '360', '361']
# base H (= number of lots swept before the pass starts)
O_DC, O_EF, O_MARGIN_B, O_MARGIN_D, O_MARGIN_F, O_GH, O_M, O_K, O_J, O_I, O_L = 836, 1871, 2331, 2372, 2401, 2413, 2586, 2835, 2950, 3082, 3146

def pre(w1, w2, r):
    """lots swept in rows 1..r-1 of a two-section pass whose row widths are w1, w2"""
    return sum((w1[j] if j < len(w1) else 0) + (w2[j] if j < len(w2) else 0) for j in range(r - 1))

def parse(lab):
    m = re.match(r'^([A-Z]?)(\d+)([A-Za-z_0-9]*)$', lab)
    return (m.group(1), int(m.group(2)), m.group(3)) if m else (None, None, None)

# ---------------------------------------------------------------- pass 1 : B and A (pure formulas)
def H_B_grid(n, sf):
    if sf == 'H' and n % 20 == 0 and 1 <= n // 20 <= ROWS: r, c = n // 20, 1                 # H-lots 20H,40H..380H : first column
    elif sf == 'A' and n == 19: r, c = 1, 2                                                  # the one lettered lot "19A"
    elif sf == '':
        rr = next((x for x in range(1, ROWS + 1) if n == 12 + 19 * (x - 1)), None)
        if rr is not None: r, c = rr, N                                                       # last column: 12,31,50,... (increment 19 - wins any clash)
        elif 1 <= n <= 380 and n % 20 != 0: r = (n - 1) // 20 + 1; c = N - (n - 20 * (r - 1))   # body: increment 20, columns 3..21, right-to-left
        else: return None
    else: return None
    return SW * (r - 1) + c, 'closed'

def H_A_grid(n, sf):
    if not (1 <= n <= 19 * ROWS): return None
    r = (n - 1) // 19 + 1; q = n - 19 * (r - 1)                                              # increment 19; q = place inside the row
    if sf == '': c = 20 - q + (q <= 13) + (q <= 5) + (q <= 1)
    elif sf == 'H' and q in (13, 5, 1): c = 20 - q + (q <= 5) + (q <= 1)                      # H-lot sits just before its twin
    else: return None
    return SW * (r - 1) + N + c, 'closed'

# ---------------------------------------------------------------- pass 2 : D and C (rows interleaved: D row r, then C row r)
# D row structure.  rows 2-15 are regular; rows 16-23 are described by "blocks": (row, first lot k0, top lot, bottom lot) -> k = k0 + top - n
DBLOCK = [(16, 2, 310, 301), (16, 12, 420, 412), (17, 2, 321, 312), (17, 12, 411, 403), (18, 2, 332, 323), (18, 12, 402, 394),
          (19, 2, 344, 344), (19, 3, 343, 334), (19, 13, 393, 385), (20, 2, 355, 355), (20, 3, 354, 345), (20, 13, 384, 376),
          (21, 2, 366, 366), (21, 3, 365, 356), (21, 13, 375, 367), (22, 1, 541, 521), (23, 1, 520, 500)]
DHLOT = {16: 311, 17: 322, 18: 333, 19: 344, 20: 355, 21: 366}            # the H-lot that opens rows 16-21 (k = 1)

def H_D(pf, n, sf, lab):
    """Section D, main grid (the margin strip 542-563H is handled in H_margin_D)"""
    base = None
    if lab in ('1U', '1T', '1S', '1R', '1Q', '1P', '1O', '1N', '1M', '1L', '1K', '1J', '1I', '1H'): r, k, tier = 1, 1 + (ord('U') - ord(lab[1])), 'rows'
    elif pf == '' and sf == '' and 1 <= n <= 20: r, k, tier = 1, 15 + (20 - n), 'rows'
    elif lab in ('1A', '1B', '1C', '1D', '1E'): r, k, tier = 1, 35 + (ord(lab[1]) - ord('A')), 'rows'
    elif lab == 'F1': r, k, tier = 1, 40, 'rows'
    elif lab == '1G': r, k, tier = 1, 41, 'rows'
    elif lab == '1H_2': r, k, tier = 1, 42, 'rows'
    elif lab == '1I_2': r, k, tier = 1, 43, 'rows'
    elif pf == '' and sf == 'H' and 20 <= n <= 280 and n % 20 == 0: r, k, tier = n // 20 + 1, 1, 'closed'         # 20H, 40H ... 280H : first lot of rows 2..15
    elif pf == '' and sf == 'H' and 29 <= n <= 289 and n % 20 == 9: r, k, tier = (n + 11) // 20, 13, 'closed'      # 29H, 49H ... 289H : 13th lot
    elif pf == '' and sf == 'H' and any(n == v for v in DHLOT.values()): r = next(x for x, v in DHLOT.items() if v == n); k, tier = 1, 'rows'
    elif pf == '' and sf == '' and 21 <= n <= 300:
        r = (n - 1) // 20 + 1; j = 20 * r - n; k, tier = (j + 2 if j <= 10 else j + 3), 'closed'                 # 20 lots per row, 2 H-lots slipped in
    elif pf == '' and sf in ('A', 'B') and 367 <= n <= 384:                                                    # double-row lots: nA and nB share the position of n
        return H_D(pf, n, '', str(n))
    elif pf == '' and sf == '':
        hit = next(((r_, k0 + top - n) for (r_, k0, top, bot) in DBLOCK if bot <= n <= top), None)
        if hit is None: return None
        r, k = hit; tier = 'rows'
    else: return None
    return O_DC + pre(WD, WC, r) + k, tier

def H_C(pf, n, sf):
    r = next((x for x in range(1, 25) if n <= CT[x - 1]), None)
    if r is None or (r > 1 and n <= CT[r - 2]): return None
    trio = 3 if r in CTRIO else 0
    tw = CTW[r]
    def before(nn): return sum(1 for (t, f) in tw if t > nn or (t == nn and f == 'b'))
    if sf == '': k = (CT[r - 1] - n) + 1 + trio + before(n)
    elif sf in ('C', 'B', 'A') and r in CTRIO and n == CT[r - 1]: k = 'CBA'.index(sf) + 1
    elif sf == 'H' and (n, 'b') in tw: k = (CT[r - 1] - n) + 1 + trio + before(n) - 1
    elif sf == 'H' and (n, 'a') in tw: k = (CT[r - 1] - n) + 1 + trio + before(n) + 1
    else: return None
    return O_DC + pre(WD, WC, r) + (WD[r - 1] if r <= len(WD) else 0) + k, 'rows'

# ---------------------------------------------------------------- pass 3 : F and E
def H_F(pf, n, sf):
    if sf != '' or pf != '': return None
    if 1 <= n <= 198:
        r = (n - 1) // 18 + 1; c = 19 - (n - 18 * (r - 1))                  # increment 18, no H-lots; right-to-left
        return O_EF + pre(WF, WE, r) + c, 'closed'
    if 199 <= n <= 210: return O_MARGIN_F + (n - 198), 'closed'                # margin strip: just 199..210 in a row
    return None

EBLOCK = [(9, 1, 169, 164), (9, 8, 163, 163), (9, 9, 162, 160), (9, 13, 159, 159), (9, 14, 158, 156), (9, 18, 155, 155), (9, 19, 154, 153),
          (10, 1, 177, 172), (10, 8, 171, 171), (10, 9, 170, 170), (10, 12, 199, 190),
          (11, 1, 183, 178), (11, 8, 213, 210), (11, 13, 209, 209), (11, 14, 208, 200),
          (12, 1, 189, 184), (12, 8, 227, 224), (12, 13, 223, 223), (12, 14, 222, 214)]
EHLOT = {('163', 9): 7, ('159', 9): 12, ('155', 9): 17, ('171', 10): 7, ('177', 11): 7, ('209', 11): 12, ('183', 12): 7, ('223', 12): 12, ('199BH', 10): 11}
def H_E(pf, n, sf, lab):
    base = lab
    if re.match(r'^(152|169|19\d)[AB]$', lab) and n in (152, 169, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199):  # double-row lots share ONE position
        r, k = (9, 21) if n == 152 else ((10, 10) if n == 169 else (10, 12 + (199 - n)))
        return O_EF + pre(WF, WE, r) + WF[r - 1] + k, 'rows'
    if lab == '199BH': return O_EF + pre(WF, WE, 10) + WF[9] + 11, 'rows'
    if pf != '': return None
    if sf == '' and 1 <= n <= 152 and not (n <= 152 and False):
        # rows 1..8 : increment 19, H-lots slipped in before q = 13, 9, 5
        r = (n - 1) // 19 + 1; q = n - 19 * (r - 1)
        k = (19 - q + 1) + sum(1 for t in (13, 9, 5) if t >= q)
        return O_EF + pre(WF, WE, r) + WF[r - 1] + k, 'closed'
    if sf == 'H' and n <= 152 and (n - 19 * ((n - 1) // 19)) in (13, 9, 5):
        r = (n - 1) // 19 + 1; q = n - 19 * (r - 1)
        k = (19 - q + 1) + sum(1 for t in (13, 9, 5) if t >= q) - 1
        return O_EF + pre(WF, WE, r) + WF[r - 1] + k, 'closed'
    if sf == 'H':
        hit = next(((r_, k) for (nn, r_), k in EHLOT.items() if nn == str(n) and r_ >= 9), None)
        if hit: r, k = hit; return O_EF + pre(WF, WE, r) + WF[r - 1] + k, 'rows'
        return None
    if sf == '':
        hits = [(r_, k0 + top - n) for (r_, k0, top, bot) in EBLOCK if bot <= n <= top]
        if not hits: return None
        r, k = hits[0]                                                     # first block that claims the lot, as the decoder does
        return O_EF + pre(WF, WE, r) + WF[r - 1] + k, 'rows'
    return None

# ---------------------------------------------------------------- pass 4 : margins and G/H
def H_margin_B(lab): return (O_MARGIN_B + BMARGIN.index(lab) + 1, 'list') if lab in BMARGIN else None
def H_margin_D(n, sf):
    if not (542 <= n <= 563): return None
    if sf == '': return O_MARGIN_D + (n - 541) + sum(1 for t in DM_TW if t < n), 'closed'
    if sf == 'H' and n in DM_TW: return O_MARGIN_D + (n - 541) + sum(1 for t in DM_TW if t < n) + 1, 'closed'
    return None

def H_G(pf, n, sf):
    pg = lambda r: sum(WG[j] + WH[j] for j in range(r - 1))
    if sf == '' and n in (58, 59, 60): r = n - 57; k = 1
    elif sf in ('', 'H') and 1 <= n <= 57:
        r = (n - 1) // 19 + 1; top = 19 * r; j = top - n
        if sf == 'H':
            if n == top: k = 2
            elif n == top - 11: k = 14
            else: return None
        else: k = j + 3 if j <= 10 else j + 4
    elif sf == '' and 61 <= n <= 75: r, k = 4, n - 60
    else: return None
    return O_GH + pg(r) + k, 'rows'

def H_H(pf, n, sf):
    if sf != '' or not (1 <= n <= 92): return None
    r = (n - 1) // 23 + 1; k = 23 * r + 1 - n                              # increment 23, right-to-left
    return O_GH + sum(WG[j] + WH[j] for j in range(r - 1)) + WG[r - 1] + k, 'closed'

# ---------------------------------------------------------------- pass 5/6 : M, K, J, I, L
def H_M(pf, n, sf):
    if sf != '' or pf != '': return None
    if 82 <= n <= 279: return n + 2556, 'closed'
    if str(n) in MFIRST: return O_M + MFIRST.index(str(n)) + 1, 'list'
    return None
def H_K(pf, n, sf): return (O_K + KORDER.index(str(n)) + 1, 'list') if sf == '' and pf == '' and str(n) in KORDER else None
def H_J(pf, n, sf): return (O_J + n, 'closed') if sf == '' and pf == '' and 1 <= n <= 132 else None
def H_I(pf, n, sf): return (O_I + n, 'closed') if sf == '' and pf == '' and 1 <= n <= 64 else None
def H_L(pf, n, sf): return (O_L + n - 68, 'closed') if sf == '' and pf == '' and 69 <= n <= 107 else None

# ---------------------------------------------------------------- the master function
def H(section, label):
    """(H-number, tier) or (None, why)"""
    S = section.upper(); pf, n, sf = parse(label)
    if n is None: return None, 'unreadable label'
    if (S, label) in ERRATA: return ERRATA[(S, label)]()
    res = None
    if S == 'B': res = H_margin_B(label) or H_B_grid(n, sf) if pf == '' else None
    elif S == 'A': res = H_A_grid(n, sf) if pf == '' else None
    elif S == 'D': res = (H_margin_D(n, sf) if pf == '' else None) or H_D(pf, n, sf, label)
    elif S == 'C': res = H_C(pf, n, sf) if pf == '' else None
    elif S == 'F': res = H_F(pf, n, sf)
    elif S == 'E': res = H_E(pf, n, sf, label)
    elif S == 'G': res = H_G(pf, n, sf)
    elif S == 'H': res = H_H(pf, n, sf)
    elif S == 'M': res = H_M(pf, n, sf)
    elif S == 'K': res = H_K(pf, n, sf)
    elif S == 'J': res = H_J(pf, n, sf)
    elif S == 'I': res = H_I(pf, n, sf)
    elif S == 'L': res = H_L(pf, n, sf)
    if not res and (S, label) in ERRATA: return ERRATA[(S, label)]()
    return res if res else (None, 'no such lot')

# Places where the decoder's own table contains a typo or a duplicate; the formula reproduces the decoder's answer and says so.
ERRATA = {('C', '124H'): lambda: (H_C('', 142, 'H')[0], 'errata'),            # row 8 of C lists "124H"; the pattern says 142H
          ('G', '19'): lambda: (O_GH + 2, 'errata'),                          # G row 1 lists 19 twice; the first should be 19H
          ('E', '152dr'): lambda: H_E('', 152, 'A', '152A'), ('E', '169dr'): lambda: H_E('', 169, 'A', '169A')}   # internal bookkeeping keys
