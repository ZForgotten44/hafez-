"""Step 6: the clean base layer.
Everything physical in the CAD drawing (lot outlines, roads, curbs, mausoleum and building footprints, property lines)
is kept; every text object is left out.  The legacy lot numbers, the mausoleum legend, road names and building names are
text in the source, so they are not part of the base at all - there is nothing to cover up or erase.  Text objects are
exported separately as the optional 'source annotations' layer."""
import json, collections
from common import *

def blend(c, k=0.5):
    return '#%02x%02x%02x' % tuple(int(round((v * (1 - k) + 1.0 * k) * 255)) for v in c)

def style_for(d):
    col = tuple(d['color']) if d['color'] else None
    if col == LOT_COLOR: return dict(role='lot', stroke='#8fa3b8', w=0.9)
    if col is None: return dict(role='other', stroke=None, w=0)
    if col in ((0.7, 0.8, 0.4), (0.8, 0.8, 0.4), (0.8, 0.7, 0.4)): return dict(role='road', stroke='#cdd3b0', w=1.1)
    if col in ((0.8, 0.6, 0.4), (0.6, 0.3, 0.0)): return dict(role='garden', stroke='#d2bd9d', w=0.9)
    if col in ((0.6, 0.0, 0.6), (0.3, 0.0, 0.6)): return dict(role='building', stroke='#bda3c4', w=1.0)
    if col == (0.0, 0.0, 0.0): return dict(role='building', stroke='#a4abb5', w=0.9)
    return dict(role='other', stroke=blend(col, 0.55), w=0.9)

def path_d(items):
    out = []; cur = None
    f = lambda v: ('%.2f' % v).rstrip('0').rstrip('.')
    for it in items:
        op = it[0]
        if op == 'l':
            a, b = (it[1], it[2]), (it[3], it[4])
            if cur != a: out.append('M%s %s' % (f(a[0]), f(a[1])))
            out.append('L%s %s' % (f(b[0]), f(b[1]))); cur = b
        elif op == 'c':
            p = it[1:]
            if cur != (p[0], p[1]): out.append('M%s %s' % (f(p[0]), f(p[1])))
            out.append('C%s %s %s %s %s %s' % tuple(f(v) for v in p[2:])); cur = (p[6], p[7])
        elif op == 're':
            x0, y0, x1, y1 = it[1:]; out.append('M%s %sH%sV%sH%sZ' % (f(x0), f(y0), f(x1), f(y1), f(x0))); cur = None
        elif op == 'qu':
            p = it[1:]; out.append('M%s %sL%s %sL%s %sL%s %sZ' % tuple(f(v) for v in p)); cur = None
    return ''.join(out)

def build():
    D = json.load(open(f'{DATA}/ai_raw.json'))
    groups = collections.OrderedDict()
    # the mausoleum legend is a framed text block: drop its frame and rule along with its text
    lg = [sp for sp in D['spans'] if sp['t'].upper().startswith('MAUSOLEUMS') or sp['t'] in ('Mary Queen of Angels', 'Mary Queen of All Saints', 'Mary Mother of the Church', 'Mary Mother of God')]
    lbox = [min(s['bbox'][0] for s in lg) - 8, min(s['bbox'][1] for s in lg) - 8, max(s['bbox'][2] for s in lg) + 8, max(s['bbox'][3] for s in lg) + 8] if lg else None
    def in_legend(d):
        if not lbox: return False
        xs = [v for it in d['items'] for v in it[1::2]]; ys = [v for it in d['items'] for v in it[2::2]]
        return bool(xs) and min(xs) >= lbox[0] - 12 and max(xs) <= lbox[2] + 48 and min(ys) >= lbox[1] - 12 and max(ys) <= lbox[3] + 48
    dropped = 0
    for d in D['draws']:
        if in_legend(d): dropped += 1; continue
        st = style_for(d); fill = blend(d['fill'], 0.35) if d['fill'] else None
        if not d['color'] and not fill: continue
        if not d['items']: continue
        key = (st['role'], st['stroke'], st['w'], fill)
        groups.setdefault(key, []).append(path_d(d['items']))
    layers = []
    order = {'other': 0, 'road': 1, 'garden': 2, 'building': 3, 'lot': 4}
    for (role, stroke, w, fill), ds in groups.items():
        layers.append(dict(role=role, stroke=stroke, w=w, fill=fill, d=''.join(ds)))
    layers.sort(key=lambda l: order[l['role']])
    # source annotations (optional layer): every text object that is not a lot number
    ann = []
    for s in D['spans']:
        if s['size'] >= 1.3 and not (abs(s['size'] - 2.62) < .05):
            ann.append(dict(t=s['t'], x=s['origin'][0], y=s['origin'][1], fs=s['size'], a=s['ang']))
    json.dump(dict(layers=layers, annotations=ann, page=D['page']), open(f'{DATA}/base.json', 'w'))
    tot = sum(len(l['d']) for l in layers)
    print('legend drawings dropped', dropped); print('base layers', len(layers), 'path bytes', tot, collections.Counter(l['role'] for l in layers), 'annotations', len(ann))
if __name__ == '__main__': build()
