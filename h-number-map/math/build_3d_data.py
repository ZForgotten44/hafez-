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
# hand corrections read off the photos: the garage and chapel footprints come from the drawing's loose "house" boxes, one of which is really the
# footpath; sizes and centres below are measured on the aerial (roof centres), axis-aligned unless noted
def near(b, x, y, r=12): return abs(b['o'][0] - x) < r and abs(b['o'][1] - y) < r
def rect(cx, cy, L, W, a):
    c, s_ = np.cos(a), np.sin(a); return [int(round(v * 10)) for dx, dy in [(-L/2, -W/2), (L/2, -W/2), (L/2, W/2), (-L/2, W/2)] for v in (cx + dx * c - dy * s_, cy + dx * s_ + dy * c)]
bld = [b for b in bld if not near(b, 1328.2, 387.0)]
for b in bld:
    if near(b, 1287.3, 384.6): b['t'] = 'garage'; b['h'] = 9; b['o'] = [1262.0, 370.0, 25.0, 24.0, 0.0]; b['p'] = rect(1262, 370, 25, 24, 0)
    if near(b, 1408.8, 536.3): b['t'] = 'chapel'; b['h'] = 14; b['o'] = [1392.0, 522.0, 44.0, 24.0, 0.0]; b['p'] = rect(1392, 522, 44, 24, 0)
    if b['t'] == 'office': b['o'][0], b['o'][1] = 1341.0, 345.5
bm = np.zeros((Hh, W), np.uint8)
for b in bld: cv2.fillPoly(bm, [np.int32([P(x / 10, y / 10) for x, y in np.array(b['p']).reshape(-1, 2)])], 255)
bm = cv2.dilate(bm, np.ones((9, 9), np.uint8))
clean = raw
out = clean.copy(); out[mask == 0] = (32, 38, 30)
ok, buf = cv2.imencode('.jpg', out, [cv2.IMWRITE_JPEG_QUALITY, 74])
tex = 'data:image/jpeg;base64,' + base64.b64encode(buf.tobytes()).decode()
# trees: the photo is early spring, so crowns show up as dark shadow/evergreen blobs. Blobs found with a distance transform give a position and
# crown size for each large tree; the leafless stand west of the cemetery is too tangled to separate, so it is filled at a typical spacing.
hsv = cv2.cvtColor(raw, cv2.COLOR_BGR2HSV).astype(np.float32)
Vb = cv2.GaussianBlur(hsv[..., 2], (0, 0), 2.5); V0 = hsv[..., 2]; Sb = hsv[..., 1]
white = cv2.dilate(((V0 > 195) & (Sb < 50)).astype(np.uint8), np.ones((9, 9), np.uint8))
dark = (Vb < 92).astype(np.uint8); dark[white > 0] = 0; dark[bm > 0] = 0; dark[mask == 0] = 0
dark = cv2.morphologyEx(dark, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
dt = cv2.distanceTransform(dark, cv2.DIST_L2, 5)
ys, xs = np.nonzero((dt == cv2.dilate(dt, np.ones((15, 15), np.uint8))) & (dt >= 10))
cands = sorted([(float(dt[y, x]), int(x), int(y)) for y, x in zip(ys, xs)], reverse=True)
trees = []
for r, x, y in cands:
    if any(np.hypot(x - t[0], y - t[1]) < 0.9 * max(r, t[2]) for t in trees): continue
    yy, xx = np.ogrid[:Hh, :W]; m = (xx - x) ** 2 + (yy - y) ** 2 < (r * .8) ** 2
    trees.append([x, y, r, 1 if float(Vb[m].mean()) < 58 else 0])
trees = [[round(x / S + x0, 1), round(y / S + y0, 1), round(r / S * 1.25, 1), t] for x, y, r, t in trees]
def in_bld(x, y, pad):
    for b in bld:
        cx, cy, L, Wd, ang = b['o']; c, s_ = np.cos(ang), np.sin(ang); dx, dy = x - cx, y - cy
        if abs(dx * c + dy * s_) < L / 2 + pad and abs(-dx * s_ + dy * c) < Wd / 2 + pad: return True
    return False
trees = [t for t in trees if not in_bld(t[0], t[1], 8 + 0.8 * t[2])]   # dark blobs hugging a building are its shadow, not a tree
rng = np.random.default_rng(7)
WOODS = [(573, 600, 790, 880)]
pts = [(t[0], t[1]) for t in trees]
for (wx0, wy0, wx1, wy1) in WOODS:
    for _ in range(6000):
        mx_, my_ = rng.uniform(wx0, wx1), rng.uniform(wy0, wy1); x, y = int((mx_ - x0) * S), int((my_ - y0) * S)
        if not (0 <= x < W and 0 <= y < Hh) or bm[y, x] or white[y, x] or mask[y, x] == 0: continue
        if any(np.hypot(mx_ - a, my_ - b) < 19 for a, b in pts): continue
        pts.append((mx_, my_)); trees.append([round(float(mx_), 1), round(float(my_), 1), round(float(6 + 4 * rng.random()), 1), 0])
L = json.load(open('../pipeline2/data/lots_fit.json'))
lots = []
for o in L:
    if o.get('poly'):
        lots.append([o['s'], o['l'], o['hn'], [int(round(v * 10)) for p in o['poly'] for v in p]])
json.dump(dict(tex=tex, ext=[x0, y0, x1, y1], lots=lots, bld=bld, trees=trees), open('three/data3d.json', 'w'), separators=(',', ':'))
print(len(lots), 'lots;', len(trees), 'trees; texture', len(buf) // 1024, 'KB')
vis = clean.copy()
for x, y, r, t in trees: cv2.circle(vis, P(x, y), int(r * S), (0, 0, 255) if not t else (0, 255, 0), 2)
cv2.imwrite('three/ground_preview.jpg', cv2.resize(vis, (W * 2 // 3, Hh * 2 // 3)))
