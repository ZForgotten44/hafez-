"""Step 9b: the two overall maps, each one poster sheet (50 x 35 in, vector).

  H-number map  every lot with its H-number, tinted by walking pass, old section letters, grid, landmarks, the full index of sections
  Tree map      the same sheet and grid, the trees on a quiet lot base, the tree key first, a short index

    python3 build_overall.py                 -> site/pdf/Cedar_Grove_H-Number_Map_overall.pdf
    python3 build_overall.py --trees         -> site/pdf/Cedar_Grove_Tree_Map_overall.pdf   (trees from math/three/data3d.json: [[x, y, radius, evergreen], ...])
    python3 build_overall.py --trees FILE    -> the same, from another tree list in the same shape

The drawing is clipped to the map frame; the title, grid letters and footer sit in their own clear space."""
import json, math, os, sys, collections
import pymupdf as fitz
from shapely.geometry import Polygon, box as sbox
from shapely.ops import nearest_points, unary_union
from shapely.strtree import STRtree
from common import *
import svgmap, build_pdf as B
from fit import ADV, INK_MID

W, H = 3600, 2520
VIEW_NUM = [335, 215, 1735, 940]                  # lots, road names, the mausoleum corner and the east avenue
VIEW_TREE = [215, 55, 1810, 1045]                 # the whole aerial: the woods west of the cemetery too
MX, TOP, BOT = 60, 200, 610
NAVY, GREY, PALE = B.NAVY, (.34, .38, .45), (.93, .92, .88)
PASSES = [(1, 836, 'Pass 1', 'B, A', '#cfe0f5'), (837, 1871, 'Pass 2', 'D, C', '#d5ecd9'), (1872, 2331, 'Pass 3', 'F, E', '#f6e7b9'),
          (2332, 2586, 'Pass 4', 'margins, G, H', '#f6d3cf'), (2587, 2835, 'Pass 5', 'M', '#dcd3ee'), (2836, 3185, 'Pass 6', 'K, J, I, L', '#cfe6e4')]
# number, name, note, x, y (drawing units, read off the drawing and the old section maps)
LANDMARKS = [
    (1, 'Office', 'the cottage', 1378, 358), (2, 'Maintenance building', 'the garage', 1288, 385), (3, 'Chapel', 'in Section B', 1415, 538),
    (4, 'Saint Joseph', 'hexagon marker', 1331, 314), (5, 'Parking', 'north of the office', 1288, 336), (6, 'Restroom', 'hatched building, accessible space', 1330, 341),
    (7, 'Mausoleum 1', 'Mary Queen of Angels', 635, 399), (8, 'Mausoleum 2', 'Mary Queen of All Saints', 635, 355), (9, 'Mausoleum 3', 'Mary Mother of the Church', 562, 412),
    (10, 'Mausoleum 4', 'Mary Mother of God', 562, 342), (11, 'Mausoleum crypts', 'numbered 1 to 68, no H-number', 595, 380),
    (12, 'Cremains area', 'niches 1 to 80, no H-number', 905, 361), (13, 'Spoils yard', '', 386, 534)]
