"""Step 2: turn the CAD line work into lot cells.
Lot outlines are drawn as independent short strokes whose ends do not always meet exactly, so polygonising the
vector lines is unreliable.  Instead the lines are rasterised (fine, 8 px per drawing unit) and every enclosed white
area is a lot cell; its outline is traced back to vector coordinates.  Nothing here is guessed: a cell is only an
area that the drawing itself encloses."""
import json, numpy as np, cv2
from common import *
Z = 8                      # raster pixels per drawing unit
PAD = 8
def run():
    D = json.load(open(f'{DATA}/ai_raw.json'))
    segs = []
    for d in D['draws']:
        if tuple(d['color']) == LOT_COLOR:
            for it in d['items']:
                if it[0] == 'l': segs.append(it[1:])
                elif it[0] == 'qu':          # rotated rectangles (e.g. the mausoleum-garden rows) come through as quads
                    q = it[1:]
                    for i in range(4): segs.append([q[2 * i], q[2 * i + 1], q[(2 * i + 2) % 8], q[(2 * i + 3) % 8]])
                elif it[0] == 're':
                    a, b, c, d = it[1:]; segs += [[a, b, c, b], [c, b, c, d], [c, d, a, d], [a, d, a, b]]
    S = np.array(segs)
    x0 = S[:, [0, 2]].min() - PAD; y0 = S[:, [1, 3]].min() - PAD
    x1 = S[:, [0, 2]].max() + PAD; y1 = S[:, [1, 3]].max() + PAD
    W, H = int((x1 - x0) * Z), int((y1 - y0) * Z)
    img = np.full((H, W), 255, np.uint8)
    for a, b, c, d in S:
        cv2.line(img, (int(round((a - x0) * Z)), int(round((b - y0) * Z))), (int(round((c - x0) * Z)), int(round((d - y0) * Z))), 0, thickness=6)
    n, lab, stats, cent = cv2.connectedComponentsWithStats((img == 255).astype(np.uint8), connectivity=4)
    bg = lab[0, 0]
    cells = []
    for k in range(1, n):
        if k == bg: continue
        x, y, w, h, area = stats[k]
        if area < 40 * Z * Z / 4 or w >= W - 4 or h >= H - 4: continue   # specks / the outside world
        m = (lab[y:y + h, x:x + w] == k).astype(np.uint8)
        cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        c = max(cs, key=cv2.contourArea)
        c = cv2.approxPolyDP(c, 0.35 * Z / 8 * 2, True)[:, 0, :].astype(float)
        poly = [[round((px + x) / Z + x0, 2), round((py + y) / Z + y0, 2)] for px, py in c]
        cells.append(dict(id=len(cells), area=round(float(area) / Z / Z, 1), poly=poly))
    json.dump(cells, open(f'{DATA}/cells.json', 'w'))
    print('cells', len(cells), 'median area', np.median([c['area'] for c in cells]))
if __name__ == '__main__': run()
