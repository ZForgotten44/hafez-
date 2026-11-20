import sys, json
from dlib import *
import make_assets as MA
bx, R, c, cellmark = MA.bx, MA.R, MA.c, MA.cellmark
OUT2 = os.path.join(HERE, 'assets2'); os.makedirs(OUT2, exist_ok=True)
def mk(t, shape=None, at=None, side='N', off=36, **k): return dict(t=t, shape=shape, at=at, side=side, off=off, **k)
def cm(t, tok, near, side='N', off=36, **k):
    u = unnum(tok, near); return dict(t=t, shape=poly(u['cell']), side=side, off=off, **k)
S2 = {}
S2['Q1'] = dict(box=(1250, 291, 1346, 345), S=14, page=9, marks=[mk('M 11', R([1323.5, 298.1, 1332, 321]), side='N', old=True, new=False, absent='former'),
    mk('M 12', R([1322.3, 321.1, 1331.1, 335.5]), side='E', old=True, new=False, absent='former'), mk('M 16', R([1313.2, 320.8, 1322, 335]), side='S', old=True, new=False, absent='former'),
    mk('Saint Joseph symbol', at=(1331, 314.4), side='E', kind='purple', old=False, new=True), mk('Parking', at=(1337, 343), side='SW', kind='purple', old=False, new=True, off=30)])
six = MA.six
def col2(t, a, b): return mk(t, bx(((six[a][0] + six[b][0]) / 2, (six[a][1] + six[b][1]) / 2), 4.4, 10.6), side='S', off=30, old=False, new=True, absent='pos', note='Approx. position')
S2['Q2'] = dict(box=(1190, 308, 1290, 378), S=16, page=9, marks=[dict(col2('M 56 over 57', '56', '57'), off=30), dict(col2('M 62 over 63', '62', '63'), off=95), dict(col2('M 68 over 69', '68', '69'), off=160)])
S2['Q3'] = dict(box=(1350, 340, 1460, 398), S=13, marks=[mk('B 390A', R([1402.9, 376.1, 1411.9, 387.5]), side='W', off=50, old=True, new=False, absent='former'), mk('B 390B', R([1402.9, 365.1, 1411.7, 376.1]), side='W', off=50, old=True, new=False, absent='former'),
    mk('B 390C', R([1403.8, 348.9, 1412.7, 365.1]), side='W', off=50, old=True, new=False, absent='former')])
S2['Q4'] = dict(box=(1380, 505, 1490, 567), S=13, marks=[mk('B 289', R([1444.4, 541.1, 1455.2, 551.7]), side='E', off=40, old=False, new=False, absent='both'), mk('B 290', R([1444.4, 530.5, 1455.2, 541.1]), side='NE', off=40, old=False, new=False, absent='both')])
S2['Q5'] = dict(box=(1375, 392, 1470, 428), S=13, marks=[mk(l, bx((unit('B', l)[0], unit('B', l)[1] + 1.2), 5.5, 3.4), side='N', off=30) for l in ('372H', '354H', '336H', '318H')])
S2['Q6'] = dict(box=(1598, 884, 1668, 916), S=17, marks=[mk('A 20H', R([1633.9, 895.5, 1645.7, 899.9]), side='N', off=22, note='Approx. position', old=False, new=False, absent='both'), mk('A 39H', R([1616.3, 895.3, 1628.1, 899.6]), side='W', off=24, note='Approx. position', old=False, new=False, absent='both'),
    mk('A 1H (drawn)', R([1647.3, 901, 1659.1, 905.7]), side='S', off=30)])
S2['Q8'] = dict(manual=1, box=(640, 316, 835, 356), S=14, stack=737, fpx=30, marks=[mk('L 1-13', at=(773, 329), side='N', off=40), mk('L 14', poly(unnum('14', (732, 334))['cell']), side='W', off=30, old=False, new=True, absent='former'),
    mk('L 19', poly(unnum('19', (686, 339))['cell']), side='S', off=30, old=False, new=True, absent='former'), mk('L 21', poly(unnum('21', (651, 334))['cell']), side='N', off=34)])
