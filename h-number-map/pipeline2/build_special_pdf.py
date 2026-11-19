"""Step 9c: detail sheets for the two native numbering systems (data/special_areas.json, from special_areas.py) and special_locations.csv.

  page 1  the mausoleum crypt courts, every crypt number 1-68 in its cell
  page 2  the cremains strip, every niche number 1-80 in its cell

    python3 build_special_pdf.py   -> site/pdf/Cedar_Grove_Crypts_and_Cremains_detail.pdf and h-number-map/special_locations.csv"""
import json, os, csv
import pymupdf as fitz
from common import *
import build_pdf as B, svgmap
from special_areas import build as build_special

def draw_cells(sh, items, size_fn, color):
    pg = sh.page; shp = pg.new_shape()
    for it in items:
        if it['poly']: shp.draw_polyline([sh.P(x, y) for x, y in it['poly']] + [sh.P(*it['poly'][0])])
    shp.finish(color=(.25, .3, .38), fill=color, width=.7, closePath=True, lineJoin=1); shp.commit()
    nm = pg.new_shape()                                          # cell outline not traced: nominal box, dashed
    for it in items:
        if not it['poly'] and it.get('nominal_poly'): nm.draw_polyline([sh.P(x, y) for x, y in it['nominal_poly']] + [sh.P(*it['nominal_poly'][0])])
    nm.finish(color=(.4, .45, .55), fill=color, width=.7, dashes='[2 1.5] 0', closePath=True); nm.commit()
    for it in items:
        s = str(it['n']); fs = size_fn(it); c = sh.P(it['x'], it['y'])
        w = fitz.get_text_length(s, fontname='helv', fontsize=fs) * 1.12
        rot = it.get('rot', 0)
        p0 = fitz.Point(c.x - w / 2, c.y + 0.36 * fs)
        pg.insert_text(p0, s, fontsize=fs, fontname='dvsmb', fontfile=B.FONT, color=B.NAVY, morph=(c, fitz.Matrix(rot)) if rot else None)

def sheet(doc, W, Hh, view, title, sub, items, size_fn, color, D, raw, note):
    sh = B.Sheet(doc, W, Hh, view, 36, 74, 50); pg = sh.page; pg.draw_rect(pg.rect, fill=B.BG, color=None)
    B.draw_base(sh, D, raw, skip_lots=True)
    shp = pg.new_shape()                                        # neighbouring lots, light, for orientation
    for o in D['lots']:
        if o['poly'] and view[0] - 6 < o['cx'] < view[2] + 6 and view[1] - 6 < o['cy'] < view[3] + 6:
            shp.draw_polyline([sh.P(x, y) for x, y in o['poly']] + [sh.P(*o['poly'][0])])
    shp.finish(color=(.72, .74, .78), fill=(.95, .95, .92), width=.4, closePath=True); shp.commit()
    draw_cells(sh, items, size_fn, color)
    pg.clip_to_rect(sh.clip)
    s2 = pg.new_shape(); s2.draw_rect(sh.clip); s2.finish(color=(.62, .64, .68), width=.8); s2.commit()
    pg.insert_text((36, 36), title, fontsize=24, fontname='uib', fontfile=B.UIB, color=B.NAVY)
    pg.insert_text((36, 54), sub, fontsize=9.5, fontname='ui', fontfile=B.UI, color=(.34, .38, .45))
    pg.insert_text((36, Hh - 20), note, fontsize=8.5, fontname='ui', fontfile=B.UI, color=(.34, .38, .45))
    return sh

def run():
    S = build_special(); D = svgmap.load(); raw = json.load(open(f'{DATA}/ai_raw.json'))
    cr = [i for i in S['items'] if i['kind'] == 'crypt']; ni = [i for i in S['items'] if i['kind'] == 'niche']
    for i in cr: i['rot'] = 0
    for i in ni: i['rot'] = 90 if i['n'] >= 10 else 0
    doc = fitz.open()
    sheet(doc, 792, 1224, [552, 296, 628, 422], 'Mausoleum crypts 1 to 68', 'Cedar Grove Cemetery · not part of the H-numbering · south court 1-25, north court 26-50, row north of the north court 51-68',
          cr, lambda i: 10 if i['n'] <= 50 else 9, (.86, .9, .95), D, raw,
          'Crypt numbers are the native numbers written on the drawing. Dashed boxes: no cell outline was traced, the box is nominal. 59, 60, 65, 66 have no label either: position interpolated between neighbours.')
    sheet(doc, 1224, 792, [818, 343, 993, 373], 'Cremains niches 1 to 80', 'Cedar Grove Cemetery · not part of the H-numbering · niche 1 is at the east end, niche 80 at the west end',
          ni, lambda i: 9.5 if i['n'] >= 10 else 10, (.93, .88, .8), D, raw,
          'The drawing writes every fifth number (1, 5, 10 ... 80); the others are counted from the labelled niches. Niches 1-9 are the nine small tilted cells at the east end.')
    dest = os.path.join(REPO, 'h-number-map', 'site', 'pdf', 'Cedar_Grove_Crypts_and_Cremains_detail.pdf'); os.makedirs(os.path.dirname(dest), exist_ok=True)
    doc.save(dest, garbage=3, deflate=True)
    with open(os.path.join(REPO, 'h-number-map', 'special_locations.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['id', 'name', 'area', 'map_x', 'map_y', 'how_established', 'confidence'])
        for i in S['items']: w.writerow([i['id'], i['name'], i['court'], i['x'], i['y'], i['how'], i['confidence']])
    print('wrote', dest, 'and special_locations.csv with', len(S['items']), 'rows')
if __name__ == '__main__': run()
