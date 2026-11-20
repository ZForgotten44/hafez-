"""Step 9b: the two overall maps, each one poster sheet (50 x 35 in, vector).

  H-number map  every lot with its H-number, tinted by walking pass, old section letters, grid, landmarks, the full index of sections
  Tree map      the same sheet and grid, the trees on a quiet lot base, the tree key first, a short index

    python3 build_overall.py                 -> site/pdf/Cedar_Grove_H-Number_Map_overall.pdf
    python3 build_overall.py --trees         -> site/pdf/Cedar_Grove_Tree_Map_overall.pdf   (trees from math/three/data3d.json: [[x, y, radius, evergreen], ...])
    python3 build_overall.py --trees FILE    -> the same, from another tree list in the same shape

The drawing is clipped to the map frame; the title, grid letters and footer sit in their own clear space."""
import json, math, os, sys, collections
import pymupdf as fitz
import numpy as np
from shapely.geometry import Polygon, Point, box as sbox
from shapely.ops import nearest_points, unary_union
from shapely.strtree import STRtree
from common import *
import svgmap, build_pdf as B
from fit import ADV, INK_MID

W, H = 3600, 2520
VIEW_NUM = [335, 215, 1735, 940]                  # lots, road names, the mausoleum corner and the east avenue
VIEW_TREE = [215, 55, 1810, 1045]                 # the whole aerial: the woods west of the cemetery too
MX, TOP, BOT = 60, 235, 660
NAVY, GREY, PALE = B.NAVY, (.34, .38, .45), (.93, .92, .88)
PASSES = [(1, 836, 'Pass 1', 'B, A', '#cfe0f5'), (837, 1885, 'Pass 2', 'D, C', '#d5ecd9'), (1886, 2345, 'Pass 3', 'F, E', '#f6e7b9'),
          (2346, 2600, 'Pass 4', 'margins, G, H', '#f6d3cf'), (2601, 2855, 'Pass 5', 'M', '#dcd3ee'), (2856, 3218, 'Pass 6', 'L strip, K, J, I, L', '#cfe6e4')]
# number, name, note, x, y (drawing units, read off the drawing and the old section maps)
LANDMARKS = [
    (1, 'Office', 'the cottage', 1378, 358), (2, 'Maintenance building', 'the garage', 1288, 385), (3, 'Chapel', 'in Section B', 1415, 538),
    (4, 'Saint Joseph', 'hexagon marker', 1331, 314), (5, 'Parking', 'north of the office', 1288, 336),
    (6, 'Mausoleum 1', 'Mary Queen of Angels', 635, 399), (7, 'Mausoleum 2', 'Mary Queen of All Saints', 635, 355), (8, 'Mausoleum 3', 'Mary Mother of the Church', 562, 412),
    (9, 'Mausoleum 4', 'Mary Mother of God', 562, 342), (10, 'Mausoleum crypts', 'numbered 1 to 68, no H-number', 595, 380),
    (11, 'Cremains area', 'niches 1 to 80, no H-number', 905, 361), (12, 'Spoils yard', '', 386, 534)]
ROADS = (('NOTRE DAME AVENUE', 1707, 605, -90, 30), ('HOLY CROSS DRIVE', 1080, 246, -3.5, 26))

class Sheet2:
    def __init__(self, page, view, x0, y0, x1, y1):
        self.page = page; self.view = view; aw, ah = x1 - x0, y1 - y0
        self.s = min(aw / (view[2] - view[0]), ah / (view[3] - view[1]))
        self.ox = x0 + (aw - self.s * (view[2] - view[0])) / 2; self.oy = y0 + (ah - self.s * (view[3] - view[1])) / 2
        self.clip = fitz.Rect(self.ox, self.oy, self.ox + self.s * (view[2] - view[0]), self.oy + self.s * (view[3] - view[1]))
    def P(self, x, y): return fitz.Point(self.ox + (x - self.view[0]) * self.s, self.oy + (y - self.view[1]) * self.s)

def rgb(h): return B.hex2rgb(h)
def passof(h): return next(p for p in PASSES if p[0] <= h <= p[1])
def text(pg, x, y, t, fs, bold=False, color=NAVY):
    pg.insert_text((x, y), t, fontsize=fs, fontname='uib' if bold else 'ui', fontfile=B.UIB if bold else B.UI, color=color)
_FB = fitz.Font(fontfile=B.UIB)
def twb(t, fs): return _FB.text_length(t, fontsize=fs)
def tw(t, fs, bold=False): return fitz.get_text_length(t, fontname='helv', fontsize=fs) * (1.06 if bold else 1.0)

def ranges(D):
    """per section: lots drawn, the whole H range of its body (numbers the drawing has no lot for count, they belong to the section),
    the margin strip of B, D and F (pass 4), the numbers with no lot, bbox"""
    st = B.section_stats(D); out = {}
    miss = collections.defaultdict(list)
    for u in D['reg']['known_unplaced']:
        if not u['legacy'].endswith('dr'): miss[u['section']].append(u['hnum'])
    for sec, e in st.items():
        hs = [o['hn'] for o in D['lots'] if o['s'] == sec]; ms = miss.get(sec, [])
        marg = lambda h: sec in 'BDF' and 2332 <= h <= 2412
        body = [h for h in hs + ms if not marg(h)]; mg = [h for h in hs + ms if marg(h)]
        out[sec] = dict(n=e['n'], b=e['b'], lo=min(body), hi=max(body), mlo=min(mg) if mg else None, mhi=max(mg) if mg else None, missing=sorted(ms))
    return out

# ------------------------------------------------------------------ the map itself
def marker(pg, p, n, r):
    shp = pg.new_shape(); shp.draw_circle(p, r + r * .22); shp.finish(color=None, fill=(1, 1, 1), fill_opacity=.9); shp.commit()
    shp = pg.new_shape(); shp.draw_circle(p, r); shp.finish(color=NAVY, fill=(1, 1, 1), width=r * .16); shp.commit()
    s = str(n); f = r * (1.15 if n < 10 else .95)
    pg.insert_text((p.x - tw(s, f, True) / 2, p.y + f * .36), s, fontsize=f, fontname='uib', fontfile=B.UIB, color=NAVY)

