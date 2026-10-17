"""Assemble the standalone 3D page: fonts, lot data and the ground are inlined; three.js loads from jsDelivr.
  python3 build_3d.py          -> Cedar_Grove_3D.html   (ground = the warped Google Earth photo; git-ignored, private)
  python3 build_3d.py public   -> ../site/3d.html        (ground drawn from the lot map only; safe to commit and publish)"""
import json, base64, os, sys
import numpy as np, cv2
here = os.path.dirname(os.path.abspath(__file__)); os.chdir(here)
public = len(sys.argv) > 1 and sys.argv[1] == 'public'
b64 = lambda p: base64.b64encode(open(p, 'rb').read()).decode()
FONTS = '@font-face{font-family:"Space Grotesk";font-style:normal;font-weight:300 700;font-display:swap;src:url(data:font/woff2;base64,%s) format("woff2")}' % b64('fonts/SpaceGrotesk-400.woff2')
for w in (400, 500, 600):
    FONTS += '@font-face{font-family:"IBM Plex Mono";font-style:normal;font-weight:%d;font-display:swap;src:url(data:font/woff2;base64,%s) format("woff2")}' % (w, b64('fonts/IBMPlexMono-%d.woff2' % w))
D = json.load(open('three/data3d.json'))
if public:
    # ground without imagery: lawn, with the roads and paths read from the gaps between blocks of lots
    x0, y0, x1, y1 = D['ext']; S = 1.4; W, H = int((x1 - x0) * S), int((y1 - y0) * S)
    P = lambda x, y: (int(round((x - x0) * S)), int(round((y - y0) * S)))
    lot = np.zeros((H, W), np.uint8)
    for r in D['lots']:
        v = np.array(r[3], float).reshape(-1, 2) / 10; cv2.fillPoly(lot, [np.int32([P(a, b) for a, b in v])], 255)
    block = cv2.morphologyEx(lot, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(7 * S) | 1, int(7 * S) | 1)))
    hull = cv2.morphologyEx(block, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(46 * S) | 1, int(46 * S) | 1)))
    road = (hull > 0) & (block == 0)
    rng = np.random.default_rng(3)
    n = cv2.GaussianBlur(rng.random((H, W)).astype(np.float32), (0, 0), 6); n = (n - n.mean()) / n.std()
    img = np.zeros((H, W, 3), np.float32); lawn = np.array([86, 128, 98], np.float32)   # BGR
    img[:] = lawn + n[..., None] * 5
    outer = hull == 0; img[outer] = (lawn * 0.93 + n[outer][:, None] * 4)
    rd = np.array([186, 190, 190], np.float32); img[road] = rd + n[road][:, None] * 3
    for b in D['bld']:
        cv2.fillPoly(img, [np.int32([P(a / 10, c / 10) for a, c in np.array(b['p']).reshape(-1, 2)])], (150, 154, 156))
    ok, buf = cv2.imencode('.jpg', np.clip(img, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 82])
    D['tex'] = 'data:image/jpeg;base64,' + base64.b64encode(buf.tobytes()).decode(); D['pub'] = 1
html = open('cemetery3d_page2.html').read().replace('/*__FONTS__*/', FONTS).replace('/*__DATA__*/null', json.dumps(D, separators=(',', ':')).replace('</', '<\\/'))
out = '../site/3d.html' if public else 'Cedar_Grove_3D.html'
if public: html = '<!doctype html>\n' + html
open(out, 'w').write(html)
print(out, len(html) // 1024, 'KB')
