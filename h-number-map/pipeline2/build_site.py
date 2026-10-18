"""Step 9: assemble the interactive site (single HTML file) from the same data the PDFs use."""
import json, os, re, collections
from shapely.geometry import Polygon, MultiPoint
from shapely.ops import unary_union
from common import *
import svgmap

REASON_ORDER = []
def run(pdfs=None):
    if not pdfs:
        pd = os.path.join(REPO, 'h-number-map', 'site', 'pdf'); pdfs = {}
        if os.path.isdir(pd):
            for f in sorted(os.listdir(pd)):
                m = re.match(r'Cedar_Grove_H-Map_(full|overview|area_[A-Z])\.pdf$', f)
                if m: pdfs[m.group(1)] = dict(file='pdf/' + f, name=f)
    D = svgmap.load(); lots = D['lots']; reg = D['reg']; cells = {c['id']: c for c in D['cells']}
    # --- lots (compact rows)
    rows = []
    for o in lots:
        if o['poly']:
            xs = [p[0] for p in o['poly']]; ys = [p[1] for p in o['poly']]; bb = [min(xs), min(ys), max(xs), max(ys)]
        else: bb = [o['cx'] - 3, o['cy'] - 3, o['cx'] + 3, o['cy'] + 3]
        ev = 0 if 'old_ocr_agrees' in o['ev'] else 1
        rows.append([o['d'], o['h'], o['s'], o['l'], o['hn'], o['cx'], o['cy'], *[round(v, 2) for v in bb], ev, 0 if o['poly'] else 1])
    # --- review items
    reasons = []; rv = []
    for r in reg['review']:
        idx = []
        for t in (r.get('reasons') or ['Weak section vote at an area boundary.']):
            if t not in reasons: reasons.append(t)
            idx.append(reasons.index(t))
        b = None
        if r['geom'] == 'outlined' and r['cell'] is not None:
            xs = [p[0] for p in cells[r['cell']]['poly']]; ys = [p[1] for p in cells[r['cell']]['poly']]; b = [round(min(xs), 2), round(min(ys), 2), round(max(xs), 2), round(max(ys), 2)]
        rv.append(dict(x=r['pt'][0], y=r['pt'][1], b=b, t=''.join(r['tokens']), r=idx, s=r.get('section', ''), l=r.get('legacy', ''), h=r.get('htext', ''), c=r.get('cands', [])))
    # --- areas (legacy sections): bbox + hull of verified lots
    areas = {}
    by = collections.defaultdict(list)
    for o in lots: by[o['s']].append(o)
    for s, os_ in by.items():
        pts = [p for o in os_ if o['poly'] for p in o['poly']]
        hull = MultiPoint(pts).convex_hull
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        hn = [o['hn'] for o in os_]
        areas[s] = dict(b=[round(min(xs) - 4, 1), round(min(ys) - 4, 1), round(max(xs) + 4, 1), round(max(ys) + 4, 1)], hull=[[round(x, 1), round(y, 1)] for x, y in hull.exterior.coords][:-1],
                        n=len(os_), hmin=min(hn), hmax=max(hn), nr=0, nu=0, c=[round(sum(o['cx'] for o in os_) / len(os_), 1), round(sum(o['cy'] for o in os_) / len(os_), 1)])
    for r in reg['review']:
        s = r.get('section') or r.get('region')
        if s in areas: areas[s]['nr'] += 1
    unpl = [dict(h=u['htext'], s=u['section'], l=u['legacy'], n=u['note']) for u in reg['known_unplaced']]
    for u in unpl:
        if u['s'] in areas: areas[u['s']]['nu'] += 1
    ann = [[a['t'], a['x'], a['y'], a['fs'], a['a']] for a in D['base']['annotations']]
    bbox = svgmap.content_bbox(D)
    data = dict(lots=rows, review=rv, unplaced=unpl, areas=areas, reasons=reasons, ann=ann, bbox=bbox, pdfs=pdfs or {})
    # --- svg fragments
    lab = svgmap.label_svg(lots)
    labels = ''.join('<g data-bin="%s">%s</g>' % (b, v) for b, v in lab.items())
    tpl = open(os.path.join(HERE, 'site', 'template.html')).read()
    html = (tpl.replace('__BASE__', svgmap.base_svg(D['base'])).replace('__REVIEW__', svgmap.review_svg(D)).replace('__LOTS__', svgmap.lots_svg(lots))
               .replace('__LABELS__', labels).replace('/*__DATA__*/null', json.dumps(data, separators=(',', ':'))))
    dest = os.path.join(REPO, 'h-number-map', 'site', 'index.html')
    open(dest, 'w').write(html)
    print('site', dest, '%.2f MB' % (len(html) / 1e6), 'areas', len(areas), 'review', len(rv), 'unplaced', len(unpl))
if __name__ == '__main__': run()
