"""Step 10: vector PDFs from the very same data as the site (base.json via ai_raw.json drawings, lots_fit.json, registry.json).
  * overview sheet  - one 42 x 24 in sheet, whole cemetery
  * detail pages    - tabloid landscape pages at a scale where every number is >= 8 pt; tiles overlap by more than the
                      largest lot, and each lot (outline AND number) is placed on a page that contains it completely
  * one PDF per section, each on a single page, and a full PDF (overview + details + the unresolved-locations appendix)"""
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

def draw_base(sh, D, raw, only_lines=False, skip_lots=False):
    pg = sh.page; v = sh.view; pad = 2
    groups = collections.OrderedDict()
    for d in raw['draws']:
        st = basemap.style_for(d)
        if not d['color'] and not d['fill']: continue
        groups.setdefault((st['role'], st['stroke'], st['w'], basemap.blend(d['fill'], .35) if d['fill'] else None), []).append(d)
    order = {'other': 0, 'road': 1, 'garden': 2, 'building': 3, 'lot': 4}
    for (role, stroke, w, fill), ds in sorted(groups.items(), key=lambda kv: order[kv[0][0]]):
        if only_lines and role != 'lot': continue
        if skip_lots and role == 'lot': continue
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

TEAL = (44 / 255, 125 / 255, 160 / 255); TEAL_FILL = (207 / 255, 228 / 255, 238 / 255); TEAL_INK = (29 / 255, 95 / 255, 125 / 255)

def draw_review(sh, D, cells, only=None):
    """open lots in amber dashes; lots whose number is inferred from the path in teal, with their proposed number written inside"""
    pg = sh.page; v = sh.view; amber = pg.new_shape(); teal = pg.new_shape(); texts = []
    for i, r in enumerate(D['reg']['review']):
        pv = D['pvmap'].get(i); prov = bool(pv and pv['status'] == 'provisional')
        sec = pv['prop']['section'] if prov else (r.get('section') or r.get('region'))
        if only and sec != only: continue
        shp = teal if prov else amber
        if r['geom'] == 'outlined' and r['cell'] is not None:
            poly = cells[r['cell']]['poly']
            if max(p[0] for p in poly) < v[0] or min(p[0] for p in poly) > v[2] or max(p[1] for p in poly) < v[1] or min(p[1] for p in poly) > v[3]: continue
            shp.draw_polyline([sh.P(x, y) for x, y in poly] + [sh.P(*poly[0])])
            if prov:
                xs = [p[0] for p in poly]; ys = [p[1] for p in poly]; d = pv['prop']['htext'][1:].lstrip('0') or '0'
                fs = min(4.0, 0.8 * (max(xs) - min(xs)) / (ADV * len(d)), 0.7 * (max(ys) - min(ys)))
                if fs >= 1.6: texts.append((d, (sum(xs) / len(xs), sum(ys) / len(ys)), fs))
        else:
            if v[0] <= r['pt'][0] <= v[2] and v[1] <= r['pt'][1] <= v[3]: shp.draw_circle(sh.P(*r['pt']), 1.5 * sh.s)
    amber.finish(color=(201 / 255, 137 / 255, 47 / 255), fill=(244 / 255, 231 / 255, 208 / 255), width=0.5, dashes='[2 1.5] 0', closePath=True); amber.commit()
    teal.finish(color=TEAL, fill=TEAL_FILL, width=0.6, closePath=True); teal.commit()
    for d, (cx, cy), fs in texts:
        f = fs * sh.s; c = sh.P(cx, cy); w = ADV * len(d) * f
        pg.insert_text(fitz.Point(c.x - w / 2, c.y + INK_MID * f), d, fontsize=f, fontname='dvsmb', fontfile=FONT, color=TEAL_INK)

