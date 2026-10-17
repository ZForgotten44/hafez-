"""Find building footprints in the raw drawing: render every line, flood-fill the enclosed white regions,
keep compact ones that are not lots, and give each a height from its area. Writes three/buildings.json."""
import json, numpy as np, cv2, os
here = os.path.dirname(os.path.abspath(__file__)); os.chdir(here)
D = json.load(open('../pipeline2/data/ai_raw.json'))['draws']
S = 4; x0, y0, x1, y1 = 300, 200, 1800, 1060; W, H = (x1 - x0) * S, (y1 - y0) * S
img = np.full((H, W), 255, np.uint8)
P = lambda x, y: (int(round((x - x0) * S)), int(round((y - y0) * S)))
for d in D:
    for it in d['items']:
        if it[0] == 'l': cv2.line(img, P(it[1], it[2]), P(it[3], it[4]), 0, 2)
        elif it[0] == 'c' and len(it) >= 9: cv2.polylines(img, [np.array([P(it[1], it[2]), P(it[7], it[8])])], False, 0, 2)
        elif it[0] == 're': cv2.rectangle(img, P(it[1], it[2]), P(it[3], it[4]), 0, 2)
        elif it[0] == 'qu': cv2.polylines(img, [np.array([P(it[i], it[i + 1]) for i in (1, 3, 5, 7)])], True, 0, 2)
n, lab, st, cen = cv2.connectedComponentsWithStats((img > 128).astype(np.uint8), connectivity=4)
L = json.load(open('../pipeline2/data/lots_fit.json')); lc = np.array([[o['cx'], o['cy']] for o in L if o.get('cx') is not None])
out = []
for i in range(1, n):
    x, y, w, h, a = st[i]; au = a / (S * S)
    if au < 150 or au > 6000 or x == 0 or y == 0 or x + w >= W or y + h >= H: continue
    comp = (lab == i).astype(np.uint8); cnt, _ = cv2.findContours(comp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE); c = max(cnt, key=cv2.contourArea)
    sol = cv2.contourArea(c) / max(1, cv2.contourArea(cv2.convexHull(c))); asp = max(w, h) / max(1, min(w, h))
    cx, cy = cen[i] / S + [x0, y0]
    if np.min(np.hypot(lc[:, 0] - cx, lc[:, 1] - cy)) < 16 or sol < .8 or asp > 4: continue
    ap = cv2.approxPolyDP(c, 2.5, True)[:, 0, :] / S + [x0, y0]
    out.append([[int(round(float(v) * 10)) for p in ap for v in p], 12 if au < 350 else (22 if au < 1400 else 28)])
os.makedirs('three', exist_ok=True); json.dump(out, open('three/buildings.json', 'w'), separators=(',', ':'))
print(len(out), 'buildings')
