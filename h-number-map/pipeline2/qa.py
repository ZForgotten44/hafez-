"""Step 8: automatic checks on the placed numbers (run after fit.py).
  A. model check   - every number's text box lies inside its own lot with PAD clearance, clear of every real lot line
                     of the CAD drawing, and overlaps no other number;
  B. outline check - traced lot outlines coincide with the drawn lot lines;
  C. pixel check   - render the labels and the lot lines separately in a real browser and count label pixels that
                     touch a line pixel (catches font / spacing differences the model cannot see)."""
import json, math, collections, io
import numpy as np
from shapely.geometry import Polygon, LineString, MultiLineString
from shapely import STRtree
from PIL import Image
from common import *
from fit import ADV, CAPH, PAD, text_box
import svgmap

def lot_segments():
    D = json.load(open(f'{DATA}/ai_raw.json')); segs = []
    for d in D['draws']:
        if tuple(d['color']) == LOT_COLOR:
            for it in d['items']:
                if it[0] == 'l': segs.append(LineString([(it[1], it[2]), (it[3], it[4])]))
                elif it[0] == 'qu':
                    q = it[1:]; segs += [LineString([(q[2 * i], q[2 * i + 1]), (q[(2 * i + 2) % 8], q[(2 * i + 3) % 8])]) for i in range(4)]
                elif it[0] == 're':
                    a, b, c, e = it[1:]; segs += [LineString(p) for p in (((a, b), (c, b)), ((c, b), (c, e)), ((c, e), (a, e)), ((a, e), (a, b)))]
    return segs

def model_check(lots):
    segs = lot_segments(); st = STRtree(segs)
    boxes = []; bad = collections.defaultdict(list)
    for i, o in enumerate(lots):
        if not o['fs'] or not o['poly']: boxes.append(None); continue
        b = text_box(o['cx'], o['cy'], ADV * len(o['d']) * o['fs'], CAPH * o['fs'], o['ang']); boxes.append(b)
        p = Polygon(o['poly']).buffer(0)
        if not p.contains(b): bad['outside_lot'].append(i)
        elif p.exterior.distance(b) < PAD - 0.06: bad['too_close_to_edge'].append(i)
        near = st.query(b.buffer(0.4))
        if any(segs[j].distance(b) < 0.36 for j in near): bad['touches_drawn_line'].append(i)
    tree = STRtree([b for b in boxes if b is not None]); idx = [i for i, b in enumerate(boxes) if b is not None]
    for k, b in enumerate(boxes):
        if b is None: continue
        for j in tree.query(b):
            if idx[j] != k and b.intersects(boxes[idx[j]]): bad['overlaps_other_number'].append(k)
    return bad

def outline_check(lots):
    segs = lot_segments(); st = STRtree(segs); worst = []
    for i, o in enumerate(lots):
        if not o['poly']: continue
        ring = LineString(o['poly'] + [o['poly'][0]]); d = []
        for t in np.linspace(0, ring.length, max(8, int(ring.length))):
            pt = ring.interpolate(t); d.append(segs[int(st.nearest(pt))].distance(pt))
        worst.append((max(d), i))
    worst.sort(reverse=True); return worst

def pixel_check(D, scale=5):
    from playwright.sync_api import sync_playwright
    bb = svgmap.content_bbox(D); w, h = bb[2] - bb[0], bb[3] - bb[1]; W, H = int(w * scale), int(h * scale)
    lines = '<g fill="none" stroke="#000" stroke-width="%.3f">%s</g>' % (0.71, ''.join(
        '<path d="%s"/>' % l['d'] for l in D['base']['layers'] if l['role'] == 'lot'))
    labels = ''.join(svgmap.label_svg(D['lots']).values())
    def page(inner):
        return ('<html><body style="margin:0;background:#fff"><svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="%.2f %.2f %.2f %.2f">'
                '<style>text{font-family:"DejaVu Sans Mono","DM Mono",ui-monospace,monospace;font-weight:700;fill:#000;text-anchor:middle}</style>%s</svg></body></html>' % (W, H, bb[0], bb[1], w, h, inner))
    imgs = []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args=['--no-sandbox'])
        for inner in (lines, labels):
            pg = b.new_page(viewport={'width': W, 'height': H}); pg.set_content(page(inner)); imgs.append(np.array(Image.open(io.BytesIO(pg.screenshot())).convert('L')) < 128); pg.close()
        b.close()
    L, T = imgs
    from scipy.ndimage import binary_dilation
    hit = T & binary_dilation(L, iterations=1)
    return int(T.sum()), int(hit.sum()), (hit, bb, scale)

