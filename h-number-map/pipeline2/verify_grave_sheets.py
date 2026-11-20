"""Checks on the grave sheets (run after build_grave_sheets.py):
  a  every workbook grave of every drawn lot has its ID in the sheet's text layer exactly once, and no other ID is printed
  b  every printed ID resolves with decoder v2 (decode_h on id // 10) to the section, lot and grave digit of its record, and the record id says the same
  c  the printed text is >= 6.5 pt (font size in the PDF) and a sample of 80 IDs, rendered at 4x, has digit ink >= 4.5 pt high
  d  lots the decoder numbers but the drawing does not show (reserved IDs, not drawn)
Writes crosswalk/grave_sheets_verification.txt."""
import csv, glob, os, re, sys, random, collections
import numpy as np
import pymupdf as fitz
from common import *
sys.path.insert(0, os.path.join(REPO, 's4')); import s4decoder1 as DEC
OUT = os.path.join(REPO, 'h-number-map'); PDF = os.path.join(OUT, 'site', 'pdf'); log = []; fail = collections.Counter()
def say(t): log.append(t); print(t)
rows = list(csv.DictReader(open(os.path.join(OUT, 'grave_positions_JKM.csv'))))
printed = collections.defaultdict(list); sizes = []; spans_by = {}
for sec in 'JKM':
    doc = fitz.open(os.path.join(PDF, 'Cedar_Grove_Grave_IDs_%s.pdf' % sec))
    for pn, p in enumerate(doc):
        for b in p.get_text('dict')['blocks']:
            for l in b.get('lines', []):
                for s in l['spans']:
                    t = s['text'].strip()
                    if re.fullmatch(r'H\d{7}', t): printed[(sec, t)].append(pn + 1); sizes.append(s['size']); spans_by[(sec, t)] = (pn, fitz.Rect(s['bbox']), l['dir'])
want = {(r['section'], r['v2_h_grave']): r for r in rows}
missing = [k for k in want if len(printed.get(k, [])) == 0]; dup = [k for k in want if len(printed.get(k, [])) > 1]; extra = [k for k in printed if k not in want]
say('a. %d workbook graves (J %d, K %d, M %d); printed exactly once: %d; missing %d; printed more than once %d; printed but not a workbook grave %d' % (
    len(want), sum(1 for k in want if k[0] == 'J'), sum(1 for k in want if k[0] == 'K'), sum(1 for k in want if k[0] == 'M'), len(want) - len(missing) - len(dup), len(missing), len(dup), len(extra)))
for k in (missing + dup + extra)[:20]: say('   ' + str(k))
fail['missing'] = len(missing); fail['duplicate'] = len(dup); fail['extra'] = len(extra)
wrong = 0
for (sec, t), r in want.items():
    n = int(t[1:]); lot_h, g = divmod(n, 10); d = DEC.decode_h(lot_h); m = re.match(r'CEDARGROVE-(\w)-(\w+)-(\d+)-?$', r['record_id'])
    ok = d and d['section'] == sec == r['section'] and d['lot_label'] == r['lot_label'] and g == int(r['grave']) and m and (m.group(1), m.group(2), int(m.group(3))) == (sec, r['lot_label'], g)
    if not ok: wrong += 1; say('   wrong: %s %s' % (t, r['record_id']))
say('b. %d IDs resolve with decoder v2 to the record\'s section, lot and grave; IDs pointing to the wrong place: %d' % (len(want) - wrong, wrong)); fail['wrong'] = wrong
mn = min(sizes); say('c. printed ID font size: min %.2f pt, max %.2f pt over %d IDs; below 6.5 pt: %d' % (mn, max(sizes), len(sizes), sum(1 for s in sizes if s < 6.49))); fail['small'] = sum(1 for s in sizes if s < 6.49)
random.seed(3); keys = random.sample([k for k in spans_by if abs(spans_by[k][2][0]) > .99], 80); inks = []
docs = {s: fitz.open(os.path.join(PDF, 'Cedar_Grove_Grave_IDs_%s.pdf' % s)) for s in 'JKM'}
for k in keys:
    pn, bb, d = spans_by[k]; pix = docs[k[0]][pn].get_pixmap(dpi=288, clip=bb + (-1, -1, 1, 1)); a = np.frombuffer(pix.samples, np.uint8).reshape(pix.h, pix.w, pix.n)[..., :3].astype(int)
    dark = (a.sum(2) < 200); rowsd = np.where(dark.any(1))[0]
    if len(rowsd): inks.append((rowsd.max() - rowsd.min() + 1) / 4.0)
say('   sample of %d horizontal IDs rendered at 4x: ink height min %.2f pt, median %.2f pt (digits of a 6.5 pt font are 4.7 pt)' % (len(inks), min(inks), float(np.median(inks)))); fail['ink'] = sum(1 for v in inks if v < 4.4)
nd = []
for sec in 'JKM':
    drawn = {r['lot_label'] for r in rows if r['section'] == sec}
    for r in DEC.full_table(sec):
        if r['lot_label'] not in drawn: nd.append((sec, r['lot_label'], r['h_lot']))
say('d. numbered by the decoder but not drawn (reserved IDs, no lot, no grave sheet): ' + (', '.join('%s %s %s' % x for x in nd) or 'none'))
tot = collections.Counter(r['status'] for r in rows)
say('   status totals: ' + str(dict(tot)))
open(os.path.join(OUT, 'crosswalk', 'grave_sheets_verification.txt'), 'w').write('\n'.join(log) + '\n\nfailures: %s\n' % dict(fail))
print('failures', dict(fail)); sys.exit(1 if sum(fail.values()) else 0)
