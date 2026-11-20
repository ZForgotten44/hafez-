"""One row per identified outline that has no H-number yet (the 47 'outline without an H-number'): physical lot label, section guess, position,
predecessor and successor on the route as far as the drawing shows them (nearest numbered lots, with their H and the distance), the source, and the placement candidates."""
import csv, json, math, os
from common import *
R = json.load(open(f'{DATA}/registry.json')); V = R['verified']; OUT = os.path.join(REPO, 'h-number-map', 'crosswalk', 'outlines_without_h_number.csv')
def near(p, k=3): return sorted(V, key=lambda v: math.dist(v['pt'], p))[:k]
rows = []
for u in R['unnumbered']:
    t = ''.join(u.get('tokens', []))
    if not t or u.get('graves'): continue            # crypts (graves=True) and unlabelled are handled elsewhere
    nb = near(u['pt']); d0 = math.dist(nb[0]['pt'], u['pt'])
    num = int(''.join(c for c in t if c.isdigit()) or 0); b = 395 <= num <= 414 and t.isdigit()
    cand = ''
    if b: cand = '(a) after H000836, before D 1U: H000837-H000856, route +13 units; (b) before B 20H: H000001-H000020, route +275 units; deciding fact: whether the B/A pass ends with these lots (Jon, deck Q15)'
    rows.append(dict(label_on_drawing=t, x=round(u['pt'][0], 1), y=round(u['pt'][1], 1), nearest_numbered_lot_1='%s %s %s (%.0f u)' % (nb[0]['section'], nb[0]['legacy'], nb[0]['htext'], d0),
                     nearest_numbered_lot_2='%s %s %s' % (nb[1]['section'], nb[1]['legacy'], nb[1]['htext']), nearest_numbered_lot_3='%s %s %s' % (nb[2]['section'], nb[2]['legacy'], nb[2]['htext']),
                     source='outline and label on both the old sheet and the 2022 drawing (grey_inventory.csv)', placement_candidates=cand or 'no unique free route number; needs ledger entry (jon_questions/QUESTIONS.md)', proposed_h='none (not assigned)'))
with open(OUT, 'w', newline='') as f:
    w = csv.DictWriter(f, list(rows[0])); w.writeheader(); w.writerows(rows)
print(len(rows), 'outlines written to', OUT)
