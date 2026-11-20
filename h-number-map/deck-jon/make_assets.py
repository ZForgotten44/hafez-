import sys, json
from dlib import *
OUTD = os.path.join(HERE, 'assets'); os.makedirs(OUTD, exist_ok=True)
def bx(c, hw=5.5, hh=5.0): return [(c[0] - hw, c[1] - hh), (c[0] + hw, c[1] - hh), (c[0] + hw, c[1] + hh), (c[0] - hw, c[1] + hh)]
def R(b): return [(b[0], b[1]), (b[2], b[1]), (b[2], b[3]), (b[0], b[3])]
def g(n, sec, lab, side='N', **k):
    return dict(n=n, kind='green', at=unit(sec, lab), side=side, **k)
def cellmark(n, tok, near, side='N', **k):
    c = unnum(tok, near); return dict(n=n, shape=poly(c['cell']), side=side, **k)
specs = {}
specs['Q1'] = dict(box=(1250, 291, 1346, 345), S=14, page=9, marks=[
    dict(n='1', shape=R([1323.5, 298.1, 1332, 321]), old=True, new=False, side='N', off=50), dict(n='2', shape=R([1322.3, 321.1, 1331.1, 335.5]), old=True, new=False, side='E', off=50),
    dict(n='3', shape=R([1313.2, 320.8, 1322, 335]), old=True, new=False, side='S', off=50),
    dict(n='4', kind='purple', at=(1331, 314.4), old=False, new=True, side='E', off=55), dict(n='5', kind='purple', at=(1337, 343), old=False, new=True, side='N', off=50),
    g('A', 'M', '14', 'W'), g('B', 'M', '15', 'W')])
six = {'56': (1253.6, 329.7), '57': (1253.6, 340.8), '62': (1244.5, 329.5), '63': (1244.5, 340.5), '68': (1235.4, 329.1), '69': (1235.4, 340.1)}
specs['Q2'] = dict(box=(1190, 308, 1290, 357), S=16, page=9, marks=[dict(n=k, shape=bx(c, 4.4, 5.1), old=False, new=True, side='S', off=45 + 28 * (i % 2)) for i, (k, c) in enumerate(six.items())] +
    [g('A', 'M', '55', 'E'), g('B', 'M', '61', 'E'), g('C', 'M', '67', 'E')])
specs['Q3'] = dict(box=(1350, 340, 1460, 398), S=13, marks=[dict(n='1', shape=R([1402.9, 376.1, 1411.9, 387.5]), old=True, new=False, side='W', off=70), dict(n='2', shape=R([1402.9, 365.1, 1411.7, 376.1]), old=True, new=False, side='W', off=70),
    dict(n='3', shape=R([1403.8, 348.9, 1412.7, 365.1]), old=True, new=False, side='W', off=70), g('A', 'B', '390', 'S'), g('B', 'B', '391', 'S'), g('C', 'B', '389', 'S')])
specs['Q4a'] = dict(box=(1380, 505, 1490, 567), S=13, marks=[dict(n='1', shape=R([1444.4, 541.1, 1455.2, 551.7]), old=False, new=False, side='E', off=55), dict(n='2', shape=R([1444.4, 530.5, 1455.2, 541.1]), old=False, new=False, side='E', off=55),
    dict(n='3', kind='purple', at=(1441, 537), side='W', off=55), dict(n='4', kind='purple', at=(1420, 538), side='S', off=50), g('A', 'B', '288', 'E'), g('B', 'B', '291', 'E')])