def frame(sh, title, sub, pageno, total, D, win=None):
    pg = sh.page; W, H = pg.rect.width, pg.rect.height; u = min(W, 1224) / 1224.0
    pg.insert_text((sh.mx, sh.top - 18 * u), title, fontsize=15 * u, fontname='uib', fontfile=UIB, color=NAVY)
    pg.insert_text((sh.mx, sh.top - 5 * u), sub, fontsize=8 * u, fontname='ui', fontfile=UI, color=(.34, .38, .45))
    foot = 'Numbers are H-numbers (H and leading zeros left off; A / B = the two rows of a double-row lot). Amber dashed = could not be tied to one H-number. Blue = number inferred from the path, please confirm.'
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
                if o['fs'] and o['fs'] * sh.s >= 5.0: put_label(sh, o)
        st = section_stats(D); from shapely.strtree import STRtree
        polys = [Polygon(o['poly']) for o in lots if o['poly'] and len(o['poly']) > 2]; tree = STRtree(polys); placed = []
        for sec, e in sorted(st.items()):
            txt, sub = 'Section %s' % sec, '%s to %s' % (fmtH(e['hmin']), fmtH(e['hmax'])); big = 22
            bw = max(fitz.get_text_length(txt, fontname='helv', fontsize=big) * 1.12, fitz.get_text_length(sub, fontname='helv', fontsize=big * .46)) + big * .9
            wu, hu = bw / sh.s, big * 1.75 / sh.s; b = e['b']; cx0, cy0 = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2; g = 3
            cands = [(cx0, b[1] - g - hu / 2), (cx0, b[3] + g + hu / 2), (b[0] - g - wu / 2, cy0), (b[2] + g + wu / 2, cy0), (b[0] + wu / 2, b[1] - g - hu / 2), (b[2] - wu / 2, b[1] - g - hu / 2),
                     (b[0] + wu / 2, b[3] + g + hu / 2), (b[2] - wu / 2, b[3] + g + hu / 2), (cx0, cy0)]
            def cost(c):
                r = sbox(c[0] - wu / 2, c[1] - hu / 2, c[0] + wu / 2, c[1] + hu / 2)
                n = len(tree.query(r, predicate='intersects')) + 5 * sum(r.intersects(q) for q in placed)
                return n + (0 if bb[0] < c[0] < bb[2] and bb[1] < c[1] < bb[3] else 9)
            c = min(cands, key=cost); placed.append(sbox(c[0] - wu / 2, c[1] - hu / 2, c[0] + wu / 2, c[1] + hu / 2))
            p = sh.P(*c); section_tag(sh, txt, sub, p.x, p.y, big)
        frame(sh, 'Cedar Grove Cemetery - H-Map, overview', 'Whole cemetery on one 42 x 24 in sheet. Numbers appear where they are large enough to read; detail pages show every number.', 1, total, D)
    for n, k in enumerate(used):
        w = wins[k]; sh = Sheet(doc, W, H, w, M, T, B, parts); sh.page.draw_rect(sh.page.rect, fill=BG, color=None)
        # roads, buildings and context are clipped to the window; lot outlines are drawn only for the lots this page owns, so no lot is ever shown half-cut
        if 'base' in parts: draw_base(sh, D, raw, only_lines='lines' in parts, skip_lots=True)
        shp = sh.page.new_shape()
        for i in own[k]:
            if lots[i]['poly']: shp.draw_polyline([sh.P(x, y) for x, y in lots[i]['poly']] + [sh.P(*lots[i]['poly'][0])])
        shp.finish(color=(.25, .3, .38), width=.45, closePath=True, lineJoin=1); shp.commit()
        if 'review' in parts: draw_review(sh, D, cells)
        if 'labels' in parts:
            for i in own[k]:
                if lots[i]['fs']: put_label(sh, lots[i]); page_of[lots[i]['h']] = n + 1 + (1 if with_overview else 0)
        sh.page.clip_to_rect(sh.clip)
        ttl = 'Cedar Grove Cemetery - H-Map' + (', Section %s' % area if area else ', detail')
        secs = sorted({lots[i]['s'] for i in own[k]})
        frame(sh, ttl, 'Detail page %d of %d · Section %s on this page. Each lot is drawn whole on exactly one page: a lot the page edge would cut appears on the neighbouring page.' % (n + 1, len(used), ', '.join(secs)), n + 1 + (1 if with_overview else 0), total, D, w)
    return doc, dict(pages=len(used), lost=lost, ov=ov, page_of=page_of, windows=[wins[k] for k in used], owners=[own[k] for k in used], scale=S)

