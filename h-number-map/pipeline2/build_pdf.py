"""Step 10: vector PDFs from the very same data as the site (base.json via ai_raw.json drawings, lots_fit.json, registry.json).
  * overview sheet  - one 42 x 24 in sheet, whole cemetery
  * detail pages    - tabloid landscape pages at a scale where every number is >= 8 pt; tiles overlap by more than the
                      largest lot, and each lot (outline AND number) is placed on a page that contains it completely
  * one PDF per legacy area, and a full PDF (overview + details + the unresolved-locations appendix)"""
import json, math, os, collections
import pymupdf as fitz
from shapely.geometry import Polygon, box as sbox
from common import *
import svgmap, basemap
from fit import ADV, CAPH, INK_MID

FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'
UI = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
UIB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
NAVY = (12 / 255, 35 / 255, 64 / 255); BG = (251 / 255, 250 / 255, 246 / 255)
def hex2rgb(h): return tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))

class Sheet:
    def __init__(self, doc, w, h, view, margin, top, bottom, parts=('base', 'review', 'labels')):
        self.page = doc.new_page(width=w, height=h); self.view = view; self.parts = parts
        self.mx, self.top, self.bottom = margin, top, bottom
        aw, ah = w - 2 * margin, h - top - bottom
        self.s = min(aw / (view[2] - view[0]), ah / (view[3] - view[1]))
        self.ox = margin + (aw - self.s * (view[2] - view[0])) / 2; self.oy = top + (ah - self.s * (view[3] - view[1])) / 2
        self.clip = fitz.Rect(self.ox, self.oy, self.ox + self.s * (view[2] - view[0]), self.oy + self.s * (view[3] - view[1]))
    def P(self, x, y): return fitz.Point(self.ox + (x - self.view[0]) * self.s, self.oy + (y - self.view[1]) * self.s)

def draw_base(sh, D, raw, only_lines=False):
    pg = sh.page; v = sh.view; pad = 2
    groups = collections.OrderedDict()
    for d in raw['draws']:
        st = basemap.style_for(d)
        if not d['color'] and not d['fill']: continue
        groups.setdefault((st['role'], st['stroke'], st['w'], basemap.blend(d['fill'], .35) if d['fill'] else None), []).append(d)
    order = {'other': 0, 'road': 1, 'garden': 2, 'building': 3, 'lot': 4}
    for (role, stroke, w, fill), ds in sorted(groups.items(), key=lambda kv: order[kv[0][0]]):
        if only_lines and role != 'lot': continue
        shp = pg.new_shape(); n = 0
        for d in ds:
            for it in d['items']:
                xs = it[1::2]; ys = it[2::2]
                if max(xs) < v[0] - pad or min(xs) > v[2] + pad or max(ys) < v[1] - pad or min(ys) > v[3] + pad: continue
                op = it[0]
                if op == 'l': shp.draw_line(sh.P(it[1], it[2]), sh.P(it[3], it[4]))
                elif op == 'c': shp.draw_bezier(sh.P(it[1], it[2]), sh.P(it[3], it[4]), sh.P(it[5], it[6]), sh.P(it[7], it[8]))
                elif op == 're': shp.draw_rect(fitz.Rect(sh.P(it[1], it[2]), sh.P(it[3], it[4])))
                elif op == 'qu': shp.draw_polyline([sh.P(it[1 + 2 * i], it[2 + 2 * i]) for i in range(4)] + [sh.P(it[1], it[2])])
                n += 1
        if n: shp.finish(color=hex2rgb(stroke) if stroke else None, fill=hex2rgb(fill) if fill else None, width=max(0.3, w * 0.45), closePath=False, lineJoin=1)
        if n: shp.commit()

