"""Crops from the two source maps for the Jon deck. Both crops use the same box in drawing units, so scale and orientation match.
OLD = 'Cemetery Map - All Sections on Individual Pages' (one section per page, registered to the 2022 drawing by reg.json).
2022 = 'Cedar Grove 2022 with CR.ai'.  Marks we add are red (solid = drawn on that map, dashed = approximate position taken from the other map);
green rings = neighbours to match by eye; purple = other features. Everything else is the source drawing, untouched."""
import json, os, math, pymupdf as fitz
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
AI = os.path.join(REPO, 'Ground Maps', 'Cedar Grove 2022 with CR.ai')
OLD = os.environ.get('OLD_SHEETS', '/root/.claude/uploads/23b6d665-ee61-58a0-937d-770ab39ca67b/52c1cc26-Cemetery_Map_-_All_Sections_on_Individual_Pages_1.pdf')
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
REG = {int(k): v for k, v in json.load(open(os.path.join(HERE, 'reg.json'))).items()}
CELLS = {c['id']: c for c in json.load(open(os.path.join(REPO, 'h-number-map', 'pipeline2', 'data', 'cells.json')))}
LF = json.load(open(os.path.join(REPO, 'h-number-map', 'pipeline2', 'data', 'lots_fit.json')))
REGISTRY = json.load(open(os.path.join(REPO, 'h-number-map', 'pipeline2', 'data', 'registry.json')))
_ai = fitz.open(AI)[0]; _old = fitz.open(OLD)
RED, GREEN, PURPLE, BLUE = (214, 0, 40), (0, 140, 60), (120, 0, 150), (20, 80, 210)

def unit(sec, lab):
    for o in LF:
        if o['s'] == sec and o['l'] == lab: return (o['cx'], o['cy'])
    raise KeyError((sec, lab))
def unnum(token, near):
    best = None
    for u in REGISTRY['unnumbered']:
        if ''.join(u['tokens']) == token:
            d = math.dist(u['pt'], near)
            if best is None or d < best[0]: best = (d, u)
    return best[1]
def poly(cell): return CELLS[cell]['poly']
def page_of(box):
    cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2; best = None
    for pg, (sc, k, (lx, ly)) in REG.items():
        r = _old[pg - 1].rect; x, y = k * cx - lx, k * cy - ly
        m = min(x - r.x0, r.x1 - x, y - r.y0, r.y1 - y)
        if best is None or m > best[0]: best = (m, pg)
    return best[1]
def crop_ai(box, S):
    pm = _ai.get_pixmap(matrix=fitz.Matrix(S, S), clip=fitz.Rect(*box)); return Image.frombytes('RGB', (pm.width, pm.height), pm.samples)
def crop_old(pg, box, S):
    sc, k, (lx, ly) = REG[pg]; p = _old[pg - 1]
    full = fitz.Rect(k * box[0] - lx, k * box[1] - ly, k * box[2] - lx, k * box[3] - ly); clip = full & p.rect
    z = S / k; pm = p.get_pixmap(matrix=fitz.Matrix(z, z), clip=clip); im = Image.frombytes('RGB', (pm.width, pm.height), pm.samples)
    # pad to the full requested box when the page edge cuts it
    out = Image.new('RGB', (int(round((box[2] - box[0]) * S)), int(round((box[3] - box[1]) * S))), 'white')
    out.paste(im, (int(round(((clip.x0 + lx) / k - box[0]) * S)), int(round(((clip.y0 + ly) / k - box[1]) * S)))); return out
FS = ImageFont.truetype(FB, 24)
def dashed_poly(d, pts, col, w=4, on=14, off=9):
    pts = pts + [pts[0]]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = math.dist((x0, y0), (x1, y1)); t = 0
        while t < L:
            a, b = t / L, min(t + on, L) / L
            d.line([(x0 + (x1 - x0) * a, y0 + (y1 - y0) * a), (x0 + (x1 - x0) * b, y0 + (y1 - y0) * b)], fill=col, width=w); t += on + off