EXTRA_NOTES = {'M': '6 drawn lots have no H-number yet: 56, 57, 62, 63, 68, 69'}
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
    pg = sh.page; v = sh.view
    c0, c1 = int((v[0] - GX0) // GC), int((v[2] - GX0) // GC); r0, r1 = int((v[1] - GY0) // GC), int((v[3] - GY0) // GC)
    for i in range(c0, c1 + 1):
        x0, x1 = max(v[0], GX0 + i * GC), min(v[2], GX0 + (i + 1) * GC)
        if x1 - x0 < 25: continue
        t = chr(65 + i); c = sh.P((x0 + x1) / 2, v[1])
        text(pg, c.x - tw(t, 34, True) / 2, sh.clip.y0 - 16, t, 34, True, GREY); text(pg, c.x - tw(t, 34, True) / 2, sh.clip.y1 + 46, t, 34, True, GREY)
    for j in range(r0, r1 + 1):
        y0, y1 = max(v[1], GY0 + j * GC), min(v[3], GY0 + (j + 1) * GC)
        if y1 - y0 < 25: continue
        t = str(j + 1); c = sh.P(v[0], (y0 + y1) / 2)
        text(pg, sh.clip.x0 - 16 - tw(t, 34, True), c.y + 12, t, 34, True, GREY); text(pg, sh.clip.x1 + 16, c.y + 12, t, 34, True, GREY)

def cellref(b):
    c0 = int((b[0] - GX0) // GC); c1 = int((b[2] - GX0) // GC); r0 = int((b[1] - GY0) // GC); r1 = int((b[3] - GY0) // GC)
    return '%s%d to %s%d' % (chr(65 + c0), r0 + 1, chr(65 + c1), r1 + 1)

def road_names(sh, strong):
    pg = sh.page
    for t, x, y, ang, fs in ROADS:
        p = sh.P(x, y)
        pg.insert_text(p, t, fontsize=fs, fontname='uib', fontfile=B.UIB, color=(.3, .33, .38) if strong else (.45, .48, .52), morph=(p, fitz.Matrix(ang)) if ang else None)

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
    shp = pg.new_shape()
    for u in R.get('unnumbered', []):
        if u['cell'] is None: continue
        shp.draw_polyline([sh.P(x, y) for x, y in cells[u['cell']]['poly']] + [sh.P(*cells[u['cell']]['poly'][0])])
    shp.finish(color=(.55, .57, .6), fill=(.9, .9, .88), width=.5, closePath=True, lineJoin=1); shp.commit()
    if not trees_mode:
        for o in lots:
            if o['fs']: B.put_label(sh, o)
    else:
        draw_trees(sh, trees)
    road_names(sh, trees_mode)

# ------------------------------------------------------------------ section letters, placed in open lanes with a short leader
def section_tags(sh, D, with_range):
    st = ranges(D); polys = {}
    for o in D['lots']:
        if o['poly'] and len(o['poly']) > 2: polys.setdefault(o['s'], []).append(Polygon(o['poly']).buffer(0))
    allp = [p for v in polys.values() for p in v]; tree = STRtree(allp); v = sh.view
    placed = [sbox(x - 14, y - 14, x + 14, y + 14) for _, _, _, x, y in LANDMARKS]
    for t, x, y, ang, fs in ROADS: placed.append(sbox(x - 15, y - 95, x + 15, y + 5) if ang == -90 else sbox(x - 5, y - 20, x + 90, y + 10))
    big = 26 if not with_range else 28; tags = []
    for sec in sorted(st, key=lambda s: -st[s]['n']):
        e = st[sec]; txt = 'Section %s' % sec; bw = tw(txt, big, True) + big * .9; wu, hu = bw / sh.s, big * 1.5 / sh.s
        b = e['b']; cx0, cy0 = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2; U = unary_union(polys[sec]); best = None
        for gx in range(int(b[0] - 220), int(b[2] + 220), 6):
            for gy in range(int(b[1] - 170), int(b[3] + 170), 6):
                r = sbox(gx - wu / 2, gy - hu / 2, gx + wu / 2, gy + hu / 2)
                if r.bounds[0] < v[0] + 6 or r.bounds[2] > v[2] - 6 or r.bounds[1] < v[1] + 6 or r.bounds[3] > v[3] - 6: continue
                cov = sum(allp[i].intersection(r).area for i in tree.query(r, predicate='intersects')) / r.area
                over = sum(r.intersects(q) for q in placed)
                d = r.distance(U)
                c = cov * 400 + 120 * over + 0.35 * d + (0 if d < 90 else (d - 90) * 1.5)
                if best is None or c < best[0]: best = (c, gx, gy, r, d)
        c, gx, gy, r, d = best; placed.append(r.buffer(3)); tags.append((sec, txt, gx, gy, wu, hu, r, U, d))
    pg = sh.page
    for sec, txt, gx, gy, wu, hu, r, U, d in tags:
        if d > 14:       # short leader from the tag to the nearest lot of the section
            a, bpt = nearest_points(r, U); l = pg.new_shape(); l.draw_line(sh.P(a.x, a.y), sh.P(bpt.x, bpt.y)); l.finish(color=NAVY, width=2.2); l.commit()
            dot = pg.new_shape(); dot.draw_circle(sh.P(bpt.x, bpt.y), 4); dot.finish(color=NAVY, fill=NAVY); dot.commit()
        p = sh.P(gx, gy); bw = wu * sh.s; bh = hu * sh.s
        shp = pg.new_shape(); shp.draw_rect(fitz.Rect(p.x - bw / 2, p.y - bh / 2, p.x + bw / 2, p.y + bh / 2), radius=.25); shp.finish(color=NAVY, fill=(1, 1, 1), fill_opacity=.94, width=1.6); shp.commit()
        text(pg, p.x - tw(txt, big, True) / 2, p.y + big * .36, txt, big, True)

# ------------------------------------------------------------------ the sheet around the map
def lot_sample(pg, x, y):
    """a lot with its printed number and the full form beside it"""
    shp = pg.new_shape(); shp.draw_rect(fitz.Rect(x, y, x + 150, y + 78)); shp.finish(color=(.35, .4, .5), fill=rgb('#d5ecd9'), width=1.4); shp.commit()
    fs = 46; t = '1698'; pg.insert_text((x + 75 - fitz.get_text_length(t, 'helv', fs) * .6 / 1.0 * 1.0 * .85, y + 58), t, fontsize=fs, fontname='dvsmb', fontfile=B.FONT, color=NAVY)

def panel_numbers(pg, D, st):
    y0 = H - BOT + 76
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
        if sname in EXTRA_NOTES: text(pg, xx + 175, yy + 40, EXTRA_NOTES[sname], 18, False, GREY)
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
    y0 = H - BOT + 76; ev = sum(1 for t in trees if t[3] in (1, 'e', 'evergreen')); lf = len(trees) - ev
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
        text(pg, MX + 62, ky, 'grey outline = a drawn lot without an H-number (mausoleum crypts, repeated labels)', 22, False, GREY)
    text(pg, MX, H - 50, 'Source: Cedar Grove Ground Maps drawing (2022) and the old section maps. Positions follow the drawing, which is marked not to scale.', 21, False, GREY)

def build(mode='numbers', trees=None, dest=None):
    view = VIEW_NUM if mode == 'numbers' else VIEW_TREE
    D = svgmap.load(); raw = json.load(open(f'{DATA}/ai_raw.json')); cells = {c['id']: c for c in D['cells']}
    doc = fitz.open(); pg = doc.new_page(width=W, height=H)
    sh = Sheet2(pg, view, MX + 50, TOP, W - MX - 50, H - BOT)
    draw_map(sh, D, raw, cells, mode, trees)
    section_tags(sh, D, mode == 'numbers')
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
        else: trees = json.load(open(os.path.join(REPO, 'h-number-map', 'math', 'three', 'data3d.json')))['trees']
        print(build('trees', trees, os.path.join(REPO, 'h-number-map', 'site', 'pdf', 'Cedar_Grove_Tree_Map_overall.pdf')))
    else: print(build())