GX0, GY0, GC = 200, 0, 100          # the grid is anchored on the drawing, so a square has the same name on both maps: columns from x = 200, rows from y = 0, 100 units each

def grid_lines(sh):
    pg = sh.page; v = sh.view
    c0, c1 = int((v[0] - GX0) // GC), int((v[2] - GX0) // GC); r0, r1 = int((v[1] - GY0) // GC), int((v[3] - GY0) // GC)
    shp = pg.new_shape()
    for i in range(c0 + 1, c1 + 1): shp.draw_line(sh.P(GX0 + i * GC, v[1]), sh.P(GX0 + i * GC, v[3]))
    for j in range(r0 + 1, r1 + 1): shp.draw_line(sh.P(v[0], GY0 + j * GC), sh.P(v[2], GY0 + j * GC))
    shp.finish(color=(.6, .62, .66), width=.8, dashes='[10 8] 0'); shp.commit()

def grid_letters(sh):
    """grid letters and numbers sit in their own bands outside the frame; the bands are opaque so nothing of the drawing can run into them"""
    pg = sh.page; v = sh.view; bw = 62; c = sh.clip
    for r in (fitz.Rect(c.x0 - bw, c.y0 - bw, c.x1 + bw, c.y0), fitz.Rect(c.x0 - bw, c.y1, c.x1 + bw, c.y1 + bw), fitz.Rect(c.x0 - bw, c.y0, c.x0, c.y1), fitz.Rect(c.x1, c.y0, c.x1 + bw, c.y1)):
        shp = pg.new_shape(); shp.draw_rect(r); shp.finish(color=None, fill=(.955, .95, .93)); shp.commit()
    shp = pg.new_shape(); shp.draw_rect(fitz.Rect(c.x0 - bw, c.y0 - bw, c.x1 + bw, c.y1 + bw)); shp.finish(color=(.6, .62, .66), width=1.2, fill=None); shp.commit()
    c0, c1 = int((v[0] - GX0) // GC), int((v[2] - GX0) // GC); r0, r1 = int((v[1] - GY0) // GC), int((v[3] - GY0) // GC)
    for i in range(c0, c1 + 1):
        x0, x1 = max(v[0], GX0 + i * GC), min(v[2], GX0 + (i + 1) * GC)
        if x1 - x0 < 25: continue
        t = chr(65 + i); cc = sh.P((x0 + x1) / 2, v[1])
        text(pg, cc.x - twb(t, 34) / 2, c.y0 - 20, t, 34, True, GREY); text(pg, cc.x - twb(t, 34) / 2, c.y1 + 44, t, 34, True, GREY)
    for j in range(r0, r1 + 1):
        y0, y1 = max(v[1], GY0 + j * GC), min(v[3], GY0 + (j + 1) * GC)
        if y1 - y0 < 25: continue
        t = str(j + 1); cc = sh.P(v[0], (y0 + y1) / 2)
        text(pg, c.x0 - 18 - twb(t, 34), cc.y + 12, t, 34, True, GREY); text(pg, c.x1 + 18, cc.y + 12, t, 34, True, GREY)

def cellref(b):
    c0 = int((b[0] - GX0) // GC); c1 = int((b[2] - GX0) // GC); r0 = int((b[1] - GY0) // GC); r1 = int((b[3] - GY0) // GC)
    return '%s%d to %s%d' % (chr(65 + c0), r0 + 1, chr(65 + c1), r1 + 1)

def road_names(sh, strong):
    pg = sh.page
    for t, x, y, ang, fs in ROADS:
        p = sh.P(x, y)
        pg.insert_text(p, t, fontsize=fs, fontname='uib', fontfile=B.UIB, color=(.3, .33, .38) if strong else (.45, .48, .52), morph=(p, fitz.Matrix(ang)) if ang else None)

INV = {}            # cell id -> inventory row (grey_inventory.csv, refreshed by refresh_inventory.py)
AMBER = (.78, .5, .1); AMBER_FILL = (.99, .93, .8); HIST = (.1, .12, .2)   # amber only for outlines; old lot labels are dark

def load_inventory():
    p = os.path.join(REPO, 'h-number-map', 'grey_inventory.csv'); INV.clear()
    if os.path.exists(p):
        import csv
        for r in csv.DictReader(open(p)): INV[int(r['cell'])] = r

def draw_unnumbered(sh, D, cells, trees_mode):
    """every drawn outline without an H-number, by what it is: crypts (own numbering), not graves, lots still awaiting a number or an identification"""
    pg = sh.page; groups = collections.defaultdict(list)
    for u in D['reg'].get('unnumbered', []):
        if u['cell'] is None: continue
        r = INV.get(u['cell']); st = r['final_status'] if r else 'awaiting identification'
        groups[st].append((u, r))
    style = {'native numbering (crypt)': ((.1, .28, .5), (.87, .91, .96), None), 'not a grave': ((.6, .6, .62), (.93, .93, .91), None),
             'awaiting a number (lot identified)': (AMBER, AMBER_FILL, '[4 3] 0'), 'awaiting identification': (AMBER, (.99, .88, .7), '[4 3] 0')}
    for st, mem in groups.items():
        col, fill, dash = style.get(st, style['awaiting identification']); shp = pg.new_shape()
        for u, r in mem: shp.draw_polyline([sh.P(x, y) for x, y in cells[u['cell']]['poly']] + [sh.P(*cells[u['cell']]['poly'][0])])
        shp.finish(color=col, fill=fill, width=.9 if dash else .5, dashes=dash, closePath=True, lineJoin=1); shp.commit()
    if trees_mode: return
    for st in ('awaiting a number (lot identified)', 'awaiting identification'):         # the old label, in amber: it is NOT an H-number
        for u, r in groups.get(st, []):
            t = ''.join(u['tokens'])
            if not t: continue
            poly = Polygon(cells[u['cell']]['poly']); c = poly.representative_point(); x0, y0, x1, y1 = poly.bounds
            fs = min(3.4, .85 * (x1 - x0) / (ADV * len(t)), .75 * (y1 - y0))
            if fs * sh.s < 5.0: fs = 5.0 / sh.s
            p = sh.P(c.x, c.y); f = fs * sh.s; w = ADV * len(t) * f
            pg.insert_text(fitz.Point(p.x - w / 2, p.y + f * .36), t, fontsize=f, fontname='dvsm', fontfile=B.FONT.replace('-Bold', ''), color=HIST)

CALLOUT_PT = 6.0        # a number that would print smaller than this inside its lot gets a leader and a larger number in free space

CALLOUTS = []

def _callout_box(pg, sh, q, t, fs, halo=True):
    bw = ADV * len(t) * fs + 8; bh = fs * 1.5
    if halo:   # opaque white halo: whatever line runs behind the number (the blue dashed boundary, a road) is broken there
        h = pg.new_shape(); h.draw_rect(fitz.Rect(q.x - bw / 2 - 4, q.y - bh / 2 - 4, q.x + bw / 2 + 4, q.y + bh / 2 + 4)); h.finish(color=None, fill=(1, 1, 1)); h.commit()
    s2 = pg.new_shape(); s2.draw_rect(fitz.Rect(q.x - bw / 2, q.y - bh / 2, q.x + bw / 2, q.y + bh / 2), radius=.15); s2.finish(color=NAVY, fill=(1, 1, 1), width=1.0); s2.commit()
    pg.insert_text(fitz.Point(q.x - ADV * len(t) * fs / 2, q.y + fs * .36), t, fontsize=fs, fontname='dvsmb', fontfile=B.FONT, color=NAVY)

def draw_callouts(sh, small, lots, cells):
    """lots too small (or with no traced outline): the number is printed larger outside the lot, joined by a leader that ends inside its own outline.
    Section M numbers stand in one straight row per run of lots, in plot order (west to east), with the blue boundary broken behind each label."""
    pg = sh.page; polys = [Polygon(o['poly']).buffer(0) for o in lots if o['poly'] and len(o['poly']) > 2]; tree = STRtree(polys); placed = []; fs = 8.5
    def boxu(px, py, t): return sbox(px - (ADV * len(t) * fs + 14) / 2 / sh.s, py - (fs * 1.5 + 8) / 2 / sh.s, px + (ADV * len(t) * fs + 14) / 2 / sh.s, py + (fs * 1.5 + 8) / 2 / sh.s)
    def onlab(r): return len(ltree.query(r, predicate='intersects')) if ltree is not None else 0
    def free(r): return onlab(r) == 0 and sum(polys[i].intersection(r).area for i in tree.query(r, predicate='intersects')) / r.area < .02 and not any(r.intersects(q) for q in placed)
    small_ids = {id(o) for o in small}; lab = [sbox(o['cx'] - max(ADV * len(o['d']) * o['fs'], o['fs']) * .6, o['cy'] - max(ADV * len(o['d']) * o['fs'], o['fs']) * .6, o['cx'] + max(ADV * len(o['d']) * o['fs'], o['fs']) * .6, o['cy'] + max(ADV * len(o['d']) * o['fs'], o['fs']) * .6) for o in lots if o.get('fs') and id(o) not in small_ids]; ltree = STRtree(lab) if lab else None
    msm = sorted([o for o in small if o['s'] == 'M' and o['poly']], key=lambda o: o['cx']); rest = [o for o in small if o not in msm]
    runs = []
    for o in msm:
        if runs and o['cx'] - runs[-1][-1]['cx'] < 70: runs[-1].append(o)
        else: runs.append([o])
    for run in runs:
        wmax = max((ADV * len(o['d']) * fs + 14) / sh.s for o in run); xs = [o['cx'] for o in run]
        for side in (1, -1, 1):     # south of the lots first, then north
            ok = False
            for dy in range(10, 90, 2):
                yr = (max(o['cy'] for o in run) + dy) if side == 1 else (min(o['cy'] for o in run) - dy)
                px = []
                for x in xs: px.append(max(x, (px[-1] + wmax) if px else x))
                sh_ = (sum(px) - sum(xs)) / len(xs); px = [p - sh_ for p in px]
                for i in range(1, len(px)): px[i] = max(px[i], px[i - 1] + wmax)
                rs = [boxu(p, yr, o['d']) for p, o in zip(px, run)]
                if all(free(r) and r.bounds[0] > sh.view[0] + 3 and r.bounds[2] < sh.view[2] - 3 for r in rs): ok = True; break
            if ok: break
        if not ok: rest += run; continue
        for p, o, r in zip(px, run, rs):
            t = o['d']; placed.append(r.buffer(1.5)); CALLOUTS.append(dict(h=o['h'], text=t, tx=o['cx'], ty=o['cy'], bx=p, by=yr))
            a = sh.P(o['cx'], o['cy']); q = sh.P(p, yr); l = pg.new_shape(); l.draw_line(a, q); l.finish(color=NAVY, width=1.1); l.commit()
            d = pg.new_shape(); d.draw_circle(a, 2.6); d.finish(color=NAVY, fill=NAVY); d.commit(); _callout_box(pg, sh, q, t, fs)
    for o in sorted(rest, key=lambda o: (o['cx'], o['cy'])):
        t = o['d']; wu = (ADV * len(t) * fs + 8) / sh.s; hu = (fs * 1.5) / sh.s; cx, cy = o['cx'], o['cy']
        if not o['poly']:
            b = pg.new_shape(); a = sh.P(cx - 4.5, cy - 6.5); c = sh.P(cx + 4.5, cy + 6.5); b.draw_rect(fitz.Rect(a, c)); b.finish(color=NAVY, width=1.0, dashes='[4 3] 0', fill=None); b.commit()
        best = None
        for dist in (13, 18, 24, 32, 42, 56, 72):
            for k in range(24):
                ang = k * math.pi / 12; px = cx + dist * math.cos(ang); py = cy + dist * math.sin(ang)
                r = sbox(px - wu / 2, py - hu / 2, px + wu / 2, py + hu / 2)
                if r.bounds[0] < sh.view[0] + 3 or r.bounds[2] > sh.view[2] - 3 or r.bounds[1] < sh.view[1] + 3 or r.bounds[3] > sh.view[3] - 3: continue
                cov = sum(polys[i].intersection(r).area for i in tree.query(r, predicate='intersects')) / r.area
                over = sum(r.intersects(q) for q in placed)
                c0 = cov * 300 + over * 200 + dist * .6 + onlab(r) * 600
                if best is None or c0 < best[0]: best = (c0, px, py, r)
        if best is None: continue
        c0, px, py, r = best; placed.append(r.buffer(1.5)); CALLOUTS.append(dict(h=o['h'], text=t, tx=cx, ty=cy, bx=px, by=py))
        a = sh.P(cx, cy); q = sh.P(px, py); l = pg.new_shape(); l.draw_line(a, q); l.finish(color=NAVY, width=1.1); l.commit()
        d = pg.new_shape(); d.draw_circle(a, 2.6); d.finish(color=NAVY, fill=NAVY); d.commit(); _callout_box(pg, sh, q, t, fs)

def draw_twins(sh, lots):
    """one lot drawn as two outlines: a dashed bracket joins them (the number is written once)"""
    pg = sh.page; by = collections.defaultdict(list)
    for o in lots:
        if o.get('twin') or any(p.get('twin') for p in [o]): by[o['h']].append(o)
    for h, mem in by.items(): pass
    tw_ = [o for o in lots if o.get('twin')]
    for o in tw_:
        mate = next((p for p in lots if p['h'] == o['h'] and not p.get('twin')), None)
        if not mate: continue
        l = pg.new_shape(); l.draw_line(sh.P(o['cx'], o['cy']), sh.P(mate['cx'], mate['cy'])); l.finish(color=NAVY, width=1.6, dashes='[3 2] 0'); l.commit()

def draw_trees(sh, trees):
    """crowns at their measured size, lightly filled so the ground shows through; every recorded tree centre is a dot, evergreens a dark triangle"""
    pg = sh.page; crowns = pg.new_shape(); dots = pg.new_shape(); tri = pg.new_shape(); v = sh.view
    for x, y, r, kind in trees:
        if not (v[0] <= x <= v[2] and v[1] <= y <= v[3]): continue
        c = sh.P(x, y)
        if kind in ('e', 'evergreen', 1):
            crowns.draw_circle(c, r * sh.s)
            tri.draw_polyline([fitz.Point(c.x, c.y - 9), fitz.Point(c.x + 8, c.y + 6), fitz.Point(c.x - 8, c.y + 6), fitz.Point(c.x, c.y - 9)])
        else:
            crowns.draw_circle(c, r * sh.s); dots.draw_circle(c, 3.2)
    crowns.finish(color=(.18, .45, .24), fill=(.55, .78, .5), fill_opacity=.22, stroke_opacity=.75, width=1.1); crowns.commit()
    dots.finish(color=None, fill=(.1, .36, .18)); dots.commit()
    tri.finish(color=(.05, .22, .1), fill=(.05, .22, .1), width=.6, closePath=True); tri.commit()

OBST = []          # rectangles (map units) that section letters must keep clear of

def draw_special_ranges(sh):
    """the native numbering of the crypts and the cremains niches: the range on the overview (individual numbers are on the detail sheets)"""
    p = os.path.join(DATA, 'special_areas.json')
    if not os.path.exists(p): return
    pg = sh.page
    for r in json.load(open(p))['ranges']:
        b = r['bbox']; pad = 4; a = sh.P(b[0] - pad, b[1] - pad); c = sh.P(b[2] + pad, b[3] + pad)
        shp = pg.new_shape(); shp.draw_rect(fitz.Rect(a, c)); shp.finish(color=(.1, .28, .5), width=1.8, dashes='[7 5] 0', fill=None); shp.commit()
        short = ('Detail 1 · Crypts 1-68' if r['kind'] == 'crypt' else 'Detail 2 · Niches 1-80'); fs = 22; w = tw(short, fs, True) + 16
        x = (a.x + c.x) / 2 - w / 2 if r['kind'] == 'niche' else a.x - w - 8; y = c.y + 34 if r['kind'] == 'niche' else (a.y + c.y) / 2 - 6
        q = pg.new_shape(); q.draw_rect(fitz.Rect(x, y - fs, x + w, y + 8), radius=.2); q.finish(color=(.1, .28, .5), fill=(1, 1, 1), fill_opacity=.92, width=1); q.commit()
        text(pg, x + 8, y, short, fs, True, (.1, .28, .5))
        u0 = lambda px, py: (sh.view[0] + (px - sh.ox) / sh.s, sh.view[1] + (py - sh.oy) / sh.s)
        (ax, ay), (cx2, cy2) = u0(x, y - fs), u0(x + w, y + 8)
        OBST.append(sbox(min(ax, b[0] - pad), min(ay, b[1] - pad), max(cx2, b[2] + pad), max(cy2, b[3] + pad)))

def draw_map(sh, D, raw, cells, mode, trees):
    pg = sh.page; lots = D['lots']; R = D['reg']; trees_mode = mode == 'trees'
    pg.draw_rect(sh.clip, fill=(1, 1, 1), color=None)
    B.draw_base(sh, D, raw, skip_lots=True, boost=2.4 if trees_mode else 1.0)
    by = collections.defaultdict(list)
    for o in lots:
        if o['poly']: by[passof(o['hn'])[4] if not trees_mode else '#f4f3ee'].append(o)
    for col, os_ in by.items():
        shp = pg.new_shape()
        for o in os_: shp.draw_polyline([sh.P(x, y) for x, y in o['poly']] + [sh.P(*o['poly'][0])])
        shp.finish(color=(.35, .4, .5) if not trees_mode else (.7, .72, .76), fill=rgb(col), width=.5 if not trees_mode else .4, closePath=True, lineJoin=1); shp.commit()
    draw_unnumbered(sh, D, cells, trees_mode)
    if not trees_mode:
        small = [o for o in lots if not o.get('twin') and (not o['fs'] or o['fs'] * sh.s < CALLOUT_PT or not o['poly'])]
        ids = {id(o) for o in small}
        for o in lots:
            if o['fs'] and id(o) not in ids: B.put_label(sh, o)
        draw_callouts(sh, small, lots, cells)
        draw_twins(sh, lots)
    else:
        draw_trees(sh, trees)
    road_names(sh, trees_mode)

# ------------------------------------------------------------------ section letters, placed in open lanes with a short leader
def section_tags(sh, D, with_range):
    """one bold letter per section in a clear lane; a short leader runs from the letter to the edge of its section and never crosses a printed number"""
    from shapely.geometry import LineString
    st = ranges(D); polys = {}; labels = []
    for o in D['lots']:
        if o['poly'] and len(o['poly']) > 2: polys.setdefault(o['s'], []).append(Polygon(o['poly']).buffer(0))
        if o.get('fs'):
            hl = ADV * len(o['d']) * o['fs'] / 2 + .8; hw_ = o['fs'] * .5 + .8; vert = abs(abs(o.get('ang', 0)) - 90) < 45
            labels.append(sbox(o['cx'] - (hw_ if vert else hl), o['cy'] - (hl if vert else hw_), o['cx'] + (hw_ if vert else hl), o['cy'] + (hl if vert else hw_)))
    allp = [p for v_ in polys.values() for p in v_]; tree = STRtree(allp); ltree = STRtree(labels); v = sh.view
    placed = [sbox(x - 14, y - 14, x + 14, y + 14) for _, _, _, x, y in LANDMARKS] + list(OBST)
    for c_ in CALLOUTS:
        wl = (ADV * len(c_['text']) * 8.5 + 16) / sh.s; placed.append(sbox(c_['bx'] - wl / 2, c_['by'] - 9 / sh.s, c_['bx'] + wl / 2, c_['by'] + 9 / sh.s))
    for cid, r_ in INV.items():
        if r_['final_status'].startswith('awaiting') and cid in CELLP: placed.append(CELLP[cid].buffer(2))
    for t, x, y, ang, fs in ROADS: placed.append(sbox(x - 15, y - 95, x + 15, y + 5) if ang == -90 else sbox(x - 5, y - 20, x + 90, y + 10))
    big = 46; tags = []
    for sec in sorted(st, key=lambda s_: -st[s_]['n']):
        e = st[sec]; txt = sec; bw = twb(txt, big) + big * .8; bh = big * 1.3; wu, hu = bw / sh.s, bh / sh.s
        b = e['b']; U = unary_union(polys[sec]); Ub = U.boundary; best = None
        _g = Ub.segmentize(2.5) if hasattr(Ub, 'segmentize') else Ub; BP[sec] = np.array([c_ for g_ in (_g.geoms if hasattr(_g, 'geoms') else [_g]) for c_ in g_.coords])
        for gx in range(int(b[0] - 220), int(b[2] + 220), 6):
            for gy in range(int(b[1] - 170), int(b[3] + 170), 6):
                r = sbox(gx - wu / 2, gy - hu / 2, gx + wu / 2, gy + hu / 2)
                if r.bounds[0] < v[0] + 8 or r.bounds[2] > v[2] - 8 or r.bounds[1] < v[1] + 8 or r.bounds[3] > v[3] - 8: continue
                cov = sum(allp[i].intersection(r).area for i in tree.query(r, predicate='intersects')) / r.area
                if cov > .02: continue
                if any(r.intersects(q) for q in placed): continue
                lab = len(ltree.query(r, predicate='intersects'))
                d = r.distance(U); cost = lab * 800 + .35 * d + (0 if d < 70 else (d - 70) * 1.5); cross = 0; seg = None
                if d > 12:
                    ctr = np.array([gx, gy]); bp = BP[sec]; dd = np.hypot(bp[:, 0] - gx, bp[:, 1] - gy); order = np.argsort(dd)[:14]; bestseg = None
                    for j in order:
                        a_ = r.exterior.interpolate(r.exterior.project(Point(bp[j, 0], bp[j, 1]))); sg = LineString([(a_.x, a_.y), (bp[j, 0], bp[j, 1])])
                        cr = len(ltree.query(sg, predicate='intersects')) + sum(sg.intersects(q) for q in placed if q is not r)
                        if bestseg is None or (cr, sg.length) < (bestseg[0], bestseg[1].length): bestseg = (cr, sg)
                        if cr == 0: break
                    cross, seg = bestseg; cost += cross * 900 + seg.length * .35 - .35 * d
                if best is None or cost < best[0]: best = (cost, gx, gy, r, d, seg)
        if best is None or (best[5] is not None and (len(ltree.query(best[5], predicate='intersects')) or any(best[5].intersects(q) for q in placed))):
            alt = None      # no clear lane: the letter may sit on empty lot ground of its own section (never on a printed number), so no leader is needed
            for gx in range(int(b[0]), int(b[2]), 3):
                for gy in range(int(b[1]), int(b[3]), 3):
                    r = sbox(gx - wu / 2, gy - hu / 2, gx + wu / 2, gy + hu / 2)
                    if r.bounds[0] < v[0] + 8 or r.bounds[2] > v[2] - 8 or r.bounds[1] < v[1] + 8 or r.bounds[3] > v[3] - 8: continue
                    if len(ltree.query(r, predicate='intersects')) or any(r.intersects(q) for q in placed) or r.distance(U) > 0: continue
                    cov = sum(allp[i].intersection(r).area for i in tree.query(r, predicate='intersects')) / r.area
                    if alt is None or cov < alt[0]: alt = (cov, gx, gy, r)
            if alt is not None: best = (0, alt[1], alt[2], alt[3], 0, None)
        if best is None: continue
        c, gx, gy, r, d, seg = best; placed.append(r.buffer(3)); tags.append((sec, txt, gx, gy, wu, hu, r, seg, d, bw, bh))
    pg = sh.page; TAGS.clear()
    for sec, txt, gx, gy, wu, hu, r, seg, d, bw, bh in tags:
        TAGS.append(dict(sec=sec, cx=gx, cy=gy, wu=wu, hu=hu, seg=[list(c_) for c_ in seg.coords] if seg is not None and d > 12 else None))
        if seg is not None and d > 12:
            (x0, y0), (x1, y1) = list(seg.coords)[0], list(seg.coords)[-1]; l = pg.new_shape(); l.draw_line(sh.P(x0, y0), sh.P(x1, y1)); l.finish(color=NAVY, width=2.4); l.commit()
            dot = pg.new_shape(); dot.draw_circle(sh.P(x1, y1), 4.5); dot.finish(color=NAVY, fill=NAVY); dot.commit()
        p = sh.P(gx, gy)
        shp = pg.new_shape(); shp.draw_rect(fitz.Rect(p.x - bw / 2, p.y - bh / 2, p.x + bw / 2, p.y + bh / 2), radius=.2); shp.finish(color=NAVY, fill=(1, 1, 1), width=1.8); shp.commit()
        text(pg, p.x - twb(txt, big) / 2, p.y + big * .36, txt, big, True)

CELLP = {}
BP = {}
TAGS = []

# ------------------------------------------------------------------ the sheet around the map
def lot_sample(pg, x, y):
    """a lot with its printed number and the full form beside it"""
    shp = pg.new_shape(); shp.draw_rect(fitz.Rect(x, y, x + 150, y + 78)); shp.finish(color=(.35, .4, .5), fill=rgb('#d5ecd9'), width=1.4); shp.commit()
    fs = 46; t = '1698'; pg.insert_text((x + 75 - fitz.get_text_length(t, 'helv', fs) * .6 / 1.0 * 1.0 * .85, y + 58), t, fontsize=fs, fontname='dvsmb', fontfile=B.FONT, color=NAVY)

def panel_numbers(pg, D, st):
    y0 = H - BOT + 128
    # index (left): section, the whole H range, lots drawn, grid squares
    text(pg, MX, y0, 'Index of sections', 40, True); text(pg, MX + 400, y0, '(old section letters)', 26, False, GREY)
    names = sorted(st); half = (len(names) + 1) // 2; y = y0 + 52
    for col in (0, 1):
        xx = MX + col * 880
        for c, t in zip((0, 175, 590, 700), ('Section', 'H-numbers', 'Lots', 'Grid')): text(pg, xx + c, y, t, 22, True, GREY)
    for k, sname in enumerate(names):
        col, row = divmod(k, half); xx = MX + col * 880; yy = y + 44 + row * 52; e = st[sname]
        text(pg, xx, yy, 'Section %s' % sname, 27, True); text(pg, xx + 175, yy, '%s to %s' % (B.fmtH(e['lo']), B.fmtH(e['hi'])), 27); text(pg, xx + 590, yy, str(e['n']), 27); text(pg, xx + 700, yy, cellref(e['b']), 27)
        note = []
        if e['mlo']: note.append('margin strip %s to %s' % (B.fmtH(e['mlo']), B.fmtH(e['mhi'])))
        if e['missing']: note.append('%d number%s with no lot drawn' % (len(e['missing']), '' if len(e['missing']) == 1 else 's'))
        if note: text(pg, xx + 175, yy + 21, ' · '.join(note), 18, False, GREY)
    # how to read a number (middle)
    x2 = MX + 1840
    text(pg, x2, y0, 'Reading a number', 40, True)
    lot_sample(pg, x2, y0 + 26)
    text(pg, x2 + 176, y0 + 66, '= lot H001698', 40, True)
    text(pg, x2 + 176, y0 + 96, 'H and leading zeros are left off on the map.', 21, False, GREY)
    text(pg, x2, y0 + 138, 'Grave 3 of that lot is H0016983.', 21, False, GREY)
    text(pg, x2, y0 + 164, 'A / B after a number: the two rows of a double-row lot.', 21, False, GREY)
    for i, (lo, hi, nm, secs, col) in enumerate(PASSES):
        yy = y0 + 226 + i * 40; shp = pg.new_shape(); shp.draw_rect(fitz.Rect(x2, yy - 23, x2 + 50, yy + 7)); shp.finish(color=(.35, .4, .5), fill=rgb(col), width=.6); shp.commit()
        text(pg, x2 + 68, yy, '%s · Sections %s · H%06d to H%06d' % (nm, secs, lo, hi), 22)
    text(pg, x2, y0 + 226 + 6 * 40 + 14, 'Colour = the pass of the numbering route the lot belongs to.', 21, False, GREY)
    key(pg, y0, H - 100, True)

def panel_trees(pg, D, st, trees):
    y0 = H - BOT + 128; ev = sum(1 for t in trees if t[3] in (1, 'e', 'evergreen')); lf = len(trees) - ev
    text(pg, MX, y0, 'Tree key', 44, True)
    c = fitz.Point(MX + 60, y0 + 100); shp = pg.new_shape(); shp.draw_circle(c, 46); shp.finish(color=(.18, .45, .24), fill=(.55, .78, .5), fill_opacity=.22, width=1.4); shp.commit()
    d = pg.new_shape(); d.draw_circle(c, 5); d.finish(color=None, fill=(.1, .36, .18)); d.commit()
    text(pg, MX + 140, y0 + 96, 'Leafy tree: %d' % lf, 30, True); text(pg, MX + 140, y0 + 128, 'circle = crown as measured on the aerial photo, dot = tree centre', 21, False, GREY)
    c = fitz.Point(MX + 60, y0 + 230); shp = pg.new_shape(); shp.draw_circle(c, 40); shp.finish(color=(.18, .45, .24), fill=(.55, .78, .5), fill_opacity=.22, width=1.4); shp.commit()
    t = pg.new_shape(); t.draw_polyline([fitz.Point(c.x, c.y - 9), fitz.Point(c.x + 8, c.y + 6), fitz.Point(c.x - 8, c.y + 6), fitz.Point(c.x, c.y - 9)]); t.finish(color=(.05, .22, .1), fill=(.05, .22, .1), closePath=True); t.commit()
    text(pg, MX + 140, y0 + 226, 'Evergreen: %d' % ev, 30, True); text(pg, MX + 140, y0 + 258, 'same crown circle, dark triangle at the centre', 21, False, GREY)
    # roads and paths
    r = pg.new_shape(); r.draw_line(fitz.Point(MX + 14, y0 + 330), fitz.Point(MX + 106, y0 + 330)); r.finish(color=(.54, .58, .38), width=4.6); r.commit()
    text(pg, MX + 140, y0 + 338, 'Road, path and drive edge', 26, True)
    shp = pg.new_shape(); shp.draw_rect(fitz.Rect(MX + 18, y0 + 376, MX + 102, y0 + 408)); shp.finish(color=(.7, .72, .76), fill=(.957, .953, .933), width=.8); shp.commit()
    text(pg, MX + 140, y0 + 400, 'Lot (the numbers are on the H-number map)', 26)
    # short index: section letter and grid squares only
    x2 = MX + 1500
    text(pg, x2, y0, 'Sections', 40, True); names = sorted(st); half = (len(names) + 1) // 2
    for k, sname in enumerate(names):
        col, row = divmod(k, half); xx = x2 + col * 360; yy = y0 + 56 + row * 50
        text(pg, xx, yy, 'Section %s' % sname, 27, True); text(pg, xx + 160, yy, cellref(st[sname]['b']), 24, False, GREY)
    text(pg, x2, y0 + 56 + half * 50 + 24, 'Lot numbers and section ranges are on the H-number map.', 21, False, GREY)
    text(pg, x2, y0 + 56 + half * 50 + 54, 'Trees stand where the aerial photo shows a crown. The stand west of the cemetery is too', 21, False, GREY)
    text(pg, x2, y0 + 56 + half * 50 + 80, 'tangled to separate, so it is filled at a typical spacing.', 21, False, GREY)
    key(pg, y0, H - 100, False)

def landmark_list(pg, y0):
    x3 = MX + 2720; text(pg, x3, y0, 'Landmarks', 40, True)
    for i, (n, nm, note, lx, ly) in enumerate(LANDMARKS):
        col, row = divmod(i, 7); xx = x3 + col * 390; yy = y0 + 62 + row * 56
        marker(pg, fitz.Point(xx + 18, yy - 9), n, 17); text(pg, xx + 50, yy, nm, 24, True)
        if note: text(pg, xx + 50, yy + 21, note, 18, False, GREY)

def key(pg, y0, ky, numbers):
    landmark_list(pg, y0)
    if numbers:
        shp = pg.new_shape(); shp.draw_rect(fitz.Rect(MX, ky - 22, MX + 48, ky + 8)); shp.finish(color=(.55, .57, .6), fill=(.9, .9, .88), width=.6); shp.commit()
        x = MX
        for fill, col, dash, lab in (((.99, .93, .8), AMBER, '[4 3] 0', 'amber dashed = lot not yet numbered (old label in amber)'), ((.87, .91, .96), (.1, .28, .5), None, 'blue = crypt (own numbers)'), ((.93, .93, .91), (.6, .6, .62), None, 'grey = not a grave')):
            shp = pg.new_shape(); shp.draw_rect(fitz.Rect(x, ky - 22, x + 44, ky + 8)); shp.finish(color=col, fill=fill, width=1, dashes=dash); shp.commit()
            text(pg, x + 54, ky, lab, 22, False, GREY); x += 54 + tw(lab, 22) * 1.3 + 36
    text(pg, MX, H - 50, 'Source: Cedar Grove Ground Maps drawing (2022) and the old section maps. Positions follow the drawing, which is marked not to scale.', 21, False, GREY)

def inset_rects(sh):
    x0 = sh.clip.x0 + 12
    return fitz.Rect(x0, 1090, x0 + 330, 1676), fitz.Rect(x0 + 360, 1090, x0 + 920, 1378), fitz.Rect(x0 + 360, 1400, x0 + 920, 1688)

def native_numbers(sh2, view):
    """the native numbers of the crypts and niches (they are not H-numbers): small blue figures at their measured places"""
    import csv
    p = os.path.join(REPO, 'h-number-map', 'special_locations.csv')
    if not os.path.exists(p): return
    for r in csv.DictReader(open(p)):
        x, y = float(r['map_x']), float(r['map_y'])
        if not (view[0] <= x <= view[2] and view[1] <= y <= view[3]): continue
        n = r['name'].split()[-1]; fs = max(2.0, min(3.4, .75 * sh2.s * 0 + 3.0)) * sh2.s / 1.0
        q = sh2.P(x, y); fs = 6.4 if 'niche' in r['name'].lower() else 9.0
        sh2.page.insert_text(fitz.Point(q.x - ADV * len(n) * fs / 2, q.y + fs * .35), n, fontsize=fs, fontname='dvsmb', fontfile=B.FONT, color=(.1, .28, .5))

def draw_inset(pg, D, raw, cells, view, rect, title):
    """an enlarged, framed view of part of the drawing, rendered on a scratch page and placed as vector content"""
    tmp = fitz.open(); tp = tmp.new_page(width=rect.width, height=rect.height - 46); sh2 = Sheet2(tp, view, 0, 0, rect.width, rect.height - 46)
    saved = list(CALLOUTS); draw_map(sh2, D, raw, cells, 'numbers', None); CALLOUTS[:] = saved; native_numbers(sh2, view)
    pg.draw_rect(rect, fill=(1, 1, 1), color=None); pg.show_pdf_page(fitz.Rect(rect.x0, rect.y0 + 46, rect.x1, rect.y1), tmp, 0)
    shp = pg.new_shape(); shp.draw_rect(fitz.Rect(rect.x0, rect.y0, rect.x1, rect.y0 + 46)); shp.finish(color=None, fill=(.9, .93, .97)); shp.commit()
    text(pg, rect.x0 + 14, rect.y0 + 33, title, 28, True)
    shp = pg.new_shape(); shp.draw_rect(rect); shp.finish(color=NAVY, width=2.6, fill=None); shp.commit()

def build(mode='numbers', trees=None, dest=None):
    view = VIEW_NUM if mode == 'numbers' else VIEW_TREE
    load_inventory()
    D = svgmap.load(); raw = json.load(open(f'{DATA}/ai_raw.json')); cells = {c['id']: c for c in D['cells']}
    doc = fitz.open(); pg = doc.new_page(width=W, height=H)
    sh = Sheet2(pg, view, MX + 50, TOP, W - MX - 50, H - BOT)
    CALLOUTS.clear(); CELLP.clear()
    for cid, c_ in cells.items(): CELLP[cid] = Polygon(c_['poly']).buffer(0)
    insets = []
    if mode == 'numbers':    # enlarged views in the open south-west: the crypt court and the cremains strip
        r1, r2a, r2b = inset_rects(sh)
        insets = [((553, 303, 627, 418), r1, 'Detail 1 · Crypts 1-68'), ((815, 343, 905, 383), r2a, 'Detail 2a · Niches 1-40'), ((905, 343, 995, 383), r2b, 'Detail 2b · Niches 41-80')]
        inv = lambda x, y: (sh.view[0] + (x - sh.ox) / sh.s, sh.view[1] + (y - sh.oy) / sh.s)
        for _, r, _t in insets:
            (ax, ay), (bx_, by_) = inv(r.x0 - 8, r.y0 - 8), inv(r.x1 + 8, r.y1 + 8); OBST.append(sbox(ax, ay, bx_, by_))
    draw_map(sh, D, raw, cells, mode, trees)
    for v_, r, t_ in insets: draw_inset(pg, D, raw, cells, v_, r, t_)
    if mode == 'numbers': json.dump(CALLOUTS, open(os.path.join(DATA, 'callouts.json'), 'w'))
    draw_special_ranges(sh)
    section_tags(sh, D, mode == 'numbers')
    if mode == 'numbers': json.dump(TAGS, open(os.path.join(DATA, 'tags.json'), 'w'))
    grid_lines(sh)
    for n, nm, note, x, y in LANDMARKS:
        if view[0] <= x <= view[2] and view[1] <= y <= view[3]: marker(pg, sh.P(x, y), n, 20)
    pg.clip_to_rect(sh.clip)                         # nothing of the drawing may leave the frame
    pg.draw_rect(pg.rect, fill=B.BG, color=None, overlay=False)
    shp = pg.new_shape(); shp.draw_rect(sh.clip); shp.finish(color=NAVY, width=2.4, fill=None); shp.commit()
    grid_letters(sh)
    title = 'Cedar Grove Cemetery · H-Number Map' if mode == 'numbers' else 'Cedar Grove Cemetery · Tree Map'
    text(pg, MX, 100, title, 76, True)
    text(pg, MX, 152, 'University of Notre Dame · every lot with its H-number, sorted by the old section letters' if mode == 'numbers' else 'University of Notre Dame · where the trees stand, on the same map and grid as the H-number map', 32, False, GREY)
    nw = sum(1 for r in INV.values() if r['final_status'].startswith('awaiting'))
    if nw and mode == 'numbers':
        msg = 'Review copy · %d outlines under review' % nw; fsb = 34; bw = twb(msg, fsb) + 44
        shp = pg.new_shape(); shp.draw_rect(fitz.Rect(W - MX - bw, 62, W - MX, 120), radius=.2); shp.finish(color=AMBER, fill=AMBER_FILL, width=2); shp.commit()
        text(pg, W - MX - bw + 22, 103, msg, fsb, True, (.35, .2, .02))
        mean = 'Amber dashed outline = lot or object not yet identified or numbered'; fs2 = 24; mw = twb(mean, fs2) * 1.04
        sx = W - MX - mw - 76; shp = pg.new_shape(); shp.draw_rect(fitz.Rect(sx, 134, sx + 48, 158)); shp.finish(color=AMBER, fill=AMBER_FILL, width=2, dashes='[6 4] 0'); shp.commit()
        text(pg, sx + 62, 154, mean, fs2, False, (.2, .2, .25))
    st = ranges(D)
    if mode == 'numbers': panel_numbers(pg, D, st)
    else: panel_trees(pg, D, st, trees)
    dest = dest or os.path.join(REPO, 'h-number-map', 'site', 'pdf', 'Cedar_Grove_H-Number_Map_overall.pdf')
    os.makedirs(os.path.dirname(dest), exist_ok=True); doc.save(dest, garbage=3, deflate=True)
    return dest

if __name__ == '__main__':
    if '--trees' in sys.argv:
        i = sys.argv.index('--trees'); tf = sys.argv[i + 1] if len(sys.argv) > i + 1 and not sys.argv[i + 1].startswith('-') else None
        if tf: trees = json.load(open(tf))
        else: trees = [[t['x'], t['y'], t['radius'], t['kind']] for t in json.load(open(os.path.join(REPO, 'h-number-map', 'trees.json')))]
        print(build('trees', trees, os.path.join(REPO, 'h-number-map', 'site', 'pdf', 'Cedar_Grove_Tree_Map_overall.pdf')))
    else: print(build())