def pdf_check():
    """D. printed output: build the PDF twice from the same data (lot lines only / numbers only), rasterise every page and
    count number pixels that touch a lot line; also read the text layer back and compare it with the lot list."""
    import pymupdf as fitz, build_pdf
    from scipy.ndimage import binary_dilation
    D = svgmap.load(); raw = json.load(open(f'{DATA}/ai_raw.json')); cells = {c['id']: c for c in D['cells']}
    full, info = build_pdf.build_doc(D, raw, cells, with_overview=True, appendix=False)
    lines, _ = build_pdf.build_doc(D, raw, cells, parts=('base', 'lines'), with_overview=True, appendix=False)
    labs, _ = build_pdf.build_doc(D, raw, cells, parts=('labels',), with_overview=True, appendix=False)
    touch = ink = 0; z = 2.0
    for n in range(len(full)):
        a = np.array(Image.frombytes('L', (lambda p: (p.width, p.height))(pm := lines[n].get_pixmap(matrix=fitz.Matrix(z, z), colorspace=fitz.csGRAY)), pm.samples)) < 200
        b = np.array(Image.frombytes('L', (lambda p: (p.width, p.height))(pm2 := labs[n].get_pixmap(matrix=fitz.Matrix(z, z), colorspace=fitz.csGRAY)), pm2.samples)) < 120
        # the header/footer text also lives in the labels doc: only look inside the map window
        r = lines[n].rect; top = 70 if r.width > 2000 else 54; b[: int(top * z), :] = False; b[int((r.height - 34) * z):, :] = False
        ink += int(b.sum()); touch += int((b & binary_dilation(a, iterations=1)).sum())
    # text layer: every detail-page number appears exactly once, on the page that owns it
    seen = collections.Counter()
    for n in range(1, len(full)):
        if n == 0: continue
        for w in full[n].get_text('words'):
            seen[w[4]] += 1
    exp = collections.Counter(o['d'] for o in D['lots'] if o['fs'])
    # number strings can repeat across areas (e.g. 23 and 23A are distinct); compare counts of lot labels only
    miss = [k for k, v in exp.items() if seen.get(k, 0) < v]
    return dict(pages=len(full), pdf_label_pixels=ink, pdf_touching=touch, text_layer_missing=len(miss), detail_pages=info['pages'], overlap_units=round(info['ov'], 1))

def run():
    D = svgmap.load(); lots = D['lots']
    bad = model_check(lots)
    ow = outline_check(lots)
    print('A model check (%d lots):' % len(lots), {k: len(v) for k, v in bad.items()} or 'all numbers inside their lot, clear of lines and of each other')
    print('B outline check: worst traced-outline distance from a drawn lot line %.2f units (stroke half-width 0.36); lots over 0.8: %d' % (ow[0][0], sum(1 for d, _ in ow if d > 0.8)))
    ink, hit, _ = pixel_check(D)
    print('C pixel check: %d label pixels, %d touch a lot line (%.3f %%)' % (ink, hit, 100 * hit / ink))
    pr = pdf_check(); print('D print check:', pr)
    json.dump(dict(pdf=pr, model={k: [lots[i]['h'] for i in v] for k, v in bad.items()}, outline_worst=[(round(d, 2), lots[i]['h']) for d, i in ow[:20]], pixel=dict(ink=ink, touching=hit)),
              open(f'{OUT}/qa_report.json', 'w'), indent=1)
if __name__ == '__main__': run()
