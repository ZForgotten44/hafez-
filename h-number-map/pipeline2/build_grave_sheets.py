"""Grave-level sheets for the sections that have burial records (J, K, M).

Every grave in the burial workbook (/Section J|K|M.xlsx, record id + status only, no names) gets its own printed grave ID, vacant ones included,
at its documented position inside its lot.  Grave ID = decoder v2 lot H-number x 10 + grave digit, printed 'H0026183'.

Documented position (assumption, stated on every sheet): graves run TOP to BOTTOM inside a lot (decoder docstring), top = north, so grave 1 is at the
north end of the lot.  A lot is cut along its long axis into as many equal cells as its highest recorded grave number (all lots but K 16 have graves 1..n).
For the few lots whose long axis is horizontal the end with the smaller y is the 'north' end; with no difference in y (< 1 unit) the west end.
A lot whose outline was not traced in the drawing (label only) is drawn as a dashed nominal box between its neighbours.

  python3 build_grave_sheets.py   ->  site/pdf/Cedar_Grove_Grave_IDs_{J,K,M}.pdf  and  ../grave_positions_JKM.csv"""
import csv, json, math, os, re, sys, collections
import numpy as np
import openpyxl
import pymupdf as fitz
from shapely.geometry import Polygon, box as sbox
from shapely import affinity
from common import *
import svgmap, build_pdf as B
from fit import ADV, INK_MID

sys.path.insert(0, os.path.join(REPO, 's4'))
import s4decoder1 as DEC

S = 8.0                                       # printed points per drawing unit: a grave ID is >= 6.5 pt, the narrowest lot (K 64, 4.5 units) still holds one
W, H, M, T, BOT = 1224, 792, 36, 54, 30
FS_MIN, FS_MAX = 6.5, 9.0
STATUS_CLASS = {'Occupied': 'occupied', 'Sold': 'sold', 'Reserved': 'sold', 'Available': 'vacant'}
CLASS_FILL = {'occupied': '#b9c7da', 'sold': '#f4dfae', 'vacant': '#dcf0dc', 'other': '#e2d3ea'}
CLASS_NAME = {'occupied': 'Occupied', 'sold': 'Sold or reserved', 'vacant': 'Vacant (Available)', 'other': 'Other (Tree, hold, columbarium hold)'}
NAVY = B.NAVY; FONT = B.FONT
GX0, GY0, GC = 200, 0, 100

