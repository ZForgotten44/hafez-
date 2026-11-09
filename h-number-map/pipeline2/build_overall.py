"""Step 9b: the overall H-number map, one poster sheet (50 x 35 in, vector), with every lot's H-number, the old section letters,
grid references, the landmarks and an index.  Reads exactly the data the site and the other PDFs read.

    python3 build_overall.py                -> site/pdf/Cedar_Grove_H-Number_Map_overall.pdf
    python3 build_overall.py --trees FILE   -> the same sheet with the tree layer instead of the numbers (FILE = trees.json, [[x, y, radius, kind], ...] in map units)
"""
import json, math, os, sys, collections
import pymupdf as fitz
from shapely.geometry import Polygon, box as sbox
from shapely.strtree import STRtree
from common import *
import svgmap, build_pdf as B
from fit import ADV, INK_MID

W, H = 3600, 2520
VIEW = [335, 215, 1735, 940]                      # map units: lots, road names, the mausoleum corner and the east avenue
MX, TOP, BOT = 60, 200, 610
NAVY, GREY, PALE = B.NAVY, (.34, .38, .45), (.93, .92, .88)
PASSES = [(1, 836, 'Pass 1', 'B, A', '#cfe0f5'), (837, 1871, 'Pass 2', 'D, C', '#d5ecd9'), (1872, 2331, 'Pass 3', 'F, E', '#f6e7b9'),
          (2332, 2586, 'Pass 4', 'margins, G, H', '#f6d3cf'), (2587, 2835, 'Pass 5', 'M', '#dcd3ee'), (2836, 3185, 'Pass 6', 'K, J, I, L', '#cfe6e4')]
LANDMARKS = [   # number, name, note, x, y
    (1, 'Office', 'the cottage, Cedar Grove Cemetery office', 1370, 361), (2, 'Maintenance building', 'the garage', 1283, 385), (3, 'Saint Joseph', 'chapel', 1331, 314),
    (4, 'Mausoleum 1', 'Mary Queen of Angels', 634, 394), (5, 'Mausoleum 2', 'Mary Queen of All Saints', 634, 349),
    (6, 'Mausoleum 3', 'Mary Mother of the Church', 561, 407), (7, 'Mausoleum 4', 'Mary Mother of God', 561, 339),
    (8, 'Graves between the mausoleums', 'about 64 graves, not part of the H-numbering', 595, 370)]

class Sheet2:
    def __init__(self, page, view, x0, y0, x1, y1):
        self.page = page; self.view = view; aw, ah = x1 - x0, y1 - y0
        self.s = min(aw / (view[2] - view[0]), ah / (view[3] - view[1]))
        self.ox = x0 + (aw - self.s * (view[2] - view[0])) / 2; self.oy = y0 + (ah - self.s * (view[3] - view[1])) / 2
        self.clip = fitz.Rect(self.ox, self.oy, self.ox + self.s * (view[2] - view[0]), self.oy + self.s * (view[3] - view[1]))
    def P(self, x, y): return fitz.Point(self.ox + (x - self.view[0]) * self.s, self.oy + (y - self.view[1]) * self.s)

def rgb(h): return B.hex2rgb(h)
def ranges(D):
    """per section: lots, the H range of its body, the H range of its margin strip (sections B, D, F also own a margin strip in pass 4), bbox"""
    st = B.section_stats(D); out = {}
    for sec, e in st.items():
        hs = [o['hn'] for o in D['lots'] if o['s'] == sec]
        body = [h for h in hs if not (sec in 'BDF' and 2332 <= h <= 2412)]; marg = [h for h in hs if sec in 'BDF' and 2332 <= h <= 2412]
        out[sec] = dict(n=e['n'], b=e['b'], lo=min(body), hi=max(body), mlo=min(marg) if marg else None, mhi=max(marg) if marg else None)
    return out

def passof(h): return next(p for p in PASSES if p[0] <= h <= p[1])
def text(pg, x, y, t, fs, bold=False, color=NAVY, mono=False):
    pg.insert_text((x, y), t, fontsize=fs, fontname='uib' if bold else 'ui', fontfile=B.UIB if bold else B.UI, color=color)
def tw(t, fs, bold=False): return fitz.get_text_length(t, fontname='helv', fontsize=fs) * (1.06 if bold else 1.0)

def marker(pg, p, n, r):
    shp = pg.new_shape(); shp.draw_circle(p, r); shp.finish(color=NAVY, fill=(1, 1, 1), width=r * .16); shp.commit()
    s = str(n); f = r * 1.25
    pg.insert_text((p.x - tw(s, f, True) / 2, p.y + f * .36), s, fontsize=f, fontname='uib', fontfile=B.UIB, color=NAVY)