def put_label(sh, o):
    pg = sh.page; fs = o['fs'] * sh.s; n = len(o['d'])
    c = sh.P(o['cx'], o['cy']); w = ADV * n * o['fs'] * sh.s
    p0 = fitz.Point(c.x - w / 2, c.y + INK_MID * fs)           # baseline start, unrotated
    # fitz.Matrix(a) turns clockwise by a degrees on the (y-down) page; the SVG's rotate(ang) is clockwise too
    pg.insert_text(p0, o['d'], fontsize=fs, fontname='dvsmb', fontfile=FONT, color=NAVY, morph=(c, fitz.Matrix(o['ang'])) if abs(o['ang']) > .05 else None)

def draw_review(sh, D, cells):
    pg = sh.page; shp = pg.new_shape(); v = sh.view
    for r in D['reg']['review']:
        if r['geom'] == 'outlined' and r['cell'] is not None:
            poly = cells[r['cell']]['poly']
            if max(p[0] for p in poly) < v[0] or min(p[0] for p in poly) > v[2] or max(p[1] for p in poly) < v[1] or min(p[1] for p in poly) > v[3]: continue
            shp.draw_polyline([sh.P(x, y) for x, y in poly] + [sh.P(*poly[0])])
        else:
            if v[0] <= r['pt'][0] <= v[2] and v[1] <= r['pt'][1] <= v[3]: shp.draw_circle(sh.P(*r['pt']), 1.5 * sh.s)
    shp.finish(color=(201 / 255, 137 / 255, 47 / 255), fill=(244 / 255, 231 / 255, 208 / 255), width=0.5, dashes='[2 1.5] 0', closePath=True); shp.commit()

def frame(sh, title, sub, pageno, total, D, win=None):
    pg = sh.page; W, H = pg.rect.width, pg.rect.height; u = min(W, 1224) / 1224.0
    pg.insert_text((sh.mx, sh.top - 18 * u), title, fontsize=15 * u, fontname='uib', fontfile=UIB, color=NAVY)
    pg.insert_text((sh.mx, sh.top - 5 * u), sub, fontsize=8 * u, fontname='ui', fontfile=UI, color=(.34, .38, .45))
    foot = 'Numbers are H-numbers (H and leading zeros left off; A / B = the two rows of a double-row lot). Amber dashed lots could not be tied to one H-number. Legacy section letters are for cross-reference only.'
    pg.insert_text((sh.mx, H - 14 * u), foot, fontsize=7 * u, fontname='ui', fontfile=UI, color=(.34, .38, .45))
    pg.insert_text((W - sh.mx - 70 * u, H - 14 * u), 'Page %d of %d' % (pageno, total), fontsize=7.5 * u, fontname='ui', fontfile=UI, color=(.34, .38, .45))
    if win:     # index map
        bb = svgmap.content_bbox(D); iw = 120 * u; ih = iw * (bb[3] - bb[1]) / (bb[2] - bb[0]); ix, iy = W - sh.mx - iw, 14 * u
        k = iw / (bb[2] - bb[0]); shp = pg.new_shape(); shp.draw_rect(fitz.Rect(ix, iy, ix + iw, iy + ih)); shp.finish(color=(.8, .8, .8), fill=(.97, .97, .95), width=.4); shp.commit()
        r = fitz.Rect(ix + (win[0] - bb[0]) * k, iy + (win[1] - bb[1]) * k, ix + (win[2] - bb[0]) * k, iy + (win[3] - bb[1]) * k) & fitz.Rect(ix, iy, ix + iw, iy + ih)
        shp = pg.new_shape(); shp.draw_rect(r); shp.finish(color=(201 / 255, 137 / 255, 47 / 255), fill=(201 / 255, 137 / 255, 47 / 255), fill_opacity=.35, width=.8); shp.commit()

def tiles(bb, ww, wh, ov):
    xs = []; x = bb[0]
    while True:
        xs.append(x)
        if x + ww >= bb[2]: break
        x += ww - ov
    ys = []; y = bb[1]
    while True:
        ys.append(y)
        if y + wh >= bb[3]: break
        y += wh - ov
    return [(x, y, x + ww, y + wh) for y in ys for x in xs]

