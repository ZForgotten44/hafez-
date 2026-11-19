"""Step 5d: the two native numbering systems that are not part of the H-numbering.

  Mausoleum crypts 1-68   the small slanted cells in the two courts between the mausoleums (1-25 south court, 26-50 north court) and the
                          row of small boxes north of the north court (51-68)
  Cremains niches 1-80    the strip north of Section F/D lots: 71 narrow cells in a regular strip (niches 10-80) and 9 tiny tilted cells at its east
                          end (niches 1-9); the drawing writes every fifth number

Writes data/special_areas.json: items (id, name, centre, polygon, how established, confidence), the overview ranges and their boxes, and notes
that say what could not be established.  Positions are drawing units, the same frame as every other file."""
import json, math, collections
from shapely.geometry import Polygon, LineString
from shapely.ops import unary_union, polygonize
from common import *

LOT = [0.3, 0.52, 0.6]; NICHE = [0.8, 0.6, 0.4]
COURTS = {'south': (578, 380, 612, 415), 'north': (580, 340, 612, 373), 'row': (560, 308, 622, 332)}

def inbox(p, b): return b[0] <= p[0] <= b[2] and b[1] <= p[1] <= b[3]
def ctr(poly): c = Polygon(poly).centroid; return [round(c.x, 2), round(c.y, 2)]

def nom(rowcells, pt):
    if not rowcells: return None
    rc = rowcells[0].centroid
    return [[round(px - rc.x + pt[0], 2), round(py - rc.y + pt[1], 2)] for px, py in list(rowcells[0].exterior.coords)[:-1]]