GX0, GY0, GC = 200, 0, 100          # the grid is anchored on the drawing, so a square has the same name on every map: columns from x = 200, rows from y = 0, 100 units each

def grid(sh, D, cols=None, rows=None):
    pg = sh.page; v = sh.view
    c0, c1 = int((v[0] - GX0) // GC), int((v[2] - GX0) // GC); r0, r1 = int((v[1] - GY0) // GC), int((v[3] - GY0) // GC)
    shp = pg.new_shape()
    for i in range(c0 + 1, c1 + 1): shp.draw_line(sh.P(GX0 + i * GC, v[1]), sh.P(GX0 + i * GC, v[3]))
    for j in range(r0 + 1, r1 + 1): shp.draw_line(sh.P(v[0], GY0 + j * GC), sh.P(v[2], GY0 + j * GC))
    shp.finish(color=(.62, .64, .68), width=.8, dashes='[10 8] 0'); shp.commit()
    for i in range(c0, c1 + 1):
        x0, x1 = max(v[0], GX0 + i * GC), min(v[2], GX0 + (i + 1) * GC)
        if x1 - x0 < 25: continue
        t = chr(65 + i - 0); c = sh.P((x0 + x1) / 2, v[1])
        text(pg, c.x - tw(t, 34, True) / 2, sh.oy - 14, t, 34, True, GREY); text(pg, c.x - tw(t, 34, True) / 2, sh.clip.y1 + 42, t, 34, True, GREY)
    for j in range(r0, r1 + 1):
        y0, y1 = max(v[1], GY0 + j * GC), min(v[3], GY0 + (j + 1) * GC)
        if y1 - y0 < 25: continue
        t = str(j + 1); c = sh.P(v[0], (y0 + y1) / 2)
        text(pg, sh.ox - 12 - tw(t, 34, True), c.y + 12, t, 34, True, GREY); text(pg, sh.clip.x1 + 12, c.y + 12, t, 34, True, GREY)

def cellref(b, v=None, cols=None, rows=None):
    c0 = int((b[0] - GX0) // GC); c1 = int((b[2] - GX0) // GC); r0 = int((b[1] - GY0) // GC); r1 = int((b[3] - GY0) // GC)
    return '%s%d to %s%d' % (chr(65 + c0), r0 + 1, chr(65 + c1), r1 + 1)

def road_names(sh):
    pg = sh.page
    for t, x, y, ang, fs in (('NOTRE DAME AVENUE', 1707, 605, -90, 30), ('HOLY CROSS DRIVE', 1080, 246, -3.5, 26)):
        p = sh.P(x, y); w = tw(t, fs, True)
        pg.insert_text(p, t, fontsize=fs, fontname='uib', fontfile=B.UIB, color=(.45, .48, .52), morph=(p, fitz.Matrix(ang)) if ang else None)

def draw_map(sh, D, raw, cells, mode, trees=None):
    pg = sh.page; lots = D['lots']; R = D['reg']
    pg.draw_rect(sh.clip, fill=(1, 1, 1), color=None)
    B.draw_base(sh, D, raw, skip_lots=True)
    # numbered lots: tinted by pass
    by = collections.defaultdict(list)
    for o in lots:
        if o['poly']: by[passof(o['hn'])[4] if mode == 'numbers' else '#f2f1ec'].append(o)
    for col, os_ in by.items():
        shp = pg.new_shape()
        for o in os_: shp.draw_polyline([sh.P(x, y) for x, y in o['poly']] + [sh.P(*o['poly'][0])])
        shp.finish(color=(.35, .4, .5), fill=rgb(col), width=.5, closePath=True, lineJoin=1); shp.commit()
    # outlines that carry no H-number
    shp = pg.new_shape()
    for u in R.get('unnumbered', []):
        if u['cell'] is None: continue
        shp.draw_polyline([sh.P(x, y) for x, y in cells[u['cell']]['poly']] + [sh.P(*cells[u['cell']]['poly'][0])])
    shp.finish(color=(.55, .57, .6), fill=(.9, .9, .88), width=.5, closePath=True, lineJoin=1); shp.commit()
    if mode == 'numbers':
        for o in lots:
            if o['fs']: B.put_label(sh, o)
    else:
        draw_trees(sh, trees)
    road_names(sh)

def draw_trees(sh, trees):
    pg = sh.page
    for x, y, r, kind in trees:
        if not (sh.view[0] <= x <= sh.view[2] and sh.view[1] <= y <= sh.view[3]): continue
        c = sh.P(x, y); rr = r * sh.s
        shp = pg.new_shape(); shp.draw_circle(c, rr)
        evergreen = kind in ('e', 'evergreen', 1)
        shp.finish(color=(.1, .38, .22) if evergreen else (.2, .5, .25), fill=(.12, .4, .25) if evergreen else (.45, .72, .4), fill_opacity=.62, width=.9); shp.commit()

def section_tags(sh, D, bb, with_range=True):
    """each tag goes where it hides the fewest lots: a search over free positions near its section (white aisles and margins first)"""
    from shapely.ops import unary_union
    st = ranges(D); polys = [Polygon(o['poly']).buffer(0) for o in D['lots'] if o['poly'] and len(o['poly']) > 2]; tree = STRtree(polys)
    placed = [sbox(1590, 232, 1730, 300), sbox(1650, 560, 1735, 660)]      # road names
    for m in LANDMARKS: placed.append(sbox(m[3] - 12, m[4] - 12, m[3] + 12, m[4] + 12))
    for sec, e in sorted(st.items()):
        txt, sub = 'Section %s' % sec, ('%s to %s' % (B.fmtH(e['lo']), B.fmtH(e['hi']))) if with_range else ''; big = 30
        bw = max(tw(txt, big, True), tw(sub, big * .46)) + big * .9
        wu, hu = bw / sh.s, big * 1.75 / sh.s; b = e['b']; cx0, cy0 = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        best = None
        for gx in range(int(b[0] - 110), int(b[2] + 110), 6):
            for gy in range(int(b[1] - 80), int(b[3] + 80), 6):
                r = sbox(gx - wu / 2, gy - hu / 2, gx + wu / 2, gy + hu / 2)
                if r.bounds[0] < bb[0] + 4 or r.bounds[2] > bb[2] - 4 or r.bounds[1] < bb[1] + 4 or r.bounds[3] > bb[3] - 4: continue
                hit = [polys[i] for i in tree.query(r, predicate='intersects')]
                cov = sum(p.intersection(r).area for p in hit) / r.area
                over = sum(r.intersects(q) for q in placed)
                dx = max(b[0] - gx, 0, gx - b[2]); dy = max(b[1] - gy, 0, gy - b[3])           # distance from the section's box
                c = cov * 100 + 80 * over + 0.5 * math.hypot(dx, dy) + 0.02 * math.hypot(gx - cx0, gy - cy0)
                if best is None or c < best[0]: best = (c, gx, gy, r)
        c, gx, gy, r = best; placed.append(r.buffer(2)); p = sh.P(gx, gy); B.section_tag(sh, txt, sub, p.x, p.y, big)
        pg = sh.page; q = sh.P(cx0, cy0)
        if best[0] > 20:       # still on lots: a thin leader to the section's centre would not help; keep the tag small and translucent-free
            pass

def panel(pg, D, mode, trees, cols, rows):
    y0 = H - BOT + 80; x = MX; st = ranges(D)
    text(pg, x, y0, 'Index of sections (old section letters)', 40, True)
    names = sorted(st); half = (len(names) + 1) // 2; y = y0 + 54
    for col in (0, 1):
        xx = x + col * 1000
        for c, t in zip((0, 215, 640, 740), ('Section', 'H-numbers', 'Lots', 'Grid squares')): text(pg, xx + c, y, t, 23, True, GREY)
    for k, sname in enumerate(names):
        col, row = divmod(k, half); xx = x + col * 1000; yy = y + 46 + row * 50; e = st[sname]
        text(pg, xx, yy, 'Section %s' % sname, 28, True); text(pg, xx + 215, yy, '%s to %s' % (B.fmtH(e['lo']), B.fmtH(e['hi'])), 28); text(pg, xx + 640, yy, str(e['n']), 28); text(pg, xx + 740, yy, cellref(e['b'], VIEW, cols, rows), 28)
        if e['mlo']: text(pg, xx + 215, yy + 22, 'margin strip %s to %s' % (B.fmtH(e['mlo']), B.fmtH(e['mhi'])), 19, False, GREY)
    x2 = MX + 2040
    text(pg, x2, y0, 'How the numbers run' if mode == 'numbers' else 'Trees', 40, True)
    if mode == 'numbers':
        text(pg, x2, y0 + 44, 'One number per lot along one fixed route, in six passes.', 22, False, GREY)
        for i, (lo, hi, nm, secs, col) in enumerate(PASSES):
            yy = y0 + 104 + i * 46; shp = pg.new_shape(); shp.draw_rect(fitz.Rect(x2, yy - 26, x2 + 56, yy + 8)); shp.finish(color=(.35, .4, .5), fill=rgb(col), width=.6); shp.commit()
            text(pg, x2 + 76, yy, '%s · Sections %s · H%06d to H%06d' % (nm, secs, lo, hi), 26)
        text(pg, x2, y0 + 104 + 6 * 46 + 10, 'A grave number is the lot number plus one digit (1 to 9):', 22, False, GREY)
        text(pg, x2, y0 + 104 + 6 * 46 + 38, 'H0016983 is grave 3 of lot H001698.', 22, False, GREY)
    else:
        text(pg, x2, y0 + 44, '%d trees, each drawn at its measured crown radius.' % (len(trees) if trees else 0), 22, False, GREY)
        for i, (nm, col) in enumerate((('leafy tree', (.45, .72, .4)), ('evergreen', (.12, .4, .25)))):
            yy = y0 + 104 + i * 46; shp = pg.new_shape(); shp.draw_circle(fitz.Point(x2 + 28, yy - 8), 20); shp.finish(color=(.1, .38, .22), fill=col, fill_opacity=.7, width=1); shp.commit(); text(pg, x2 + 76, yy, nm, 26)
    x3 = MX + 3000 - 40 - 20
    text(pg, x3, y0, 'Landmarks', 40, True)
    for i, (n, nm, note, lx, ly) in enumerate(LANDMARKS):
        yy = y0 + 62 + i * 58; marker(pg, fitz.Point(x3 + 20, yy - 10), n, 19); text(pg, x3 + 56, yy, nm, 26, True); text(pg, x3 + 56, yy + 24, note, 19, False, GREY)
    ky = H - 100
    shp = pg.new_shape(); shp.draw_rect(fitz.Rect(MX, ky - 22, MX + 48, ky + 8)); shp.finish(color=(.55, .57, .6), fill=(.9, .9, .88), width=.6); shp.commit()
    text(pg, MX + 62, ky, 'outline without an H-number (not part of the numbering)', 22, False, GREY)
    if mode == 'numbers': text(pg, MX + 700, ky, 'A lot drawn twice carries one number, written once.   A / B on a number = the two rows of a double-row lot.', 22, False, GREY)
    text(pg, MX, H - 50, 'Source: Cedar Grove Ground Maps drawing (2022). Positions follow the drawing, which is marked not to scale. H and leading zeros are left off the numbers on the map: 1698 is H001698.', 21, False, GREY)

def build(mode='numbers', trees=None, dest=None):
    global VIEW
    VIEW = [335, 215, 1735, 940] if mode == 'numbers' else [215, 55, 1810, 1045]
    D = svgmap.load(); raw = json.load(open(f'{DATA}/ai_raw.json')); cells = {c['id']: c for c in D['cells']}
    doc = fitz.open(); pg = doc.new_page(width=W, height=H); pg.draw_rect(pg.rect, fill=B.BG, color=None)
    sh = Sheet2(pg, VIEW, MX + 50, TOP, W - MX - 50, H - BOT)
    cols, rows = 14, 8
    draw_map(sh, D, raw, cells, mode, trees)
    section_tags(sh, D, VIEW, mode == 'numbers')
    grid(sh, D)
    for n, nm, note, x, y in LANDMARKS: marker(pg, sh.P(x, y), n, 21)
    title = 'Cedar Grove Cemetery · H-Number Map' if mode == 'numbers' else 'Cedar Grove Cemetery · Tree Map'
    text(pg, MX, 98, title, 76, True)
    text(pg, MX, 150, 'University of Notre Dame · every lot with its H-number, sorted by the old section letters' if mode == 'numbers' else 'University of Notre Dame · where the trees stand, on the same map and grid as the H-number map', 32, False, GREY)
    # frame
    shp = pg.new_shape(); shp.draw_rect(sh.clip); shp.finish(color=NAVY, width=2, fill=None); shp.commit()
    panel(pg, D, mode, trees, cols, rows)
    dest = dest or os.path.join(REPO, 'h-number-map', 'site', 'pdf', 'Cedar_Grove_H-Number_Map_overall.pdf')
    os.makedirs(os.path.dirname(dest), exist_ok=True); doc.save(dest, garbage=3, deflate=True)
    return dest

if __name__ == '__main__':
    if '--trees' in sys.argv:
        tf = sys.argv[sys.argv.index('--trees') + 1]; print(build('trees', json.load(open(tf)), os.path.join(REPO, 'h-number-map', 'site', 'pdf', 'Cedar_Grove_Tree_Map_overall.pdf')))
    else: print(build())