four = [('362H', (1394, 520)), ('344H', (1409, 519)), ('326H', (1424, 520)), ('308H', (1438, 519))]
nb = ['363', '345', '327', '309']
specs['Q4b'] = dict(box=(1375, 497, 1465, 543), S=14, marks=[cellmark(str(i + 1), t, p, 'S', off=42) for i, (t, p) in enumerate(four)])
hl = ['372H', '354H', '336H', '318H']
specs['Q5a'] = dict(box=(1375, 399, 1470, 428), S=13, marks=[dict(n=str(i + 1), shape=bx((unit('B', l)[0], unit('B', l)[1] + 1.2), 5.5, 3.4), side='S', off=45) for i, l in enumerate(hl)] + [g('A', 'B', '300H', 'S')])
try: b20 = unit('B', '20')
except KeyError: b20 = (1654.5, 432.2)
print('B20', b20)
specs['Q5b'] = dict(box=(1608, 418, 1700, 462), S=17, marks=[dict(n='1', shape=bx(unit('B', '40H'), 5.5, 3.8), side='N', off=45), dict(n='2', shape=bx(unit('B', '40'), 5.5, 3.8), side='S', off=45),
    dict(n='3', shape=bx(unit('B', '20H'), 5.5, 3.8), side='N', off=45), dict(n='4', shape=bx(b20, 5.5, 3.8), side='E', off=50)])
specs['Q10'] = dict(box=(1608, 418, 1700, 462), S=17, marks=[dict(n='1', shape=bx(unit('B', '20H'), 5.5, 3.8), side='N', off=45), dict(n='2', shape=bx(b20, 5.5, 3.8), side='E', off=50), dict(n='3', shape=bx(unit('B', '19A'), 5.5, 3.8), side='E', off=50),
    g('A', 'B', '19', 'W'), g('B', 'B', '18', 'W'), g('C', 'B', '40', 'S')])
c = lambda sec, lab: unit(sec, lab)
specs['Q6'] = dict(box=(1598, 884, 1668, 916), S=17, marks=[dict(n='1', shape=R([1633.9, 895.5, 1645.7, 899.9]), old=False, new=False, side='N', off=40), dict(n='2', shape=R([1616.3, 895.3, 1628.1, 899.6]), old=False, new=False, side='N', off=40),
    dict(n='3', shape=R([1603.5, 894.8, 1615.2, 899.2]), old=False, new=False, side='N', off=40), dict(n='4', shape=R([1647.3, 901, 1659.1, 905.7]), side='N', off=48, kind='red'),
    g('A', 'A', '20', 'S'), g('B', 'A', '39', 'S'), g('C', 'A', '58', 'S')])
specs['Q8'] = dict(box=(640, 316, 835, 356), S=10, stack=737, marks=[dict(n='1', kind='red', at=(775, 336), side='N', off=45),
    dict(n='2', shape=poly(unnum('14', (732, 334))['cell']), old=False, side='S', off=42), dict(n='3', shape=poly(unnum('19', (686, 339))['cell']), old=False, side='S', off=42),
    dict(n='4', shape=poly(unnum('21', (651, 334))['cell']), side='N', off=45), g('A', 'K', '13', 'S')])
specs['Q9'] = dict(box=(1370, 538, 1440, 584), S=18, marks=[dict(n='1', shape=poly(1467), side='W', off=52), dict(n='2', shape=poly(1557), side='W', off=52), dict(n='3', shape=poly(1637), side='W', off=52), g('A', 'B', '362', 'E'), g('B', 'B', '361', 'E')])
uA = unnum('', (1439, 819))
specs['Q11a'] = dict(box=(1395, 800, 1470, 845), S=18, marks=[cellmark('1', '312A', (1422, 808), 'W', off=48), cellmark('2', '293A', (1439, 808), 'E', off=48), dict(n='3', shape=poly(uA['cell']), side='E', off=48), cellmark('4', '291A', (1438, 831), 'E', off=48),
    g('A', 'A', '312', 'W'), g('B', 'A', '293', 'W'), g('C', 'A', '291', 'W')])
specs['Q11b'] = dict(box=(1488, 706, 1538, 742), S=22, marks=[cellmark('1', '204A', (1516, 722), 'E', off=48), g('A', 'A', '204', 'W'), g('B', 'A', '203H', 'S')])
specs['Q12'] = dict(box=(790, 348, 870, 386), S=18, marks=[dict(n='1', shape=poly(371), side='N', off=50), g('A', 'G', '58', 'S'), g('B', 'F', '210', 'S')])
specs['Q13a'] = dict(box=(1072, 401, 1150, 438), S=20, page=4, marks=[dict(n='1', shape=bx(c('D', '311'), 6, 5.2), side='E', off=50), dict(n='2', shape=bx(c('D', '322'), 6, 5.2), side='S', off=40), dict(n='3', shape=bx(c('D', '333'), 6, 5.2), side='S', off=40),
    g('A', 'D', '311H', 'N'), g('B', 'D', '310', 'E')])
