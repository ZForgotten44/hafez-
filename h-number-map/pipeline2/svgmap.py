"""Step 7: compose the map layers as SVG fragments.  The interactive site and the QA renders use exactly these
fragments, and the PDF builder reads the same JSON, so every output shows the same geometry and label placement."""
import json, math
from common import *
from fit import ADV, CAPH, INK_MID

def pts(poly): return ' '.join('%.2f,%.2f' % (x, y) for x, y in poly)

def load():
    return dict(base=json.load(open(f'{DATA}/base.json')), lots=json.load(open(f'{DATA}/lots_fit.json')),
                reg=json.load(open(f'{DATA}/registry.json')), cells=json.load(open(f'{DATA}/cells.json')))

def base_svg(base):
    out = []
    for l in base['layers']:
        a = ' fill="%s"' % (l['fill'] or 'none')
        if l['stroke']: a += ' stroke="%s" stroke-width="%s"' % (l['stroke'], l['w'])
        out.append('<path class="b-%s"%s vector-effect="non-scaling-stroke" d="%s"/>' % (l['role'], a, l['d']))
    return ''.join(out)

def review_svg(D):
    cells = {c['id']: c for c in D['cells']}; out = []
    for i, r in enumerate(D['reg']['review']):
        if r['geom'] == 'outlined' and r['cell'] is not None:
            out.append('<polygon class="rv" data-r="%d" points="%s"/>' % (i, pts(cells[r['cell']]['poly'])))
        else:
            out.append('<circle class="rv-dot" data-r="%d" cx="%.2f" cy="%.2f" r="1.5"/>' % (i, r['pt'][0], r['pt'][1]))
    return ''.join(out)

def lots_svg(lots):
    out = []
    for i, o in enumerate(lots):
        if o['poly']: out.append('<polygon class="lot" data-i="%d" points="%s"/>' % (i, pts(o['poly'])))
        else: out.append('<circle class="lot lot-pt" data-i="%d" cx="%.2f" cy="%.2f" r="2.6"/>' % (i, o['cx'], o['cy']))
    return ''.join(out)

def label_svg(lots, bins=((4.0, 'b1'), (3.0, 'b2'), (0, 'b3'))):
    g = {b: [] for _, b in bins}
    for i, o in enumerate(lots):
        if not o['fs']: continue
        b = next(n for lim, n in bins if o['fs'] >= lim)
        w = ADV * len(o['d']) * o['fs']
        g[b].append('<text data-i="%d" transform="translate(%.2f %.2f) rotate(%.1f)" font-size="%.2f" textLength="%.2f" dy="%.3fem">%s</text>'
                    % (i, o["cx"], o["cy"], o["ang"], o["fs"], w, INK_MID, o["d"]))
    return {b: ''.join(v) for b, v in g.items()}

def content_bbox(D, pad=14):
    xs, ys = [], []
    for o in D['lots']:
        if o['poly']:
            for x, y in o['poly']: xs.append(x); ys.append(y)
    return [min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad]

STYLE = '''
.b-lot{stroke-linejoin:round} .rv{fill:#f1dcc0;fill-opacity:.45;stroke:#c9892f;stroke-opacity:.8;stroke-width:1;stroke-dasharray:3 2;vector-effect:non-scaling-stroke}
.rv-dot{fill:none;stroke:#c9892f;stroke-width:1;vector-effect:non-scaling-stroke}
.lot{fill:#fff;fill-opacity:0;stroke:none}
text{font-family:'DejaVu Sans Mono','DM Mono',ui-monospace,Menlo,Consolas,monospace;font-weight:700;fill:#0c2340;text-anchor:middle;lengthAdjust:spacingAndGlyphs}
'''

def static_svg(D, view=None, labels=True):
    bb = view or content_bbox(D)
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    L = label_svg(D['lots'])
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="%.2f %.2f %.2f %.2f" width="%d" height="%d"><style>%s</style>'
            '<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="#fbfaf6"/><g id="base">%s</g><g id="review">%s</g><g id="labels">%s</g></svg>'
            % (bb[0], bb[1], w, h, int(w * 6), int(h * 6), STYLE, bb[0], bb[1], w, h, base_svg(D['base']), review_svg(D), ''.join(L.values()) if labels else ''))
