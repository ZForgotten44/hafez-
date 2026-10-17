"""Building footprints from the raw drawing -> three/buildings.json
1. every enclosed compact region that is not a lot is a footprint (houses, sheds, the office, the gate buildings);
2. the four mausoleums are traced from seed points inside their notched outlines (the notches are the buttresses);
Each footprint gets a type, a wall height and its oriented bounding box (centre, long side, short side, angle)."""
import json, numpy as np, cv2, os
here = os.path.dirname(os.path.abspath(__file__)); os.chdir(here)
D = json.load(open('../pipeline2/data/ai_raw.json'))['draws']
L = json.load(open('../pipeline2/data/lots_fit.json')); lc = np.array([[o['cx'], o['cy']] for o in L if o.get('cx') is not None])
def render(x0, y0, x1, y1, S, thick):
    W, H = int((x1 - x0) * S), int((y1 - y0) * S); img = np.full((H, W), 255, np.uint8)
    P = lambda x, y: (int(round((x - x0) * S)), int(round((y - y0) * S)))
    for d in D:
        for it in d['items']:
            if it[0] == 'l': cv2.line(img, P(it[1], it[2]), P(it[3], it[4]), 0, thick)
            elif it[0] == 'c' and len(it) >= 9: cv2.polylines(img, [np.array([P(it[1], it[2]), P(it[7], it[8])])], False, 0, thick)
            elif it[0] == 're': cv2.rectangle(img, P(it[1], it[2]), P(it[3], it[4]), 0, thick)
            elif it[0] == 'qu': cv2.polylines(img, [np.array([P(it[i], it[i + 1]) for i in (1, 3, 5, 7)])], True, 0, thick)
    return img
def obb(pts):
    (cx, cy), (w, h), a = cv2.minAreaRect(np.float32(pts))
    if w < h: w, h, a = h, w, a + 90
    return [round(cx, 1), round(cy, 1), round(w, 1), round(h, 1), round(float(np.radians(a)), 4)]
def region_polys(img, S, x0, y0, amin, amax, seeds=None, eps=2.5):
    bw = (img > 128).astype(np.uint8)
    n, lab, st, cen = cv2.connectedComponentsWithStats(bw, connectivity=4); out = []
    H, W = img.shape
    idx = range(1, n) if seeds is None else [lab[int(round((sy - y0) * S)), int(round((sx - x0) * S))] for sx, sy in seeds]
    for i in idx:
        if i == 0: continue
        x, y, w, h, a = st[i]; au = a / (S * S)
        if seeds is None and (au < amin or au > amax or x == 0 or y == 0 or x + w >= W or y + h >= H): continue
        comp = (lab == i).astype(np.uint8); cnt, _ = cv2.findContours(comp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE); c = max(cnt, key=cv2.contourArea)
        sol = cv2.contourArea(c) / max(1, cv2.contourArea(cv2.convexHull(c))); asp = max(w, h) / max(1, min(w, h))
        cx, cy = cen[i] / S + [x0, y0]
        if seeds is None and (np.min(np.hypot(lc[:, 0] - cx, lc[:, 1] - cy)) < 16 or sol < .8 or asp > 4): continue
        ap = cv2.approxPolyDP(c, eps, True)[:, 0, :] / S + [x0, y0]
        out.append((ap, au))
    return out
b = []
# 1. everything compact and enclosed
img = render(300, 200, 1800, 1060, 4, 2)
for ap, au in region_polys(img, 4, 300, 200, 150, 6000):
    b.append(dict(t='house', p=ap, h=12 if au < 350 else (22 if au < 1400 else 26), a=au))
# 2. the four mausoleums: seeds inside the notched outlines; thick lines close small gaps
MAUS = [(563.3, 345.0), (561.7, 408.3), (638.3, 353.3), (638.3, 396.7)]
img2 = render(500, 300, 720, 480, 6, 3)
mp = region_polys(img2, 6, 500, 300, 0, 0, seeds=MAUS, eps=1.0)
b = [x for x in b if all(np.hypot(*(np.mean(x['p'], 0) - s)) > 22 for s in MAUS)]
for (ap, au) in mp: b.append(dict(t='maus', p=ap, h=15, a=au))
# 3. the cemetery office (cottage): the angled footprint beside the main gate
for x in b:
    cx, cy = np.mean(x['p'], 0)
    if x['t'] == 'house' and np.hypot(cx - 1377, cy - 359) < 20: x['t'] = 'office'; x['h'] = 11
out = [dict(t=x['t'], p=[int(round(float(v) * 10)) for q in x['p'] for v in q], h=x['h'], o=obb(x['p'])) for x in b]
os.makedirs('three', exist_ok=True); json.dump(out, open('three/buildings.json', 'w'), separators=(',', ':'))
import collections; print(len(out), 'buildings', dict(collections.Counter(x['t'] for x in out)))
