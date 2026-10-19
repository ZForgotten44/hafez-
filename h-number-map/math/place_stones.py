"""Headstone placement for the 3D page, done once at build time so the page just draws what it is given.
Every stone (and its plinth) is fitted inside its own lot polygon with a margin, kept off the paved paths/roads read from the aerial, and
shrunk or dropped when the lot cannot hold it. Also holds the road/path mask and the numeric check:
    python3 place_stones.py check      (reads three/data3d.json and three/ground.jpg)"""
import math, json, sys
import numpy as np, cv2
from shapely.geometry import Polygon, Point
S, X0, Y0 = 1.4, 220.0, 60.0
# type table: stone width, height, thickness, has plinth, lies flat, probability   (same order as TYPES in the page)
TY = [(3.0, 3.6, .85, 1, 0, .28), (3.2, 3.0, .80, 1, 0, .22), (3.0, 3.9, .85, 1, 0, .12), (3.2, 4.8, .90, 1, 0, .08),
      (2.2, 6.4, 2.20, 0, 0, .05), (2.4, .45, 3.40, 0, 1, .15), (2.8, 1.5, 1.80, 0, 0, .10)]
SIZE = .70      # overall shrink against the old stones
def rnd(i, k):
    x = math.sin(i * 127.1 + k * 311.7) * 43758.5453; return x - math.floor(x)
def _hsv(im):
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV).astype(np.float32); V = hsv[..., 2]; Sa = hsv[..., 1]
    Vb = cv2.GaussianBlur(V, (0, 0), 1.2); Sb = cv2.GaussianBlur(Sa, (0, 0), 1.2)
    sd = np.sqrt(np.maximum(cv2.GaussianBlur(V ** 2, (0, 0), 2.5) - cv2.GaussianBlur(V, (0, 0), 2.5) ** 2, 0)); return Vb, Sb, sd
def _clean(r, area, ext):
    r = cv2.morphologyEx(r, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    n, lab, st, _ = cv2.connectedComponentsWithStats(r); keep = np.zeros_like(r)
    for i in range(1, n):
        if st[i, 4] > area and max(st[i, 2], st[i, 3]) > ext: keep[lab == i] = 1
    return keep
def _lines(b, L=61, th=3, angs=(-4, -2, 0, 2, 4)):
    """long straight pale bands (narrow footpaths inside the blocks): an opening with a long thin line, a few degrees either way"""
    out = np.zeros_like(b)
    for base in (0, 90):
        for a in angs:
            k = np.zeros((L, L), np.uint8); c = L // 2; t = np.deg2rad(base + a)
            cv2.line(k, (int(c - c * np.cos(t)), int(c - c * np.sin(t))), (int(c + c * np.cos(t)), int(c + c * np.sin(t))), 1, th)
            out |= cv2.morphologyEx(b, cv2.MORPH_OPEN, k)
    return out
def road_mask(im):
    """Paved paths and roads: pale, grey and smooth in the warped aerial. A strict pass finds the sure ones, a looser pass adds the shaded
    stretches that touch them; bare lawn and stone-dense patches are neither pale-grey-smooth nor connected, so they stay out."""
    Vb, Sb, sd = _hsv(im)
    strict = _clean(((Sb < 46) & (Vb > 152) & (sd < 22)).astype(np.uint8), 420, 34)
    loose = _clean(((Sb < 60) & (Vb > 126) & (sd < 30)).astype(np.uint8), 260, 26)
    near = cv2.dilate(strict, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)))
    m = ((loose > 0) & (near > 0)) | (strict > 0) | (_lines(((Sb < 62) & (Vb > 135)).astype(np.uint8)) > 0)
    return cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
class Road:
    def __init__(self, m, grow=3):
        self.m = cv2.dilate(m, np.ones((grow, grow), np.uint8)) if grow > 1 else m; self.h, self.w = self.m.shape
    def at(self, x, y):
        i, j = int(round((x - X0) * S)), int(round((y - Y0) * S))
        return 0 <= i < self.w and 0 <= j < self.h and self.m[j, i] > 0
    def frac(self, poly, n=7):
        minx, miny, maxx, maxy = poly.bounds; tot = hit = 0
        for a in np.linspace(minx, maxx, n):
            for b in np.linspace(miny, maxy, n):
                if poly.contains(Point(a, b)): tot += 1; hit += self.at(a, b)
        return hit / tot if tot else 0.0
def rect(px, pz, ux, uz, hd, hw):
    vx, vz = -uz, ux
    return Polygon([(px + ux * a + vx * b, pz + uz * a + vz * b) for a, b in ((-hd, -hw), (hd, -hw), (hd, hw), (-hd, hw))])
