"""Step 5: place every H-number inside its own lot.

For each verified lot the number is laid out in the lot's *own* frame:
  * interior point  - centre of the largest inscribed circle of the inset outline (not the bounding-box centre, so it
                      stays inside curved / irregular lots),
  * orientation     - along the lot's long axis (or across it, when that lets the number be clearly larger),
                      always reading left-to-right / bottom-to-top, never upside down,
  * size            - the largest font for which the *measured* text box (digits are monospaced, 0.60 em advance and
                      0.72 em tall) lies entirely inside the outline inset by PAD.
Numbers are never clipped and never shrunk below MIN_FS; a lot that cannot hold a legible number is reported."""
import json, math, re, collections
import numpy as np
from shapely.geometry import Polygon, box
from shapely import affinity
from shapely.ops import polylabel
from common import *

ADV, CAPH = 0.60, 0.78      # measured in the browser for the label font: advance 0.60 em, ink height <= 0.77 em
INK_MID = 0.365             # baseline offset (em) that centres the digits vertically
PAD = 0.55                  # clear space between the text box and the lot outline (drawing units; outline ~9 x 13)
FS_MAX, FS_MIN = 4.0, 1.5

def display(htext):
    return re.sub(r'^H0*', '', htext) or '0'

def text_box(cx, cy, w, h, ang):
    b = box(-w / 2, -h / 2, w / 2, h / 2)
    b = affinity.rotate(b, ang, origin=(0, 0))
    return affinity.translate(b, cx, cy)

def norm_angle(a):
    return ((a + 90) % 180) - 90          # (-90, 90]; vertical text reads upward

def long_axis_angle(poly):
    mrr = poly.minimum_rotated_rectangle
    pts = list(mrr.exterior.coords)[:4]
    e = [(pts[(i + 1) % 4][0] - pts[i][0], pts[(i + 1) % 4][1] - pts[i][1]) for i in range(2)]
    v = max(e, key=lambda t: math.hypot(*t))
    return math.degrees(math.atan2(v[1], v[0]))

def fit_one(poly, s):
    inset = poly.buffer(-PAD)
    if inset.is_empty or inset.geom_type != 'Polygon':
        if inset.is_empty: return None
        inset = max(inset.geoms, key=lambda g: g.area)
    n = len(s)
    centers = [inset.centroid]           # the true centre first; inscribed-circle / interior points only help irregular lots
    try: centers.append(polylabel(inset, 0.05))
    except Exception: pass
    centers.append(inset.representative_point())
    la = long_axis_angle(poly)
    # candidate directions: page-horizontal (easiest to read), along the lot, across the lot
    cand = [0.0, norm_angle(la), norm_angle(la + 90)]
    res = []
    for ang in dict.fromkeys(round(a, 1) for a in cand):
        top = None
        for c in centers:
            lo, hi = 0.0, FS_MAX
            for _ in range(14):
                mid = (lo + hi) / 2
                if inset.contains(text_box(c.x, c.y, ADV * n * mid, CAPH * mid, ang)): lo = mid
                else: hi = mid
            if top is None or lo > top[0] + 0.12: top = (lo, ang, c.x, c.y)
        res.append(top)
    best = max(res, key=lambda r: r[0])
    # readability first: a (near-)horizontal number is preferred whenever it is almost as large as the best fit
    horiz = [r for r in res if abs(r[1]) <= 45 and r[0] >= max(3.0, 0.88 * best[0])]
    pick = max(horiz, key=lambda r: r[0]) if horiz else best
    return (pick[0], pick[0], pick[1], pick[2], pick[3])

def run():
    R = json.load(open(f'{DATA}/registry.json')); C = json.load(open(f'{DATA}/cells.json'))
    polys = {c['id']: Polygon(c['poly']).buffer(0) for c in C}
    out, small = [], []
    for r in R['verified']:
        s = display(r['htext'])
        rec = dict(gid=r['gid'], s=r['section'], l=r['legacy'], h=r['htext'], d=s, hn=r['hnum'], geom=r['geom'], ev=r['evidence'])
        if r['geom'] == 'outlined':
            poly = polys[r['cell']]; rec['poly'] = [[round(x, 2), round(y, 2)] for x, y in poly.exterior.coords][:-1]; rec['cell'] = r['cell']
            b = fit_one(poly, s)
            if b is None or b[1] < FS_MIN:
                rec.update(fs=0, ang=0, cx=round(poly.representative_point().x, 2), cy=round(poly.representative_point().y, 2)); small.append(rec)
            else:
                rec.update(fs=round(b[1], 2), ang=round(b[2], 1), cx=round(b[3], 2), cy=round(b[4], 2))
        else:
            rec.update(fs=2.4, ang=norm_angle(r['ang']), cx=r['pt'][0], cy=r['pt'][1], poly=None)
        out.append(rec)
    json.dump(out, open(f'{DATA}/lots_fit.json', 'w'))
    fs = np.array([o['fs'] for o in out if o['fs']])
    print('lots', len(out), 'fitted', len(fs), 'too small to label', len(small), 'font size pctl 5/50/95', np.percentile(fs, [5, 50, 95]).round(2))
    print('too small', [(o['s'], o['l']) for o in small][:20])
if __name__ == '__main__': run()