def crypts(I, C, D):
    cells = {c['id']: c for c in C}; lab = {}                                   # number -> dict(pt, cell)
    for g in I['groups']:
        t = ''.join(g['tokens'])
        if not t.isdigit(): continue
        n = int(t); pt = g['pt']
        for court, b in COURTS.items():
            if inbox(pt, b) and g['spans'][0]['size'] < 3.2:
                lo, hi = {'south': (1, 25), 'north': (26, 50), 'row': (51, 68)}[court]
                if lo <= n <= hi and n not in lab: lab[n] = dict(pt=pt, cell=g['cell'], court=court)
    used = {v['cell'] for v in lab.values() if v['cell'] is not None}
    free = [c for c in C if c['id'] not in used and inbox(Polygon(c['poly']).centroid.coords[0], COURTS['north'])]     # drawn cells without a label
    # cells of the 51-68 row are too small for the cell tracer: polygonise the lot-colour strokes there
    segs = []
    for d in D['draws']:
        if d['color'] != LOT: continue
        for it in d['items']:
            if it[0] == 'l': pts = [(it[1], it[2]), (it[3], it[4])]
            elif it[0] == 'qu': q = it[1:]; pts = [(q[0], q[1]), (q[2], q[3]), (q[4], q[5]), (q[6], q[7]), (q[0], q[1])]
            elif it[0] == 're': a, b, c, e = it[1:]; pts = [(a, b), (c, b), (c, e), (a, e), (a, b)]
            else: continue
            xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
            if min(xs) > 555 and max(xs) < 630 and min(ys) > 298 and max(ys) < 326: segs.append(LineString(pts))
    rowcells = [p for p in polygonize(unary_union(segs)) if p.area > 3]
    items = []; notes = []
    COURTNAME = {'south': ('south court', 'between Mausoleum 3 and Mausoleum 1'), 'north': ('north court', 'between Mausoleum 4 and Mausoleum 2'),
                 'row': ('row north of the north court', 'mausoleum not established')}
    missing_north = [n for n in range(26, 51) if n not in lab]
    # unlabelled drawn cells of the north court take the missing numbers in order along the row (26..33 run towards the north-east)
    if len(missing_north) == len(free) and free:
        ref = sorted((n, lab[n]['pt']) for n in lab if 26 <= n <= 33)
        d0 = (ref[-1][1][0] - ref[0][1][0], ref[-1][1][1] - ref[0][1][1]); nn = math.hypot(*d0); d0 = (d0[0] / nn, d0[1] / nn)
        free.sort(key=lambda c: Polygon(c['poly']).centroid.x * d0[0] + Polygon(c['poly']).centroid.y * d0[1])
        for n, c in zip(sorted(missing_north), free): lab[n] = dict(pt=ctr(c['poly']), cell=c['id'], court='north', inferred=True)
    else: notes.append('north court: %d numbers lack a label but %d unlabelled cells were found; they were not assigned' % (len(missing_north), len(free)))
    for n in range(1, 69):
        v = lab.get(n); court = v['court'] if v else ('south' if n <= 25 else 'north' if n <= 50 else 'row')
        cn, near = COURTNAME[court]
        if v is None:                       # 59, 60, 65, 66: no label and no cell found; interpolate between the labelled neighbours of the row
            lo = max(k for k in lab if k < n); hi = min(k for k in lab if k > n); a, b = lab[lo]['pt'], lab[hi]['pt']; t = (n - lo) / (hi - lo)
            pt = [round(a[0] + (b[0] - a[0]) * t, 2), round(a[1] + (b[1] - a[1]) * t, 2)]
            items.append(dict(id='CRYPT-%03d' % n, name='Mausoleum crypt %d' % n, kind='crypt', n=n, x=pt[0], y=pt[1], poly=None, court='%s (%s)' % (cn, near),
                              how='numbered by position between labelled neighbours %d and %d; no label and no cell traced' % (lo, hi), confidence='low (position to about 3 units)', nominal_poly=nom(rowcells, pt)))
            continue
        poly = None
        if v['cell'] is not None: poly = [[round(x, 2), round(y, 2)] for x, y in cells[v['cell']]['poly']]
        else:
            m = min(rowcells, key=lambda p: p.centroid.distance(__import__('shapely.geometry', fromlist=['Point']).Point(v['pt'])), default=None)
            if m is not None and m.centroid.distance(__import__('shapely.geometry', fromlist=['Point']).Point(v['pt'])) < 2.5: poly = [[round(x, 2), round(y, 2)] for x, y in list(m.exterior.coords)[:-1]]
        x, y = (ctr(poly) if poly else [round(v['pt'][0], 2), round(v['pt'][1], 2)])
        inf = v.get('inferred'); nominal = None
        if poly is None and court == 'row' and rowcells:     # cell outline not traced: a nominal box of the same size and tilt as the traced cells of the row, centred on the label
            ref = rowcells[0]; rc = ref.centroid; nominal = [[round(px - rc.x + x, 2), round(py - rc.y + y, 2)] for px, py in list(ref.exterior.coords)[:-1]]
        items.append(dict(id='CRYPT-%03d' % n, nominal_poly=nominal, name='Mausoleum crypt %d' % n, kind='crypt', n=n, x=x, y=y, poly=poly, court='%s (%s)' % (cn, near),
                          how='numbered by position between labelled neighbours (cell drawn, label missing)' if inf else 'labelled on drawing',
                          confidence='medium' if inf else ('high' if poly or court != 'row' else 'medium (label only, no cell traced)')))
    return items, notes