specs['Q13b'] = dict(box=(1115, 400, 1185, 438), S=22, page=4, marks=[dict(n='1', shape=bx((c('D', '300H')[0], c('D', '300H')[1] + 2.6), 5.8, 3.4), side='N', off=45), dict(n='2', shape=bx((c('D', '280H')[0], c('D', '280H')[1] + 2.6), 5.8, 3.4), side='N', off=45)])
specs['Q14'] = dict(box=(1170, 758, 1262, 796), S=14, marks=[dict(n='1', shape=bx(c('C', '237H'), 6, 4.5), side='N', off=45), dict(n='2', shape=bx(c('C', '218H'), 6, 4.5), side='N', off=45), dict(n='3', shape=bx(c('C', '161H'), 6, 4.5), side='N', off=45)])
specs['Q15'] = dict(box=(1345, 405, 1425, 645), S=9, tile=3, marks=[dict(n='1', kind='red', at=(1387, 630), side='E', off=40), dict(n='2', kind='red', at=(1380, 418), side='E', off=40), g('A', 'B', '355', 'E'), g('B', 'B', '372', 'E')])
specs['Q16'] = dict(box=(1612, 496, 1700, 538), S=18, marks=[dict(n='1', shape=bx(c('B', '12'), 6, 4.2), side='W', off=50), g('A', 'B', '13', 'W'), g('B', 'B', '11', 'W')])
specs['Q17'] = dict(box=(1105, 472, 1180, 508), S=22, marks=[dict(n='1', shape=bx(c('D', '293'), 6, 4.2), side='E', off=50), g('A', 'D', '294', 'W'), g('B', 'D', '292', 'W')])
def stack(im, box, cut, S, gap=14):
    x = int(round((cut - box[0]) * S)); a, b = im.crop((0, 0, x, im.height)), im.crop((x, 0, im.width, im.height))
    out = Image.new('RGB', (max(a.width, b.width), a.height + b.height + gap), (255, 255, 255)); out.paste(a, (0, 0)); out.paste(b, (0, a.height + gap)); return out
def run(only=None):
    meta = {}
    for q, s in specs.items():
        if not s or (only and q not in only): continue
        o, n, pg = render(s['box'], s['marks'], s['S'], page=s.get('page'))
        if s.get('stack'): o, n = stack(o, s['box'], s['stack'], s['S']), stack(n, s['box'], s['stack'], s['S'])
        if s.get('tile'): o, n = tile(o, s['tile']), tile(n, s['tile'])
        o.save(os.path.join(OUTD, q + '_old.png')); n.save(os.path.join(OUTD, q + '_new.png')); meta[q] = dict(page=pg, box=s['box'], size=o.size)
        print(q, pg, o.size)
    return meta
if __name__ == '__main__': run(sys.argv[1:] or None)

def q7():
    import pymupdf as fitz
    d = fitz.open(OLD); p = d[10]; pm = p.get_pixmap(dpi=300, clip=fitz.Rect(440, 58, 720, 190)); o = Image.frombytes('RGB', (pm.width, pm.height), pm.samples); od = ImageDraw.Draw(o)
    numbered(od, (262, 432), (200, 505), '1', RED); numbered(od, (350, 452), (430, 520), '2', RED)
    box = (1290, 318, 1375, 372); n = crop_ai(box, 14); nd = ImageDraw.Draw(n)
    numbered(nd, (560, 300), (640, 200), '1', RED)           # hatched building
    numbered(nd, (470, 395), (400, 500), '3', PURPLE)        # accessible-parking symbol
    numbered(nd, (663, 352), (760, 440), '2', RED)           # small symbol east of the building (nearest object to the old leader end)
    o.save(os.path.join(OUTD, 'Q7_old.png')); n.save(os.path.join(OUTD, 'Q7_new.png')); print('Q7', o.size, n.size)
if __name__ == '__main__': q7()
