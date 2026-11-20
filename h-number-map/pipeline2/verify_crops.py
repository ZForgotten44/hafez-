"""Print-size crop checks of the overview sheet (run after build_overall.py).
Four crops are rendered at print size (72 dpi = 1 pt per pixel on the 50 x 35 in sheet) into crosswalk/crops/, and tested:
  F/M strip, crypt court (Detail 1 and its reference), B chapel, E/C bottom edge.
Fail conditions:  a section letter outside its box | a leader line through a printed number | a callout box covering a neighbouring number."""
import json, math, os, sys
import pymupdf as fitz
from shapely.geometry import box as sbox, LineString
from common import *
import build_overall as BO
PDF = os.path.join(REPO, 'h-number-map', 'site', 'pdf', 'Cedar_Grove_H-Number_Map_overall.pdf'); OUT = os.path.join(REPO, 'h-number-map', 'crosswalk', 'crops'); os.makedirs(OUT, exist_ok=True)
pg = fitz.open(PDF)[0]; sh = BO.Sheet2(pg, BO.VIEW_NUM, BO.MX + 50, BO.TOP, BO.W - BO.MX - 50, BO.H - BO.BOT)
tags = json.load(open(f'{DATA}/tags.json')); calls = json.load(open(f'{DATA}/callouts.json'))
spans = []
for b in pg.get_text('dict')['blocks']:
    for l in b.get('lines', []):
        for s in l['spans']:
            if 'Mono' in s['font'] and s['text'].strip(): spans.append((s['text'].strip(), fitz.Rect(s['bbox'])))
cq = []
for c in calls:
    q = sh.P(c['bx'], c['by']); cq.append((c['text'], q.x, q.y))
spans = [(t, r) for t, r in spans if not any(t == ct and abs((r.x0 + r.x1) / 2 - cx) < 3 and abs((r.y0 + r.y1) / 2 - cy) < 4 for ct, cx, cy in cq)]
def P(x, y): p = sh.P(x, y); return (p.x, p.y)
log = []; fails = collections = 0
def say(t): log.append(t); print(t)
bad_letter = bad_line = bad_call = 0
for t in tags:                       # 1. letter inside its box (text width measured with the font that draws it)
    w = BO.twb(t['sec'], 46); bw = t['wu'] * sh.s
    if w > bw - 8: bad_letter += 1; say('letter %s wider than its box' % t['sec'])
    if t['seg']:                     # 2. leader through a number
        a = P(*t['seg'][0]); b = P(*t['seg'][1]); ln = LineString([a, b])
        for txt, r in spans:
            if ln.intersects(sbox(r.x0, r.y0, r.x1, r.y1)): bad_line += 1; say('leader of %s crosses number %s' % (t['sec'], txt)); break
for c in calls:                      # 3. callout box covering a number that is not its own
    q = sh.P(c['bx'], c['by']); bw = BO.ADV * len(c['text']) * 8.5 + 8; bh = 12.75; r = fitz.Rect(q.x - bw / 2, q.y - bh / 2, q.x + bw / 2, q.y + bh / 2)
    for txt, s in spans:
        if txt != c['text'] and r.intersects(s) and (r & s).get_area() > .25 * s.get_area() and not (abs(s.x0 + s.x1 - 2 * q.x) < 2): bad_call += 1; say('callout %s covers number %s' % (c['text'], txt)); break
say('letters outside their box: %d | leaders through a digit: %d | callouts covering a neighbouring number: %d' % (bad_letter, bad_line, bad_call))
def crop(name, u, dpi=72):
    a = sh.P(u[0], u[1]); b = sh.P(u[2], u[3]); pg.get_pixmap(dpi=dpi, clip=fitz.Rect(a, b)).save(os.path.join(OUT, name + '.png'))
crop('F_M_strip', (1230, 262, 1350, 350)); crop('crypt_court', (520, 295, 700, 440)); crop('B_chapel', (1360, 490, 1490, 585)); crop('E_C_bottom_edge', (840, 860, 1480, 945), 50)
pg.get_pixmap(dpi=72, clip=fitz.Rect(150, 1090, 1280, 1810)).save(os.path.join(OUT, 'south_west_insets.png'))
open(os.path.join(REPO, 'h-number-map', 'crosswalk', 'crop_checks.txt'), 'w').write('\n'.join(log) + '\n')
sys.exit(1 if bad_letter + bad_line + bad_call else 0)