def niches(I, D):
    rungs = []
    for d in D['draws']:
        if d['color'] != NICHE: continue
        for it in d['items']:
            if it[0] != 'l': continue
            x0, y0, x1, y1 = it[1:5]
            if min(x0, x1) < 815 or max(x0, x1) > 975 or min(y0, y1) < 350 or max(y0, y1) > 372: continue
            if abs(x1 - x0) < 0.4 and abs(y1 - y0) > 2: rungs.append(((x0 + x1) / 2, min(y0, y1), max(y0, y1)))
    rungs.sort(); notes = []
    cells = []                                           # (x0, x1, ymin, ymax) from the east: niche 10 = last pair
    for a, b in zip(rungs, rungs[1:]): cells.append((a, b))
    cells.reverse()                                      # cells[0] = easternmost strip cell
    items = []
    # labels: the drawing writes 1, 5, 10, 15 ... 80
    lab = {}
    for g in I['groups']:
        t = ''.join(g['tokens'])
        if t.isdigit() and g['cell'] is None and 820 <= g['pt'][0] <= 990 and 352 <= g['pt'][1] <= 363 and int(t) in {1, 5} | set(range(10, 81, 5)): lab[int(t)] = g['pt']
    # the east block: nine columns (niches 1-9, east to west) between x 973.3 and 988.8, tilted; each column shows two small openings one above the other in the drawing,
    # one number per column (the labels 1 and 5 sit over columns 1 and 5).  Outline fitted to the block edges read off a 1300 dpi render of the drawing.
    xe, xw = 988.8, 973.3; top = lambda x: 364.1 - 0.142 * (x - 973.3); bot = lambda x: 367.6 - 0.158 * (x - 973.6); wcol = (xe - xw) / 9
    for k in range(9):
        n = k + 1; xr = xe - k * wcol; xl = xr - wcol
        poly = [[round(xl, 2), round(top(xl), 2)], [round(xr, 2), round(top(xr), 2)], [round(xr, 2), round(bot(xr), 2)], [round(xl, 2), round(bot(xl), 2)]]; c = ctr(poly)
        items.append(dict(id='NICHE-%03d' % n, name='Cremains niche %d' % n, kind='niche', n=n, x=c[0], y=c[1], poly=poly, court='east end of the cremains strip (tilted block)',
                          how='labelled on drawing' if n in lab else 'numbered by position between labelled neighbours',
                          confidence='medium (outline fitted to the block; two openings per column in the drawing, one number per column)'))
    for k, (a, b) in enumerate(cells):
        n = 10 + k
        ymin = min(a[1], b[1]); ymax = max(a[2], b[2])
        poly = [[round(a[0], 2), round(a[1], 2)], [round(b[0], 2), round(b[1], 2)], [round(b[0], 2), round(b[2], 2)], [round(a[0], 2), round(a[2], 2)]]
        poly = [[poly[0][0], poly[0][1]], [poly[1][0], poly[1][1]], [poly[2][0], poly[2][1]], [poly[3][0], poly[3][1]]]
        c = ctr(poly)
        items.append(dict(id='NICHE-%03d' % n, name='Cremains niche %d' % n, kind='niche', n=n, x=c[0], y=c[1], poly=poly, court='cremains strip', how='labelled on drawing' if n in lab else 'numbered by position between labelled neighbours',
                          confidence='high'))
    items.sort(key=lambda i: i['n'])
    err = {n: round(lab[n][0] - next(i for i in items if i['n'] == n)['x'], 2) for n in lab}
    notes.append('cremains: %d strip cells between %d rungs (niches 10 to %d) + 9 tilted end columns (niches 1 to 9) = %d; the end block shows two openings per column, so whether each column is one niche or two is not established from the drawing; labelled niches fall on their own cell (x offsets label minus cell centre: max %.2f units, median %.2f)' % (
        len(cells), len(rungs), 9 + len(cells), len(items), max(abs(v) for v in err.values()), sorted(abs(v) for v in err.values())[len(err) // 2]))
    if len(items) != 80: notes.append('cremains: the strip has %d cells, not 80; numbers are not forced to 80' % len(items))
    return items, notes, err

def build():
    I = json.load(open(f'{DATA}/identified.json')); C = json.load(open(f'{DATA}/cells.json')); D = json.load(open(f'{DATA}/ai_raw.json'))
    cr, n1 = crypts(I, C, D); ni, n2, err = niches(I, D)
    def bbox(its): xs = [p[0] for i in its for p in (i['poly'] or [[i['x'], i['y']]])]; ys = [p[1] for i in its for p in (i['poly'] or [[i['x'], i['y']]])]; return [round(min(xs) - 2, 1), round(min(ys) - 2, 1), round(max(xs) + 2, 1), round(max(ys) + 2, 1)]
    out = dict(items=cr + ni, ranges=[dict(text='Mausoleum crypts 1 to 68', bbox=bbox(cr), kind='crypt'), dict(text='Cremains niches 1 to 80', bbox=bbox(ni), kind='niche')],
               courts={k: v for k, v in COURTS.items()}, notes=n1 + n2 + ['crypts: mausoleum membership is not established beyond "court between Mausoleum 3 and 1" (1-25), "court between Mausoleum 4 and 2" (26-50) and "row north of the north court" (51-68)'],
               niche_label_offsets=err)
    json.dump(out, open(f'{DATA}/special_areas.json', 'w'))
    c = collections.Counter((i['kind'], i['confidence'].split(' ')[0]) for i in out['items'])
    print('crypts', len(cr), 'niches', len(ni), dict(c)); [print(' ', n) for n in out['notes']]
    return out
if __name__ == '__main__': build()