def appendix_pages(doc, D, page_of):
    reg = D['reg']; W, H = 792, 612; rows = []
    taken = {i['prop']['hnum'] for i in D['pv']['items'] if i['status'] == 'provisional'}
    for ri, r in enumerate(reg['review']):
        pv = D['pvmap'].get(ri)
        if pv and pv['status'] == 'provisional':
            rows.append(('Inferred (confirm)', ''.join(r['tokens']) or '(no label)', pv['prop']['htext'], '%s %s' % (pv['prop']['section'], pv['prop']['label']), '%s confidence. %s' % (pv['conf'], pv['reason']), '(%d, %d)' % tuple(r['pt'])))
        else:
            rows.append(('To review', ''.join(r['tokens']) or '(no label)', r.get('htext', ''), (r.get('section', '') + ' ' + r.get('legacy', '')).strip(), (pv['reason'] if pv else '; '.join(r.get('reasons', [])[:1])), '(%d, %d)' % tuple(r['pt'])))
    for u in reg['known_unplaced']:
        if u['hnum'] in taken: continue
        rows.append(('No map position', '', u['htext'], '%s %s' % (u['section'], u['legacy']), u['note'] or 'No label on the drawing resolves to this decoder lot', ''))
    per = 38; n = 0
    for st in range(0, len(rows), per):
        pg = doc.new_page(width=W, height=H); n += 1
        pg.insert_text((36, 40), 'Unresolved locations (%d to %d of %d)' % (st + 1, min(len(rows), st + per), len(rows)), fontsize=14, fontname='uib', fontfile=UIB, color=NAVY)
        pg.insert_text((36, 54), 'Nothing here is verified. Inferred rows come from the path and need a yes or no. Map position (x, y) is in drawing units.', fontsize=7.5, fontname='ui', fontfile=UI, color=(.34, .38, .45))
        y = 76; cols = [36, 120, 220, 300, 380, 700]
        for c, t in zip(cols, ['Kind', 'Label on drawing', 'H-number candidate', 'Section / lot', 'Reason', 'Position']): pg.insert_text((c, y), t, fontsize=7.5, fontname='uib', fontfile=UIB, color=NAVY)
        y += 8
        for r in rows[st:st + per]:
            y += 13
            for c, t, mx in zip(cols, r, [14, 16, 16, 16, 62, 14]): pg.insert_text((c, y), str(t)[:mx * 1 + 40 if mx > 20 else 24] if False else str(t)[:(mx if mx > 20 else 24)] if False else str(t)[:70 if c == 380 else 22], fontsize=7, fontname='ui', fontfile=UI, color=(.1, .12, .18))
    return n

def section_stats(D):
    """bbox / H range / lot count per section, from the lots that have outlines (label-only lots widen the box a little)."""
    st = {}
    for o in D['lots']:
        e = st.setdefault(o['s'], dict(b=[1e9, 1e9, -1e9, -1e9], hmin=10 ** 9, hmax=0, n=0))
        pts = o['poly'] or [(o['cx'] - 3, o['cy'] - 3), (o['cx'] + 3, o['cy'] + 3)]
        for x, y in pts:
            e['b'][0] = min(e['b'][0], x); e['b'][1] = min(e['b'][1], y); e['b'][2] = max(e['b'][2], x); e['b'][3] = max(e['b'][3], y)
        e['hmin'] = min(e['hmin'], o['hn']); e['hmax'] = max(e['hmax'], o['hn']); e['n'] += 1
    return st

def fmtH(n): return 'H%06d' % n

def section_tag(sh, text, sub, x, y, big):
    """a rounded label with the section name and its H range, centred on (x, y) in page points"""
    pg = sh.page; w = max(fitz.get_text_length(text, 'uib', fontsize=big) if False else 0, 0)
    tw = fitz.get_text_length(text, fontname='helv', fontsize=big) * 1.12; sw = fitz.get_text_length(sub, fontname='helv', fontsize=big * .46)
    bw = max(tw, sw) + big * .9; bh = big * 1.75
    r = fitz.Rect(x - bw / 2, y - bh / 2, x + bw / 2, y + bh / 2)
    shp = pg.new_shape(); shp.draw_rect(r, radius=.25); shp.finish(color=NAVY, fill=(1, 1, 1), fill_opacity=.88, width=max(.6, big * .05)); shp.commit()
    pg.insert_text((x - tw / 2 / 1.12, y - big * .05), text, fontsize=big, fontname='uib', fontfile=UIB, color=NAVY)
    pg.insert_text((x - sw / 2, y + big * .62), sub, fontsize=big * .46, fontname='ui', fontfile=UI, color=(.34, .38, .45))