def cellref(b):
    return '%s%d to %s%d' % (chr(65 + int((b[0] - GX0) // GC)), int(b[1] // GC) + 1, chr(65 + int((b[2] - GX0) // GC)), int(b[3] // GC) + 1)

def records(sec):
    ws = openpyxl.load_workbook(os.path.join(REPO, 'Section %s.xlsx' % sec), read_only=True).worksheets[0]; out = collections.OrderedDict()
    for r in ws.iter_rows(min_row=2, values_only=True):
        if not r[0]: continue
        m = re.match(r'CEDARGROVE-%s-(\w+)-(\d+)-?$' % sec, r[0])
        out.setdefault(m.group(1), []).append((int(m.group(2)), r[0], r[2] or ''))      # grave, record id, status. names and owners are never read
    return out

def frame_of(poly):
    """long axis u (unit vector, pointing to the 'north' end), short axis v, origin, long and short length, in the lot's own frame"""
    r = Polygon(poly).minimum_rotated_rectangle; c = list(r.exterior.coords)[:4]
    e = [(c[(i + 1) % 4][0] - c[i][0], c[(i + 1) % 4][1] - c[i][1], i) for i in range(2)]
    ex, ey, i0 = max(e, key=lambda t: math.hypot(t[0], t[1])); L = math.hypot(ex, ey); u = np.array([ex, ey]) / L
    short = min(math.hypot(a, b) for a, b, _ in e)
    if abs(u[1]) >= 1.0 / L: u = u if u[1] > 0 else -u              # u points south, so the smallest projection is the north end (grave 1)
    else: u = u if u[0] > 0 else -u                                 # horizontal lot: west end first
    v = np.array([-u[1], u[0]])
    P = np.array(poly); t = P @ u; s_ = P @ v
    return u, v, t.min(), t.max(), s_.min(), s_.max()

def nominal_poly(o, lots_by_sec):
    """a label-only lot: a box between its vertical neighbours, as wide as theirs"""
    x, y = o['cx'], o['cy']; same = [q for q in lots_by_sec if q['poly'] and abs(q['cx'] - x) < 5 and q is not o]
    above = [q for q in same if q['cy'] < y]; below = [q for q in same if q['cy'] > y]
    w = float(np.median([max(p[0] for p in q['poly']) - min(p[0] for p in q['poly']) for q in same])) if same else 7.4
    y0 = max(p[1] for p in max(above, key=lambda q: q['cy'])['poly']) if above else None
    y1 = min(p[1] for p in min(below, key=lambda q: q['cy'])['poly']) if below else None
    if y0 is not None and y1 is not None and 5 < y1 - y0 < 16: pass
    elif y0 is not None: y1 = y0 + 11.0
    elif y1 is not None: y0 = y1 - 11.0
    else: y0, y1 = y - 5.5, y + 5.5
    return [(x - w / 2, y0), (x + w / 2, y0), (x + w / 2, y1), (x - w / 2, y1)]

def build_cells(poly, n_cells):
    u, v, t0, t1, s0, s1 = frame_of(poly); pg = Polygon(poly).buffer(0); cells = []; step = (t1 - t0) / n_cells
    for k in range(n_cells):
        a, b = t0 + k * step, t0 + (k + 1) * step
        rect = [u * a + v * s0, u * b + v * s0, u * b + v * s1, u * a + v * s1]
        cell = Polygon([tuple(p) for p in rect]).intersection(pg)
        if cell.is_empty: cell = Polygon([tuple(p) for p in rect])
        if cell.geom_type != 'Polygon': cell = max(cell.geoms, key=lambda g: g.area)
        cells.append(cell)
    return cells, (u, v, step, s1 - s0)

def text_plan(cells, u, v, step, width, n_cells, text):
    """choose the text direction (across the lot or along it) and the largest size that fits the smallest cell"""
    nch = len(text); best = None
    for direction, along, across in (('across', width, step), ('along', step, width)):
        # text length runs along 'along'; text height across the other
        fs = min(FS_MAX, 0.9 * along * S / (nch * ADV), 0.8 * across * S / 0.78)
        if best is None or fs > best[1] + 0.3: best = (direction, fs)
    return best

def put_text(pg, c, text, fs, ang, color=NAVY):
    w = ADV * len(text) * fs; p0 = fitz.Point(c.x - w / 2, c.y + INK_MID * fs)
    pg.insert_text(p0, text, fontsize=fs, fontname='dvsmb', fontfile=FONT, color=color, morph=(c, fitz.Matrix(ang)) if abs(ang) > .05 else None)

def build(sec, D, raw, rec, lots_all):
    lots = [o for o in lots_all if o['s'] == sec]; bylab = {o['l']: o for o in lots}
    items = []                                                          # (lot record, polygon, nominal?, graves)
    for lab, gl in rec.items():
        o = bylab.get(lab)
        if o is None: items.append(dict(lab=lab, o=None, graves=gl)); continue
        poly = o['poly'] or nominal_poly(o, lots); items.append(dict(lab=lab, o=o, poly=poly, nominal=not o['poly'], graves=gl))
    drawn = [it for it in items if it['o'] is not None]
    table = [r['lot_label'] for r in DEC.full_table(sec)]
    notdrawn = [dict(lab=l) for l in table if l not in bylab]               # numbers reserved in the decoder with no lot in the drawing
    allpts = [p for it in drawn for p in it['poly']]
    bb = [min(p[0] for p in allpts) - 6, min(p[1] for p in allpts) - 6, max(p[0] for p in allpts) + 6, max(p[1] for p in allpts) + 6]
    ww, wh = (W - 2 * M) / S, (H - T - BOT) / S
    maxdim = max(max(max(p[0] for p in it['poly']) - min(p[0] for p in it['poly']), max(p[1] for p in it['poly']) - min(p[1] for p in it['poly'])) for it in drawn)
    wins = B.tiles(bb, ww, wh, maxdim + 3); own = collections.defaultdict(list)
    for it in drawn:
        xs = [p[0] for p in it['poly']]; ys = [p[1] for p in it['poly']]; b = [min(xs), min(ys), max(xs), max(ys)]
        for k, w in enumerate(wins):
            if b[0] >= w[0] + 0.5 and b[2] <= w[2] - 0.5 and b[1] >= w[1] + 0.5 and b[3] <= w[3] - 0.5: own[k].append(it); break
        else: raise SystemExit('lot %s %s fits no page' % (sec, it['lab']))
    used = [k for k in range(len(wins)) if own[k]]
    doc = fitz.open(); rows = []; fname = 'Cedar_Grove_Grave_IDs_%s.pdf' % sec; small = []
    counts = collections.Counter()
    for n, k in enumerate(used):
        w = wins[k]; sh = B.Sheet(doc, W, H, w, M, T, BOT); pg = sh.page; pg.draw_rect(pg.rect, fill=B.BG, color=None)
        B.draw_base(sh, D, raw, skip_lots=True)
        for it in own[k]:
            gmax = max(g for g, _, _ in it['graves']); cells, (u, v, step, width) = build_cells(it['poly'], gmax)
            cls = {g: STATUS_CLASS.get(st, 'other') for g, _, st in it['graves']}
            # fills and cell dividers
            for g in range(1, gmax + 1):
                cell = cells[g - 1]; pts = [sh.P(x, y) for x, y in list(cell.exterior.coords)[:-1]]
                shp = pg.new_shape(); shp.draw_polyline(pts + [pts[0]])
                if g in cls: shp.finish(color=(.45, .5, .58), fill=B.hex2rgb(CLASS_FILL[cls[g]]), width=.45, closePath=True)
                else: shp.finish(color=(.45, .5, .58), fill=(.95, .95, .95), width=.45, closePath=True, dashes='[2 2] 0')     # a position with no workbook record
                shp.commit()
            outline = [sh.P(x, y) for x, y in it['poly']]; shp = pg.new_shape(); shp.draw_polyline(outline + [outline[0]])
            shp.finish(color=NAVY, width=1.1, closePath=True, dashes='[4 2] 0' if it['nominal'] else None); shp.commit()
            lot_h = DEC.h_lot(sec, it['lab'])[0]
            txt0 = 'H%07d' % (lot_h * 10 + 1); direction, fs = text_plan(cells, u, v, step, width, gmax, txt0)
            ang = math.degrees(math.atan2(v[1], v[0])) if direction == 'across' else math.degrees(math.atan2(u[1], u[0]))
            ang = ((ang + 90) % 180) - 90
            if fs < FS_MIN - 0.01: small.append((sec, it['lab'], round(fs, 2)))
            for g, rid, st in it['graves']:
                hg, hfmt = DEC.h_grave(sec, it['lab'], g); c = sh.P(*[float(a) for a in cells[g - 1].centroid.coords[0]])
                put_text(pg, c, hfmt, fs, ang); cc = cells[g - 1].centroid
                rows.append(dict(record_id=rid, section=sec, lot_label=it['lab'], grave=g, status=st, v2_h_grave=hfmt, lot_h='H%06d' % lot_h, sheet=fname, page=n + 1,
                                 x=round(cc.x, 2), y=round(cc.y, 2), outline='nominal box (outline not traced)' if it['nominal'] else 'traced', cells_in_lot=gmax, text_pt=round(fs, 2)))
                counts[CLASS_FILL and cls[g]] += 1
        pg.clip_to_rect(sh.clip)
        shp = pg.new_shape(); shp.draw_rect(sh.clip); shp.finish(color=(.6, .62, .68), width=.6, fill=None); shp.commit()
        frame(pg, sec, n + 1, len(used), w, bb, [wins[j] for j in used], own, sh, notdrawn, lots_all)
    doc.save(os.path.join(REPO, 'h-number-map', 'site', 'pdf', fname), garbage=3, deflate=True)
    return rows, dict(pages=len(used), notdrawn=notdrawn, small=small, counts=counts, lots=len(drawn))

def frame(pg, sec, n, total, win, bb, wins, own, sh, notdrawn, lots_all):
    pg.insert_text((M, 34), 'Grave IDs · Section %s' % sec, fontsize=22, fontname='uib', fontfile=B.UIB, color=NAVY)
    pg.insert_text((M, 49), 'Cedar Grove Cemetery · page %d of %d · grid squares %s · numbering v2 (H000001 to H003191)' % (n, total, cellref(win)), fontsize=8.5, fontname='ui', fontfile=B.UI, color=(.34, .38, .45))
    # legend
    x = M; ky = H - 17
    for cls in ('occupied', 'sold', 'vacant', 'other'):
        shp = pg.new_shape(); shp.draw_rect(fitz.Rect(x, ky - 6, x + 14, ky + 5)); shp.finish(color=(.45, .5, .58), fill=B.hex2rgb(CLASS_FILL[cls]), width=.5); shp.commit()
        pg.insert_text((x + 18, ky + 3), CLASS_NAME[cls], fontsize=7.5, fontname='ui', fontfile=B.UI, color=(.2, .24, .3)); x += 28 + fitz.get_text_length(CLASS_NAME[cls], 'helv', 7.5)
    shp = pg.new_shape(); shp.draw_rect(fitz.Rect(x, ky - 6, x + 14, ky + 5)); shp.finish(color=(.45, .5, .58), fill=(.95, .95, .95), width=.5, dashes='[2 2] 0'); shp.commit()
    pg.insert_text((x + 18, ky + 3), 'no workbook record', fontsize=7.5, fontname='ui', fontfile=B.UI, color=(.2, .24, .3))
    pg.insert_text((M, H - 6), 'H0026183 = lot H002618 + grave 3. Graves run top (north) to bottom: grave 1 is at the north end of the lot. Heavy outline = lot, thin lines = graves, dashed outline = lot outline not traced.', fontsize=7, fontname='ui', fontfile=B.UI, color=(.34, .38, .45))
    if notdrawn and n == 1:
        t = 'Reserved numbers, no lot drawn: ' + ', '.join('%s %s %s' % (sec, it['lab'], 'H%06d' % DEC.h_lot(sec, it['lab'])[0]) for it in notdrawn)
        pg.insert_text((M, 63), t, fontsize=7, fontname='ui', fontfile=B.UI, color=(.6, .3, .1))
    # index map
    iw = 150; ih = iw * (bb[3] - bb[1]) / (bb[2] - bb[0]); ix, iy = W - M - iw, 12; k = iw / (bb[2] - bb[0])
    if ih > 44: ih = 44; k = ih / (bb[3] - bb[1]); iw = k * (bb[2] - bb[0]); ix = W - M - iw
    shp = pg.new_shape(); shp.draw_rect(fitz.Rect(ix, iy, ix + iw, iy + ih)); shp.finish(color=(.8, .8, .8), fill=(.97, .97, .95), width=.4); shp.commit()
    shp = pg.new_shape()
    for o in lots_all:
        if o['s'] == sec and o['poly']:
            xs = [p[0] for p in o['poly']]; ys = [p[1] for p in o['poly']]; shp.draw_rect(fitz.Rect(ix + (min(xs) - bb[0]) * k, iy + (min(ys) - bb[1]) * k, ix + (max(xs) - bb[0]) * k + .4, iy + (max(ys) - bb[1]) * k + .4))
    shp.finish(color=(.55, .6, .68), fill=(.55, .6, .68), width=.2); shp.commit()
    r = fitz.Rect(ix + (win[0] - bb[0]) * k, iy + (win[1] - bb[1]) * k, ix + (win[2] - bb[0]) * k, iy + (win[3] - bb[1]) * k) & fitz.Rect(ix, iy, ix + iw, iy + ih)
    shp = pg.new_shape(); shp.draw_rect(r); shp.finish(color=(201 / 255, 137 / 255, 47 / 255), fill=(201 / 255, 137 / 255, 47 / 255), fill_opacity=.3, width=.8); shp.commit()

def run():
    D = svgmap.load(); raw = json.load(open(f'{DATA}/ai_raw.json')); lots_all = D['lots']; allrows = []; info = {}
    for sec in 'JKM':
        rows, inf = build(sec, D, raw, records(sec), lots_all); allrows += rows; info[sec] = inf
        print('Section %s: %d lots drawn, %d graves, %d pages, text below %.1f pt: %s, not drawn (reserved numbers): %s, status %s' % (sec, inf['lots'], len(rows), inf['pages'], FS_MIN, inf['small'] or 'none',
              [(it['lab'], DEC.h_lot(sec, it['lab'])[0]) for it in inf['notdrawn']] or 'none', dict(inf['counts'])))
    cols = ['record_id', 'section', 'lot_label', 'grave', 'status', 'v2_h_grave', 'lot_h', 'sheet', 'page', 'x', 'y', 'outline', 'cells_in_lot', 'text_pt']
    with open(os.path.join(REPO, 'h-number-map', 'grave_positions_JKM.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, cols); w.writeheader(); w.writerows(allrows)
    return allrows, info
if __name__ == '__main__': run()