def build_doc(D, raw, cells, area=None, parts=('base', 'review', 'labels'), with_overview=True, appendix=True):
    doc = fitz.open(); lots = D['lots']; bb = svgmap.content_bbox(D)
    sel = [i for i, o in enumerate(lots) if area is None or o['s'] == area]
    ab = bb
    if area:
        xs = [p[0] for i in sel for p in lots[i]['poly'] or []]; ys = [p[1] for i in sel for p in lots[i]['poly'] or []]
        ab = [min(xs) - 6, min(ys) - 6, max(xs) + 6, max(ys) + 6]
    S = 3.1                                   # pt per drawing unit on detail pages (a 4-unit number = 12 pt)
    W, H, M, T, B = 1224, 792, 36, 54, 30
    ww, wh = (W - 2 * M) / S, (H - T - B) / S
    maxdim = max(max(o['poly'][k][0] for k in range(len(o['poly']))) - min(p[0] for p in o['poly']) for o in lots if o['poly'])
    maxdim = max(maxdim, max(max(p[1] for p in o['poly']) - min(p[1] for p in o['poly']) for o in lots if o['poly']))
    ov = maxdim + 3
    wins = tiles(ab, ww, wh, ov)
    # assign every selected lot to the first window that holds it completely
    own = collections.defaultdict(list); lost = []
    for i in sel:
        o = lots[i]
        if not o['poly']:
            b = [o['cx'] - 3, o['cy'] - 3, o['cx'] + 3, o['cy'] + 3]
        else:
            xs = [p[0] for p in o['poly']]; ys = [p[1] for p in o['poly']]; b = [min(xs), min(ys), max(xs), max(ys)]
        for k, w in enumerate(wins):
            if b[0] >= w[0] + 0.5 and b[2] <= w[2] - 0.5 and b[1] >= w[1] + 0.5 and b[3] <= w[3] - 0.5: own[k].append(i); break
        else: lost.append(i)
    used = [k for k in range(len(wins)) if own[k]]
    total = (1 if with_overview else 0) + len(used) + (3 if appendix else 0)
    page_of = {}
    if with_overview:
        OW, OH = 3024, 1728; sh = Sheet(doc, OW, OH, bb, 40, 70, 34, parts)
        sh.page.draw_rect(sh.page.rect, fill=BG, color=None)
        if 'base' in parts: draw_base(sh, D, raw, only_lines='lines' in parts)
        if 'review' in parts: draw_review(sh, D, cells)
        if 'labels' in parts:
            for i in range(len(lots)):
                o = lots[i]
                if o['fs'] and o['fs'] * sh.s >= 6.5: put_label(sh, o)
        frame(sh, 'Cedar Grove Cemetery - H-Map, overview', 'Whole cemetery on one 42 x 24 in sheet. Numbers appear where they are large enough to read; detail pages show every number.', 1, total, D)
    for n, k in enumerate(used):
        w = wins[k]; sh = Sheet(doc, W, H, w, M, T, B, parts); sh.page.draw_rect(sh.page.rect, fill=BG, color=None)
        if 'base' in parts: draw_base(sh, D, raw, only_lines='lines' in parts)
        if 'review' in parts: draw_review(sh, D, cells)
        if 'labels' in parts:
            for i in own[k]:
                if lots[i]['fs']: put_label(sh, lots[i]); page_of[lots[i]['h']] = n + 1 + (1 if with_overview else 0)
        ttl = 'Cedar Grove Cemetery - H-Map' + (', legacy section %s' % area if area else ', detail')
        frame(sh, ttl, 'Detail page %d of %d. A lot cut by the page edge is numbered on the neighbouring page that shows it whole.' % (n + 1, len(used)), n + 1 + (1 if with_overview else 0), total, D, w)
    return doc, dict(pages=len(used), lost=lost, ov=ov, page_of=page_of, windows=[wins[k] for k in used], owners=[own[k] for k in used], scale=S)