def build_area_pdf(D, raw, cells, area, st):
    """One page per section: every lot, outline and number inside the margins, nothing cut. The page size and orientation are chosen
    from the section's shape (the smallest sheet that keeps numbers at 3 pt per map unit or more, else tabloid at the best fit);
    the map is clipped to the section's own window so neighbouring lots never appear half-cut."""
    lots = D['lots']; e = st[area]; pad = 7
    ab = [e['b'][0] - pad, e['b'][1] - pad, e['b'][2] + pad, e['b'][3] + pad]
    w, h = ab[2] - ab[0], ab[3] - ab[1]; M, T, B = 36, 66, 46
    sizes = [(612, 792), (792, 612), (792, 1224), (1224, 792)]
    def scale(sz): return min((sz[0] - 2 * M) / w, (sz[1] - T - B) / h)
    pick = next((sz for sz in sizes if scale(sz) >= 3.0), None) or max(sizes[2:], key=scale)
    W, H = pick
    doc = fitz.open()
    sh = Sheet(doc, W, H, ab, M, T, B); sh.page.draw_rect(sh.page.rect, fill=BG, color=None)
    draw_base(sh, D, raw, skip_lots=True)
    # own lot outlines (the base layer's lot lines are not drawn, so neighbouring sections never show half a lot)
    shp = sh.page.new_shape()
    for o in lots:
        if o['s'] != area or not o['poly']: continue
        shp.draw_polyline([sh.P(x, y) for x, y in o['poly']] + [sh.P(*o['poly'][0])])
    shp.finish(color=(.25, .3, .38), width=.45, closePath=True, lineJoin=1); shp.commit()
    draw_review(sh, D, cells, only=area)
    for o in lots:
        if o['s'] == area and o['fs']: put_label(sh, o)
    page = sh.page; page.clip_to_rect(sh.clip)
    shp = page.new_shape(); shp.draw_rect(sh.clip); shp.finish(color=(.62, .64, .68), width=.6, fill=None); shp.commit()
    u = min(W, 1224) / 1224.0
    page.insert_text((M, 34), 'Section %s' % area, fontsize=26, fontname='uib', fontfile=UIB, color=NAVY)
    page.insert_text((M, 50), 'Cedar Grove Cemetery · %s to %s · %d lots · one page, drawn to fit (print at any size)' % (fmtH(e['hmin']), fmtH(e['hmax']), e['n']), fontsize=8.5, fontname='ui', fontfile=UI, color=(.34, .38, .45))
    # key
    ky = H - 22; x = M
    page.insert_text((x, ky + 3.5), '12', fontsize=9, fontname='dvsmb', fontfile=FONT, color=NAVY); x += 18
    page.insert_text((x, ky + 3.5), '= H-number, H and leading zeros left off (A / B = the two rows of a double-row lot)', fontsize=7.5, fontname='ui', fontfile=UI, color=(.34, .38, .45)); x += 330
    shp = page.new_shape(); shp.draw_rect(fitz.Rect(x, ky - 3, x + 13, ky + 6)); shp.finish(color=(201 / 255, 137 / 255, 47 / 255), fill=(244 / 255, 231 / 255, 208 / 255), width=.6, dashes='[2 1.5] 0'); shp.commit()
    page.insert_text((x + 18, ky + 3.5), '= to review: could not be tied to one H-number', fontsize=7.5, fontname='ui', fontfile=UI, color=(.34, .38, .45)); x += 250
    shp = page.new_shape(); shp.draw_rect(fitz.Rect(x, ky - 3, x + 13, ky + 6)); shp.finish(color=TEAL, fill=TEAL_FILL, width=.6); shp.commit()
    page.insert_text((x + 18, ky + 3.5), '= number inferred from the path, please confirm', fontsize=7.5, fontname='ui', fontfile=UI, color=(.34, .38, .45))
    page.insert_text((M, H - 8), 'Source: Cedar Grove Ground Maps drawing. Positions follow the drawing, which is marked "not to scale".', fontsize=6.5, fontname='ui', fontfile=UI, color=(.5, .52, .56))
    bb = svgmap.content_bbox(D); iw = 110; ih = iw * (bb[3] - bb[1]) / (bb[2] - bb[0]); ix, iy = W - M - iw, 14
    k = iw / (bb[2] - bb[0]); shp = page.new_shape(); shp.draw_rect(fitz.Rect(ix, iy, ix + iw, iy + ih)); shp.finish(color=(.8, .8, .8), fill=(.97, .97, .95), width=.4); shp.commit()
    for s2, e2 in st.items():
        r = fitz.Rect(ix + (e2['b'][0] - bb[0]) * k, iy + (e2['b'][1] - bb[1]) * k, ix + (e2['b'][2] - bb[0]) * k, iy + (e2['b'][3] - bb[1]) * k)
        shp = page.new_shape(); shp.draw_rect(r); on = s2 == area
        shp.finish(color=(201 / 255, 137 / 255, 47 / 255) if on else (.75, .75, .75), fill=(201 / 255, 137 / 255, 47 / 255) if on else None, fill_opacity=.45, width=.6 if on else .3); shp.commit()
    return doc, dict(scale=sh.s, size=pick)

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
    st = section_stats(D)
    for s in sorted(st):
        d2, i2 = build_area_pdf(D, raw, cells, s, st); assert len(d2) == 1
        f3 = 'Cedar_Grove_H-Map_area_%s.pdf' % s; d2.save(os.path.join(pdir, f3), garbage=3, deflate=True); out['area_' + s] = dict(file='pdf/' + f3, name=f3)
    json.dump(dict(pages=info['pages'], windows=info['windows'], page_of=info['page_of']), open(f'{DATA}/pdf_layout.json', 'w'))
    return out
if __name__ == '__main__': print(run())
