"""Two-way check of the overall H-number map (run after build_overall.py).
 forward   every drawn numbered lot (A-M, 3,000+ lots) has its number printed on the overview, inside its outline or at the end of its leader; counts lots with no visible ID
 backward  every number printed on the overview (monospace spans) is the number of the lot at that spot or at the end of that leader; counts IDs that point to the wrong place
 identity  outlines still awaiting identification (from grey_inventory.csv) with their exact location
Graves: J, K and M have burial records; their individual grave IDs are checked by verify_grave_sheets.py. A to I and L have no burial records, so no individual grave is
'confirmed' there: only lot numbers (the grave digit 1-9 is appended to a lot number) are printed and checked."""
import json, os, sys, math, csv, collections
import pymupdf as fitz
from shapely.geometry import Polygon, Point
from common import *
import svgmap
D = svgmap.load(); lots = D['lots']
pdf = fitz.open(os.path.join(REPO, 'h-number-map', 'site', 'pdf', 'Cedar_Grove_H-Number_Map_overall.pdf'))[0]
log = []
def say(t): log.append(t); print(t)
import build_overall as BO
# geometry of the sheet (same as build_overall.build for the numbers map)
sh = BO.Sheet2(pdf, BO.VIEW_NUM, BO.MX + 50, BO.TOP, BO.W - BO.MX - 50, BO.H - BO.BOT)
inv = lambda x, y: (sh.view[0] + (x - sh.ox) / sh.s, sh.view[1] + (y - sh.oy) / sh.s)
AMBER_INT = (int(BO.AMBER[0] * 255 + .5) << 16) | (int(BO.AMBER[1] * 255 + .5) << 8) | int(BO.AMBER[2] * 255 + .5)
insets = BO.inset_rects(sh) if hasattr(BO, 'inset_rects') else ()
HIST_INT = (int(BO.HIST[0] * 255 + .5) << 16) | (int(BO.HIST[1] * 255 + .5) << 8) | int(BO.HIST[2] * 255 + .5)
spans = []
for b in pdf.get_text('dict')['blocks']:
    for l in b.get('lines', []):
        for s in l['spans']:
            if 'Mono' in s['font'] and s['color'] not in (AMBER_INT, HIST_INT) and s['text'].strip() and not any(r.intersects(fitz.Rect(s['bbox'])) for r in insets) and sh.clip.contains(fitz.Point((s['bbox'][0] + s['bbox'][2]) / 2, (s['bbox'][1] + s['bbox'][3]) / 2)):
                x0, y0, x1, y1 = s['bbox']; ux, uy = inv((x0 + x1) / 2, (y0 + y1) / 2); spans.append((s['text'].strip(), ux, uy, s['size']))
say('spans in the number font on the map: %d' % len(spans))
callouts = json.load(open(os.path.join(DATA, 'callouts.json'))) if os.path.exists(os.path.join(DATA, 'callouts.json')) else []
# lots with a number anywhere: each lot expects a span with its text at its centre, or a callout record pointing at it
spans_by_text = collections.defaultdict(list)
for t, x, y, sz in spans: spans_by_text[t].append((x, y, sz))
call_by_h = {c['h']: c for c in callouts}
miss = []; wrong = 0; used = set(); small = 0
for o in lots:
    if o.get('twin'): continue
    t = o['d']; c = call_by_h.get(o['h']) if (not o['poly'] or not o['fs'] or o['fs'] * sh.s < BO.CALLOUT_PT) else None
    if c:
        cand = [(x, y, sz) for x, y, sz in spans_by_text[t] if math.hypot(x - c['bx'], y - c['by']) < 3]
        ok = bool(cand) and abs(c['tx'] - o['cx']) < 1e-6 and abs(c['ty'] - o['cy']) < 1e-6
        for x, y, sz in cand: used.add((t, round(x, 2), round(y, 2)))
    else:
        cand = [(x, y, sz) for x, y, sz in spans_by_text[t] if math.hypot(x - o['cx'], y - o['cy']) < 2.0]
        ok = bool(cand)
        for x, y, sz in cand: used.add((t, round(x, 2), round(y, 2)))
        if ok and cand[0][2] < 6.0: small += 1
    if not ok: miss.append((o['s'], o['l'], o['h']))
say('forward: %d numbered lots checked; confirmed lots with no visible ID: %d %s' % (len([o for o in lots if not o.get('twin')]), len(miss), miss[:12]))
# backward
unmatched = [(t, round(x), round(y)) for t, x, y, sz in spans if (t, round(x, 2), round(y, 2)) not in used]
# every callout's leader end must be inside (or within 1 unit of) the lot it names
polys = {o['h']: Polygon(o['poly']).buffer(0) for o in lots if o['poly'] and len(o['poly']) > 2 and not o.get('twin')}
for c in callouts:
    p = polys.get(c['h'])
    if p is not None and p.distance(Point(c['tx'], c['ty'])) > 1.0: wrong += 1; say('leader of %s ends %.1f units from its lot' % (c['h'], p.distance(Point(c['tx'], c['ty']))))
say('backward: %d printed numbers; numbers not tied to a lot: %d %s; leaders ending at the wrong place: %d' % (len(spans), len(unmatched), unmatched[:12], wrong))
ip = os.path.join(REPO, 'h-number-map', 'grey_inventory.csv'); aw = []
if os.path.exists(ip):
    aw = [r for r in csv.DictReader(open(ip)) if r['final_status'].startswith('awaiting')]
say('identity: outlines still awaiting identification: %d' % len(aw))
for r in aw[:200]: say('   cell %s grid %s (%s, %s) label "%s": %s' % (r['cell'], r.get('grid_square', r.get('grid', '')), r['x'], r['y'], r['label'], r['final_status'] + ': ' + r['evidence_needed_or_consequence'][:110]))
open(os.path.join(REPO, 'h-number-map', 'crosswalk', 'map_verification.txt'), 'w').write('\n'.join(log) + '\n')
print('TOTALS: confirmed lots with no visible ID = %d | visible IDs pointing to the wrong place = %d | outlines awaiting identification = %d' % (len(miss), len(unmatched) + wrong, len(aw)))