def rect_pts(b): return [(b[0], b[1]), (b[2], b[1]), (b[2], b[3]), (b[0], b[3])]
def arrow(d, tip, frm, col, w=4):
    d.line([frm, tip], fill=col, width=w); ang = math.atan2(tip[1] - frm[1], tip[0] - frm[0]); L = 16
    d.polygon([tip, (tip[0] - L * math.cos(ang - .4), tip[1] - L * math.sin(ang - .4)), (tip[0] - L * math.cos(ang + .4), tip[1] - L * math.sin(ang + .4))], fill=col)
def numbered(d, tip, frm, text, col, font=FS):
    arrow(d, tip, frm, col); r = 19 if len(text) < 3 else 25
    d.ellipse([frm[0] - r, frm[1] - r, frm[0] + r, frm[1] + r], fill=(255, 255, 255), outline=col, width=4)
    tw = d.textlength(text, font=font); d.text((frm[0] - tw / 2, frm[1] - font.size / 2 - 2), text, fill=col, font=font)
DIRS = {'N': (0, -1), 'S': (0, 1), 'E': (1, 0), 'W': (-1, 0), 'NE': (.7, -.7), 'NW': (-.7, -.7), 'SE': (.7, .7), 'SW': (-.7, .7)}
def render(box, marks, S, page=None, extra_old=None):
    """marks: dict(n=label, shape=[pts in units] or None, at=(x,y), kind='red'|'green'|'purple', old=True/False (drawn on old sheet), new=True/False (drawn in 2022), side='N', off=60)
    Returns (old_image, new_image)."""
    pg = page or page_of(box); ims = {}
    for view in ('old', 'new'):
        im = crop_old(pg, box, S) if view == 'old' else crop_ai(box, S); d = ImageDraw.Draw(im)
        P = lambda p: ((p[0] - box[0]) * S, (p[1] - box[1]) * S)
        for m in marks:
            col = {'red': RED, 'green': GREEN, 'purple': PURPLE, 'blue': BLUE}[m.get('kind', 'red')]
            present = m.get('old', True) if view == 'old' else m.get('new', True)
            shp = [P(p) for p in m['shape']] if m.get('shape') else None
            at = P(m['at']) if m.get('at') else (P(((min(p[0] for p in m['shape']) + max(p[0] for p in m['shape'])) / 2, (min(p[1] for p in m['shape']) + max(p[1] for p in m['shape'])) / 2)) if m.get('shape') else None)
            if m.get('kind') in ('green', 'purple') and not present: continue
            if m.get('kind') == 'green':
                dx, dy = DIRS[m.get('side', 'N')]; tip = (at[0] + dx * m.get('gap', 44), at[1] + dy * m.get('gap', 44)); frm = (tip[0] + dx * 40, tip[1] + dy * 40)
                numbered(d, tip, frm, m['n'], col); continue
            if shp:
                (d.line(shp + [shp[0]], fill=col, width=4) if present else dashed_poly(d, shp, col))
            dx, dy = DIRS[m.get('side', 'N')]; off = m.get('off', 62)
            if shp:   # tip on the shape edge facing the arrow
                xs = [p[0] for p in shp]; ys = [p[1] for p in shp]; cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
                hw, hh = (max(xs) - min(xs)) / 2, (max(ys) - min(ys)) / 2; tip = (cx + dx * hw * (1 if abs(dx) > .1 else 0), cy + dy * hh * (1 if abs(dy) > .1 else 0)); tip = (cx + dx * hw, cy + dy * hh) if abs(dx) > .1 and abs(dy) < .1 else ((cx, cy + dy * hh) if abs(dx) < .1 else (cx + dx * hw, cy + dy * hh))
            else: tip = at
            frm = (tip[0] + dx * off, tip[1] + dy * off); numbered(d, tip, frm, m['n'], col)
        ims[view] = im
    return ims['old'], ims['new'], pg

def tile(im, n, gap=14):
    """cut a tall image into n vertical slices placed side by side (so a long column stays readable)"""
    h = im.height // n + 1; out = Image.new('RGB', (im.width * n + gap * (n - 1), h), (255, 255, 255))
    for i in range(n): out.paste(im.crop((0, i * h, im.width, min((i + 1) * h, im.height))), (i * (im.width + gap), 0))
    return out