S2['Q9'] = dict(box=(1370, 538, 1440, 584), S=18, marks=[mk('A362', poly(1557), side='W', off=34), mk('A361', poly(1637), side='W', off=34), mk('unlabelled', poly(1467), side='W', off=34)])
S2['Q10'] = dict(box=(1608, 418, 1700, 462), S=17, marks=[mk('B 20H', bx(unit('B', '20H'), 5.5, 3.8), side='NE', off=34), mk('B 20', bx(MA.b20, 5.5, 3.8), side='E', off=40), mk('B 19A', bx(unit('B', '19A'), 5.5, 3.8), side='E', off=40)])
S2['Q11'] = dict(manual=1, box=(1395, 790, 1470, 855), S=18, padr=300, fpx=34, marks=[cm('312A', '312A', (1422, 808), 'E', 800), cm('293A', '293A', (1439, 808), 'E', 520), cm('unlabelled strip', '', (1439, 819), 'E', 520), cm('291A', '291A', (1438, 831), 'E', 520)])
S2['Q12'] = dict(box=(790, 348, 870, 386), S=18, marks=[mk('Unlabelled lot', poly(371), side='N', off=34)])
S2['Q13'] = dict(box=(1072, 401, 1150, 438), S=20, page=4, marks=[mk('D 311', bx(c('D', '311'), 6, 5.2), side='E', off=34), mk('D 322', bx(c('D', '322'), 6, 5.2), side='S', off=34), mk('D 333', bx(c('D', '333'), 6, 5.2), side='S', off=34)])
S2['Q14'] = dict(box=(1170, 758, 1262, 796), S=14, marks=[mk('C 237H', bx(c('C', '237H'), 6, 4.5), side='N', off=34), mk('C 218H', bx(c('C', '218H'), 6, 4.5), side='N', off=34), mk('C 161H', bx(c('C', '161H'), 6, 4.5), side='N', off=34)])
S2['Q15'] = dict(box=(1360, 405, 1412, 645), S=16, tile=3, fpx=52, manual=1, marks=[mk('B 395', at=(1387, 630), side='E', off=30), mk('B 414', at=(1380, 418), side='E', off=30)])
S2['Q16'] = dict(box=(1612, 496, 1700, 538), S=18, marks=[mk('B 12', bx(c('B', '12'), 6, 4.2), side='E', off=40)])
S2['Q17'] = dict(box=(1105, 472, 1180, 508), S=22, marks=[mk('D 293', bx(c('D', '293'), 6, 4.2), side='E', off=36)])
def q7():
    import pymupdf as fitz
    p = fitz.open(OLD)[10]; pm = p.get_pixmap(dpi=300, clip=fitz.Rect(440, 58, 720, 190)); o = Image.frombytes('RGB', (pm.width, pm.height), pm.samples); d = ImageDraw.Draw(o)
    tagged(d, (272, 428), 'SW', 60, 'Hatched building', RED, 34, 5)
    n = crop_ai((1290, 318, 1375, 372), 14); d2 = ImageDraw.Draw(n)
    tagged(d2, (560, 300), 'N', 40, 'Hatched building', RED, 34, 5); tagged(d2, (470, 395), 'SW', 50, 'Accessible parking', PURPLE, 34, 5)
    o.save(os.path.join(OUT2, 'Q7_old.png')); n.save(os.path.join(OUT2, 'Q7_new.png'))
def stack(im, box, cut, S): return MA.stack(im, box, cut, S)
def autobox(s, aspect=1.15):
    xs = []; ys = []
    for mk_ in s['marks']:
        pts = mk_['shape'] if mk_.get('shape') else [mk_['at']]
        xs += [p[0] for p in pts]; ys += [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs) - 24, max(xs) + 24, min(ys) - 17, max(ys) + 17
    w, h = x1 - x0, y1 - y0
    if w / h < aspect: x0 -= (h * aspect - w) / 2; x1 += (h * aspect - w) / 2
    else: y0 -= (w / aspect - h) / 2; y1 += (w / aspect - h) / 2
    return (x0, y0, x1, y1)
def run():
    for q, s in S2.items():
        if not s.get('manual'): s['box'] = autobox(s); s['S'] = max(s['S'], 1100 / (s['box'][2] - s['box'][0]))
        o, n, pg = render2(s['box'], s['marks'], s['S'], page=s.get('page'), fpx_override=s.get('fpx'), padr=s.get('padr', 0))
        if s.get('stack'): o, n = stack(o, s['box'], s['stack'], s['S']), stack(n, s['box'], s['stack'], s['S'])
        if s.get('tile'): o, n = tile(o, s['tile']), tile(n, s['tile'])
        o.save(os.path.join(OUT2, q + '_old.png')); n.save(os.path.join(OUT2, q + '_new.png')); print(q, pg, o.size)
    q7()
if __name__ == '__main__': run()
