"""Warp the Google Earth screenshots into lot-map coordinates, paint out the roofs that Google Earth's tilt smears beside the
footprints, find tree crowns, and dump everything the 3D page needs.
Alignment: six matched points (the two central road crossings and the four outer block corners) tie the closer screenshot to the
lot map; the wider screenshot is registered to the closer one with SIFT features and the two transforms are chained."""
import cv2, numpy as np, json, base64, os
from scipy import ndimage as ndi
here = os.path.dirname(os.path.abspath(__file__)); os.chdir(here)
im = cv2.imread('img/google_earth_wide.jpg')
ui = np.zeros(im.shape[:2], np.uint8)       # blank the Google Earth interface (legend, title, logo, compass, scale bar)
for (xa, ya, xb, yb) in [(1335, 0, 1500, 165), (0, 0, 142, 46), (0, 832, 105, 868), (1365, 832, 1500, 868)]: ui[ya:yb, xa:xb] = 255
im = cv2.inpaint(im, ui, 6, cv2.INPAINT_TELEA)
MAP = np.float32([[1006.9, 624], [1373, 634.9], [827, 386], [1670, 421], [820.6, 885], [1666.6, 914]])
AER = np.float32([[590, 490], [1047, 485], [392, 262], [1392, 258], [338, 805], [1473, 800]])
H1, _ = cv2.findHomography(MAP, AER, cv2.RANSAC, 12.0)
a1 = cv2.imread('img/google_earth_topdown.jpg')
sift = cv2.SIFT_create(6000)
k1, d1 = sift.detectAndCompute(cv2.cvtColor(a1, cv2.COLOR_BGR2GRAY), None); k2, d2 = sift.detectAndCompute(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), None)
good = [m for m, n in cv2.BFMatcher().knnMatch(d1, d2, k=2) if m.distance < 0.75 * n.distance]
G, inl = cv2.findHomography(np.float32([k1[g.queryIdx].pt for g in good]), np.float32([k2[g.trainIdx].pt for g in good]), cv2.RANSAC, 4.0)
print('registration inliers', int(inl.sum()), 'of', len(good))
H = G @ H1
S = 1.4; x0, y0, x1, y1 = 220, 60, 1800, 1040
W, Hh = int((x1 - x0) * S), int((y1 - y0) * S)
T = np.array([[S, 0, -x0 * S], [0, S, -y0 * S], [0, 0, 1]], float)
raw = cv2.warpPerspective(im, H @ np.linalg.inv(T), (W, Hh), flags=cv2.INTER_AREA | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
mask = cv2.warpPerspective(np.full(im.shape[:2], 255, np.uint8), H @ np.linalg.inv(T), (W, Hh), flags=cv2.INTER_NEAREST | cv2.WARP_INVERSE_MAP)
mask = cv2.erode(mask, np.ones((9, 9), np.uint8))
P = lambda x, y: (int(round((x - x0) * S)), int(round((y - y0) * S)))
bld = json.load(open('three/buildings.json')) if os.path.exists('three/buildings.json') else []
# roofs in the photo lean away from their footprints (the camera is tilted): paint out the footprint and its leaned copy
SHIFT = {'maus': (-3.0, -19.0), 'office': (-28.0, -13.0)}   # measured offsets between each footprint and its roof in the photo
bm = np.zeros((Hh, W), np.uint8)
for b in bld:
    dx, dy = SHIFT.get(b['t'], (0.0, 0.0))
    if dx or dy:
        p = np.array(b['p'], float).reshape(-1, 2) + [dx * 10, dy * 10]; b['p'] = [int(round(v)) for v in p.ravel()]
        b['o'][0] = round(b['o'][0] + dx, 1); b['o'][1] = round(b['o'][1] + dy, 1)
clean = raw
out = clean.copy(); out[mask == 0] = (32, 38, 30)
ok, buf = cv2.imencode('.jpg', out, [cv2.IMWRITE_JPEG_QUALITY, 74])
tex = 'data:image/jpeg;base64,' + base64.b64encode(buf.tobytes()).decode()
# tree crowns: dark, busy, round regions away from roads and buildings
hsv = cv2.cvtColor(raw, cv2.COLOR_BGR2HSV).astype(np.float32); g = cv2.cvtColor(raw, cv2.COLOR_BGR2GRAY).astype(np.float32)
Vb = cv2.GaussianBlur(hsv[..., 2], (0, 0), 3); Sb = cv2.GaussianBlur(hsv[..., 1], (0, 0), 3)
busy = cv2.GaussianBlur(np.abs(cv2.Laplacian(cv2.GaussianBlur(g, (0, 0), 1.2), cv2.CV_32F)), (0, 0), 3.5)
score = cv2.GaussianBlur(busy * (0.35 + (255 - Vb) / 255.), (0, 0), 4)
road = cv2.dilate(((Vb > 150) & (Sb < 45)).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (19, 19)))
road |= cv2.dilate((cv2.GaussianBlur(hsv[..., 2], (0, 0), 1) > 205).astype(np.uint8) & (cv2.GaussianBlur(hsv[..., 1], (0, 0), 1) < 40).astype(np.uint8), np.ones((13, 13), np.uint8))
bad = (road > 0) | (bm > 0) | (mask == 0) | (Vb > 128)
sc = np.where(bad, 0, score)
# the crowns cannot be picked out one by one at this resolution, so trees are scattered with a density that follows how dark and
# busy the photo is (woods get many, lawn few), keeping off roads, buildings and labels. Positions are approximate, not surveyed.
rng = np.random.default_rng(7)
WOODS = [(573, 600, 790, 880)]   # the dense stand west of the cemetery (read off the photo): trees go in at a high density
wood = cv2.GaussianBlur(sc, (0, 0), 10)
t0, t1 = np.percentile(wood[~bad], 62), np.percentile(wood[~bad], 97)
prob = np.clip((wood - t0) / (t1 - t0), 0, 1) ** 1.25
LT = json.load(open('../pipeline2/data/lots_fit.json'))
lotmask = np.zeros((Hh, W), np.uint8)
for o in LT:
    if o.get('poly'): cv2.fillPoly(lotmask, [np.int32([P(x, y) for x, y in o['poly']])], 255)
