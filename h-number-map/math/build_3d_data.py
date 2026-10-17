"""Warp the Google Earth top-down screenshot into lot-map coordinates and dump the lot outlines for the 3D page.
The homography comes from six matched points: the two central road crossings and the four outer block corners."""
import cv2, numpy as np, json, base64, os
here = os.path.dirname(os.path.abspath(__file__)); os.chdir(here)
im = cv2.imread('img/google_earth_wide.jpg')
# blank the Google Earth interface (legend box, map title, logo, compass and scale bar) before warping
ui = np.zeros(im.shape[:2], np.uint8)
for (xa, ya, xb, yb) in [(1335, 0, 1500, 165), (0, 0, 142, 46), (0, 832, 105, 868), (1365, 832, 1500, 868)]:
    ui[ya:yb, xa:xb] = 255
im = cv2.inpaint(im, ui, 6, cv2.INPAINT_TELEA)
MAP = np.float32([[1006.9, 624], [1373, 634.9], [827, 386], [1670, 421], [820.6, 885], [1666.6, 914]])
AER = np.float32([[590, 490], [1047, 485], [392, 262], [1392, 258], [338, 805], [1473, 800]])
H1, _ = cv2.findHomography(MAP, AER, cv2.RANSAC, 12.0)   # map -> first (closer) screenshot
# the wider screenshot is registered to the first one with SIFT features, then the two transforms are chained
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
Hm = H @ np.linalg.inv(T)
out = cv2.warpPerspective(im, Hm, (W, Hh), flags=cv2.INTER_AREA | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
mask = cv2.warpPerspective(np.full(im.shape[:2], 255, np.uint8), Hm, (W, Hh), flags=cv2.INTER_NEAREST | cv2.WARP_INVERSE_MAP)
mask = cv2.erode(mask, np.ones((9, 9), np.uint8))
# the Google Earth UI (legend box, logo, scale bar, labels) sits in the corners of the screenshot: blank it
out[mask == 0] = (32, 38, 30)
ok, buf = cv2.imencode('.jpg', out, [cv2.IMWRITE_JPEG_QUALITY, 72])
tex = 'data:image/jpeg;base64,' + base64.b64encode(buf.tobytes()).decode()
L = json.load(open('../pipeline2/data/lots_fit.json'))
lots = []
for o in L:
    if o.get('poly'):
        flat = [int(round(v * 10)) for p in o['poly'] for v in p]
        lots.append([o['s'], o['l'], o['hn'], flat])
json.dump(dict(tex=tex, ext=[x0, y0, x1, y1], lots=lots), open('three/data3d.json', 'w'), separators=(',', ':'))
print(len(lots), 'lots; texture', len(buf) // 1024, 'KB', out.shape)
cv2.imwrite('three/ground_preview.jpg', cv2.resize(out, (W // 2, Hh // 2)))
