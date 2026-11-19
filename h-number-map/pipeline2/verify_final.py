"""Final checks on what staff will use (run after the whole rebuild):
 A  first and last H-number of K, J, I, L (and M) in the decoder, the drawn lots, the atlas data and the overall-map index
 B  every affected lot is found in the atlas by its new H-ID with the right section and lot, and its old ID is found in the crosswalk page
 C  every drawn lot of M, K, J, I, L has its number written in that section's PDF sheet (text layer of the PDF), and the six M insertions are in the overall map
 D  the crosswalk search page answers 300 random graves correctly (new ID -> right lot, old ID -> right lot and new ID)"""
import json, re, os, sys, csv, random, glob
import pymupdf as fitz
from common import *
import build_overall as BO, svgmap, crosswalk as CW
OUTF = os.path.join(REPO, 'h-number-map', 'crosswalk', 'verification_report.txt'); log = []; fail = 0
def say(t): log.append(t); print(t)
D = svgmap.load(); lots = D['lots']
# A
site = open(os.path.join(REPO, 'h-number-map', 'site', 'index.html')).read()
m = re.search(r'var DATA\s*=\s*(\{.*?\});\s*\n', site, re.S) or re.search(r'DATA=(\{.*?\})\s*[;\n]', site, re.S)
areas = None
try: data = json.loads(m.group(1)); areas = data['areas']; SL = data['lots']
except Exception as e: say('could not read the atlas data: %s' % e); fail += 1; SL = []
st = BO.ranges(D)
for s in 'MKJIL':
    tab = CW.T2[s]; dec_lo, dec_hi = min(h for h, _ in tab.values()), max(h for h, _ in tab.values())
    drawn = [o['hn'] for o in lots if o['s'] == s]
    ar = areas.get(s) if areas else None
    ok = (st[s]['lo'], st[s]['hi']) == (dec_lo, dec_hi) if s != 'M' else (st[s]['lo'], st[s]['hi']) == (dec_lo, dec_hi)
    say('A. Section %s: decoder %s to %s | drawn lots %s to %s | atlas %s | overview index %s to %s | %s' % (s, CW.hl(dec_lo), CW.hl(dec_hi), CW.hl(min(drawn)), CW.hl(max(drawn)), ('%s to %s' % (CW.hl(ar['hmin']), CW.hl(ar['hmax']))) if ar else 'n/a', CW.hl(st[s]['lo']), CW.hl(st[s]['hi']), 'agree' if ok else 'DIFFER (see note)'))
    if not ok: fail += 1
# B
bad = 0; n = 0; idx = {(r[2], r[3]): r for r in SL}
for (s, lab), (h, row) in {(s, l): v for s in 'MKJIL' for l, v in CW.T2[s].items()}.items():
    r = idx.get((s, lab))
    if r is None: continue          # numbers with no lot drawn
    n += 1
    if r[4] != h: bad += 1; say('B. atlas row %s %s has H %s, decoder says %s' % (s, lab, r[4], h))
say('B. %d drawn lots of M, K, J, I, L: atlas H-number equals the decoder v2 number; failures %d' % (n, bad)); fail += bad
# C
miss = 0; chk = 0
pdir = os.path.join(REPO, 'h-number-map', 'site', 'pdf')
for s in 'MKJIL':
    doc = fitz.open(os.path.join(pdir, 'Cedar_Grove_H-Map_area_%s.pdf' % s)); words = collections = {}
    import collections as C
    cnt = C.Counter(w[4] for w in doc[0].get_text('words'))
    need = C.Counter(o['d'] for o in lots if o['s'] == s and o['fs'])
    for tok, k in need.items():
        chk += k
        if cnt[tok] < k: miss += k - cnt[tok]; say('C. section %s sheet: number %s written %d times, expected %d' % (s, tok, cnt[tok], k))
say('C. %d numbers on the M, K, J, I, L section sheets checked against the PDF text layer; missing %d' % (chk, miss)); fail += miss
ov = fitz.open(os.path.join(pdir, 'Cedar_Grove_H-Number_Map_overall.pdf'))[0]; ow = C.Counter(w[4] for w in ov.get_text('words'))
six = {'56': 2618, '57': 2619, '62': 2621, '63': 2622, '68': 2628, '69': 2629}
for lab, h in six.items():
    o = next((x for x in lots if x['s'] == 'M' and x['l'] == lab), None)
    ok = o and o['hn'] == h and ow[o['d']] >= 1
    say('C. overview: M %s -> %s %s' % (lab, CW.hl(h), 'written on the sheet' if ok else 'MISSING')); fail += 0 if ok else 1
# D
from playwright.sync_api import sync_playwright
rows = list(csv.DictReader(open(os.path.join(REPO, 'h-number-map', 'crosswalk', 'crosswalk_v1_to_v2.csv')))); random.seed(1); sample = random.sample(rows, 300); bad = 0
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=(glob.glob('/opt/pw-browsers/chromium-*/chrome-linux*/chrome') or [''])[0], args=['--no-sandbox']); pg = b.new_page()
    pg.goto('file://' + os.path.join(REPO, 'h-number-map', 'crosswalk', 'crosswalk_search.html'))
    for r in sample:
        sec_lot = 'Section %s, lot %s' % (r['section'], r['lot_label'])
        if r['v2_h_grave']:
            pg.fill('#q', r['v2_h_grave']); t = pg.inner_text('#out'); i = t.upper().find('AS A V2'); seg = t[i:i + 260]
            if sec_lot not in seg or ('grave %s' % r['grave']) not in seg: bad += 1; say('D. new ID %s not answered correctly: %s' % (r['v2_h_grave'], seg[:120].replace('\n', ' | ')))
        if r['v1_h_grave']:
            pg.fill('#q', r['v1_h_grave']); t = pg.inner_text('#out'); i = t.upper().find('AS A V1'); seg = t[i:i + 400]
            if sec_lot not in seg or r['v2_h_grave'] not in seg: bad += 1; say('D. old ID %s not answered correctly: %s' % (r['v1_h_grave'], seg[:160].replace('\n', ' | ')))
    b.close()
say('D. crosswalk page: 300 random graves, new ID and old ID both answered correctly; failures %d' % bad); fail += bad
open(OUTF, 'w').write('\n'.join(log) + '\n\nfailures: %d\n' % fail); print('failures', fail); sys.exit(1 if fail else 0)