trees = []; grid = {}
cand = rng.random((60000, 2)) * [W, Hh]
for x, y in cand:
    xi, yi = int(x), int(y)
    if bad[yi, xi]: continue
    p = prob[yi, xi] * (0.4 if lotmask[yi, xi] else 1.0)
    if rng.random() > p * 0.36: continue
    gx, gy = int(x // 24), int(y // 24)
    if any((gx + a, gy + b) in grid and np.hypot(grid[(gx + a, gy + b)][0] - x, grid[(gx + a, gy + b)][1] - y) < 21 for a in (-1, 0, 1) for b in (-1, 0, 1)): continue
    grid[(gx, gy)] = (x, y)
    r = 5.0 + 6.5 * float(prob[yi, xi]) + 1.5 * rng.random()
    trees.append([round(float(x) / S + x0, 1), round(float(y) / S + y0, 1), round(r, 1)])
    if len(trees) >= 900: break
for (wx0, wy0, wx1, wy1) in WOODS:
    for _ in range(4000):
        mx_, my_ = rng.uniform(wx0, wx1), rng.uniform(wy0, wy1); x, y = (mx_ - x0) * S, (my_ - y0) * S
        if not (0 <= int(x) < W and 0 <= int(y) < Hh) or bad[int(y), int(x)] or lotmask[int(y), int(x)]: continue
        gx, gy = int(x // 24), int(y // 24)
        if any((gx + a, gy + b) in grid and np.hypot(grid[(gx + a, gy + b)][0] - x, grid[(gx + a, gy + b)][1] - y) < 17 for a in (-1, 0, 1) for b in (-1, 0, 1)): continue
        grid[(gx, gy)] = (x, y); trees.append([round(float(mx_), 1), round(float(my_), 1), round(float(5.5 + 4.5 * rng.random()), 1)])
L = json.load(open('../pipeline2/data/lots_fit.json'))
lots = []
for o in L:
    if o.get('poly'):
        lots.append([o['s'], o['l'], o['hn'], [int(round(v * 10)) for p in o['poly'] for v in p]])
json.dump(dict(tex=tex, ext=[x0, y0, x1, y1], lots=lots, bld=bld, trees=trees), open('three/data3d.json', 'w'), separators=(',', ':'))
print(len(lots), 'lots;', len(trees), 'trees; texture', len(buf) // 1024, 'KB')
vis = clean.copy()
for x, y, r in trees: cv2.circle(vis, P(x, y), int(r * S), (0, 0, 255), 2)
cv2.imwrite('three/ground_preview.jpg', cv2.resize(vis, (W * 2 // 3, Hh * 2 // 3)))