def appendix_pages(doc, D, page_of):
    reg = D['reg']; W, H = 792, 612; rows = []
    for r in reg['review']:
        rows.append(('To review', ''.join(r['tokens']) or '(no label)', r.get('htext', ''), (r.get('section', '') + ' ' + r.get('legacy', '')).strip(), '; '.join(r.get('reasons', [])[:1]), '(%d, %d)' % tuple(r['pt'])))
    for u in reg['known_unplaced']:
        rows.append(('No map position', '', u['htext'], '%s %s' % (u['section'], u['legacy']), u['note'] or 'No label on the drawing resolves to this decoder lot', ''))
    per = 38; n = 0
    for st in range(0, len(rows), per):
        pg = doc.new_page(width=W, height=H); n += 1
        pg.insert_text((36, 40), 'Unresolved locations (%d to %d of %d)' % (st + 1, min(len(rows), st + per), len(rows)), fontsize=14, fontname='uib', fontfile=UIB, color=NAVY)
        pg.insert_text((36, 54), 'Nothing here is drawn as an H-number. Candidates are decoder results only. Map position (x, y) is in drawing units.', fontsize=7.5, fontname='ui', fontfile=UI, color=(.34, .38, .45))
        y = 76; cols = [36, 120, 220, 300, 380, 700]
        for c, t in zip(cols, ['Kind', 'Label on drawing', 'H-number candidate', 'Legacy', 'Reason', 'Position']): pg.insert_text((c, y), t, fontsize=7.5, fontname='uib', fontfile=UIB, color=NAVY)
        y += 8
        for r in rows[st:st + per]:
            y += 13
            for c, t, mx in zip(cols, r, [14, 16, 16, 16, 62, 14]): pg.insert_text((c, y), str(t)[:mx * 1 + 40 if mx > 20 else 24] if False else str(t)[:(mx if mx > 20 else 24)] if False else str(t)[:70 if c == 380 else 22], fontsize=7, fontname='ui', fontfile=UI, color=(.1, .12, .18))
    return n

def run():
    D = svgmap.load(); raw = json.load(open(f'{DATA}/ai_raw.json')); cells = {c['id']: c for c in D['cells']}
    pdir = os.path.join(REPO, 'h-number-map', 'site', 'pdf'); os.makedirs(pdir, exist_ok=True)
    out = {}
    # full
    doc, info = build_doc(D, raw, cells)
    assert not info['lost'], 'lots that fit no page: %s' % info['lost'][:5]
    appendix_pages(doc, D, info['page_of'])
    f = 'Cedar_Grove_H-Map_full.pdf'; doc.save(os.path.join(pdir, f), garbage=3, deflate=True); out['full'] = dict(file='pdf/' + f, name=f)
    print('full: %d detail pages, overlap %.1f units, %.1f MB' % (info['pages'], info['ov'], os.path.getsize(os.path.join(pdir, f)) / 1e6))
    ov = fitz.open(); ov.insert_pdf(doc, from_page=0, to_page=0); f2 = 'Cedar_Grove_H-Map_overview.pdf'; ov.save(os.path.join(pdir, f2), garbage=3, deflate=True)
    out['overview'] = dict(file='pdf/' + f2, name=f2)
    for s in sorted({o['s'] for o in D['lots']}):
        d2, i2 = build_doc(D, raw, cells, area=s, with_overview=False, appendix=False)
        assert not i2['lost']
        f3 = 'Cedar_Grove_H-Map_area_%s.pdf' % s; d2.save(os.path.join(pdir, f3), garbage=3, deflate=True); out['area_' + s] = dict(file='pdf/' + f3, name=f3)
    json.dump(dict(pages=info['pages'], windows=info['windows'], page_of=info['page_of']), open(f'{DATA}/pdf_layout.json', 'w'))
    return out
if __name__ == '__main__': print(run())