# ---------------------------------------------------------------- deck v2: label beside each mark, no legend
def _font(px): return ImageFont.truetype(FB, int(px))
def tagged(d, tip, side, off, text, col, fpx, w, placed=None):
    f = _font(fpx); f2 = _font(fpx * .85); lines = text.split('\n'); fonts = [f] + [f2] * (len(lines) - 1)
    bw = max(d.textlength(l, font=ft) for l, ft in zip(lines, fonts)) + fpx * .6; bh = fpx * 1.2 + (len(lines) - 1) * fpx * .95 + fpx * .3
    dx, dy = DIRS[side]; n = math.hypot(dx, dy) or 1; dx, dy = dx / n, dy / n; W, H = d.im.size
    cx = tip[0] + dx * (off + (bw / 2 if abs(dx) > .3 else 0)); cy = tip[1] + dy * (off + (bh / 2 if abs(dy) > .3 else 0))
    if abs(dx) > .3 and abs(dy) <= .3: cy = tip[1]
    if abs(dy) > .3 and abs(dx) <= .3: cx = tip[0]
    def rect(cx, cy): return [cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2]
    def clampc(cx, cy): return min(max(cx, bw / 2 + 2), W - bw / 2 - 2), min(max(cy, bh / 2 + 2), H - bh / 2 - 2)
    cx, cy = clampc(cx, cy)
    for _ in range(14):
        r = rect(cx, cy)
        if not any(not (r[2] < p[0] or r[0] > p[2] or r[3] < p[1] or r[1] > p[3]) for p in (placed or [])): break
        if abs(dx) > .3 and abs(dy) <= .3: cy += bh * 1.05 * (1 if cy < H / 2 else -1)
        else: cx += bw * 1.05 * (1 if cx < W / 2 else -1)
        cx, cy = clampc(cx, cy)
    r = rect(cx, cy)
    if placed is not None: placed.append(r)
    px = min(max(tip[0], r[0]), r[2]); py = min(max(tip[1], r[1]), r[3])
    arrow(d, tip, (px, py), col, w=w)
    d.rectangle(r, fill=(255, 255, 255), outline=col, width=max(2, w - 1))
    y = r[1] + fpx * .15
    for l, ft in zip(lines, fonts): d.text((cx - d.textlength(l, font=ft) / 2, y), l, fill=col, font=ft); y += fpx * (1.0 if ft is f else .95)
def render2(box, marks, S, page=None, fpx_override=None, padr=0):
    pg = page or page_of(box); out = {}
    W = (box[2] - box[0]) * S; fpx = fpx_override or max(22, .025 * W); lw = max(4, int(.0035 * W) if not fpx_override else 5)
    for view in ('old', 'new'):
        im = crop_old(pg, box, S) if view == 'old' else crop_ai(box, S)
        if padr: big = Image.new('RGB', (im.width + padr, im.height), (255, 255, 255)); big.paste(im, (0, 0)); im = big
        d = ImageDraw.Draw(im)
        P = lambda p: ((p[0] - box[0]) * S, (p[1] - box[1]) * S); placed = []
        for m in marks:
            col = {'red': RED, 'purple': PURPLE}[m.get('kind', 'red')]; present = m.get('old', True) if view == 'old' else m.get('new', True)
            if m.get('kind') == 'purple' and not present: continue
            txt = m['t']
            if not present: txt += '\n' + ('Approx. former location' if m.get('absent') == 'former' else m.get('note', 'Approx. position, not drawn'))
            elif m.get('absent') == 'both': txt += ''
            if m.get('absent') == 'both': txt = m['t'] + '\n' + m.get('note', 'Approx. position, not drawn')
            if m.get('shape'):
                shp = [P(p) for p in m['shape']]
                (d.line(shp + [shp[0]], fill=col, width=lw) if present and m.get('absent') != 'both' else dashed_poly(d, shp, col, w=lw, on=int(fpx * .6), off=int(fpx * .4)))
                xs = [p[0] for p in shp]; ys = [p[1] for p in shp]; cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2; hw, hh = (max(xs) - min(xs)) / 2, (max(ys) - min(ys)) / 2
                dx, dy = DIRS[m.get('side', 'N')]; n = math.hypot(dx, dy) or 1; tip = (cx + dx / n * hw, cy + dy / n * hh)
            else: tip = P(m['at'])
            tagged(d, tip, m.get('side', 'N'), m.get('off', 40), txt, col, fpx, lw, placed)
        out[view] = im
    return out['old'], out['new'], pg