def footprint(ty, w, th):
    t = TY[ty]; return (.95 * th, .6 * w) if t[3] else (.5 * th, .5 * w)      # half extents along the lot axis and across it
def place(lots, road):
    """lots: rows [section,label,h,flat polygon*10]. Returns a placement (or 0 = no stone) per lot row, in the same order, and stats."""
    out = []; st = dict(none_small=0, none_road=0, none_nofit=0, shrunk=0, placed=0)
    for idx, (s, l, hn, p) in enumerate(lots):
        h = hn + idx * 0.0137                                                           # distinct seed even when two lots share an H-number
        v = np.array(p, float).reshape(-1, 2) / 10
        poly = Polygon(v)
        if not poly.is_valid: poly = poly.buffer(0)
        if poly.geom_type != 'Polygon':
            poly = max(poly.geoms, key=lambda g: g.area) if hasattr(poly, 'geoms') and len(poly.geoms) else Polygon()
        if poly.is_empty or poly.area < 14: out.append(0); st['none_small'] += 1; continue
        rr = np.array(poly.minimum_rotated_rectangle.exterior.coords)[:4]; e1 = rr[1] - rr[0]; e2 = rr[2] - rr[1]
        l1, l2 = math.hypot(*e1), math.hypot(*e2); u = e1 if l1 >= l2 else e2; Lr, Wr = max(l1, l2), min(l1, l2); ctr = rr.mean(0)
        if Wr < 3.4 or Lr < 4.2: out.append(0); st['none_small'] += 1; continue
        if road.frac(poly) > .55: out.append(0); st['none_road'] += 1; continue          # the outline lies mostly on a road or path
        ux, uz = u / math.hypot(*u)
        if uz > 0: ux, uz = -ux, -uz                                                    # stone stands at the north end, face across the lot
        ja = (rnd(h, 4) - .5) * .12; cj, sj = math.cos(ja), math.sin(ja); ux, uz = ux * cj - uz * sj, ux * sj + uz * cj
        r = rnd(h, 9); a = 0; ty = 0
        for q, t in enumerate(TY):
            a += t[5]
            if r < a: ty = q; break
        t = TY[ty]
        w0 = min(t[0] * SIZE * (.9 + .2 * rnd(h, 1)), .40 * Wr); th0 = t[2] * (.62 if not t[4] else .68) * (.9 + .2 * rnd(h, 3))
        if ty == 4: th0 = w0 * .95                                                      # obelisk is square
        inner = poly.buffer(-.45)
        if inner.is_empty: out.append(0); st['none_nofit'] += 1; continue
        got = None
        for k, sh in enumerate((1.0, .84, .7)):
            w, th = w0 * sh, th0 * sh; hd, hw = footprint(ty, w, th)
            for fo in (.26, -.26, 0, .34, -.34):
                for lo in (0, .12, -.12):
                    px = ctr[0] + ux * fo * Lr + (-uz) * lo * Wr; pz = ctr[1] + uz * fo * Lr + ux * lo * Wr
                    fp = rect(px, pz, ux, uz, hd, hw)
                    if inner.contains(fp) and road.frac(fp, 5) <= .08: got = (px, pz, w, th, k); break
                if got: break
            if got: break
        if not got: out.append(0); st['none_nofit'] += 1; continue
        px, pz, w, th, k = got; st['placed'] += 1; st['shrunk'] += k > 0
        out.append([ty, round(px, 2), round(pz, 2), round(ux, 3), round(uz, 3), round(w, 2), round(th, 2), round(.72 * (.82 + .36 * rnd(h, 2)), 2)])
    return out, st
def check(D, road):
    """count stones whose plinth/footprint is not fully inside their lot, and stones standing on the road mask"""
    outside = onroad = n = 0
    for s, l, h, p, *pl in D['lots']:
        pl = pl[0] if pl else 0
        if not pl: continue
        ty, px, pz, ux, uz, w, th, hs = pl; hd, hw = footprint(ty, w, th); fp = rect(px, pz, ux, uz, hd, hw)
        poly = Polygon(np.array(p, float).reshape(-1, 2) / 10).buffer(0); n += 1
        if not poly.buffer(.01).contains(fp): outside += 1
        if road.frac(fp, 5) > .25: onroad += 1
    return n, outside, onroad
if __name__ == '__main__':
    D = json.load(open('three/data3d.json')); im = cv2.imread('three/ground.jpg'); R = Road(road_mask(im))
    n, o, r = check(D, R); print('stones', n, 'not fully inside own lot', o, 'on road mask (>25% of footprint)', r)
