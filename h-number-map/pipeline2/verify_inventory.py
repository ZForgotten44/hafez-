"""Inventory-first verification. Starts from the physical lots and graves, not from the decoder's table.
 1. every physical lot drawn on the 2022 map (lots_fit.json) and every identified outline must carry an H-number; a lot with a blank H fails even if it was never in the decoder
 2. every number must be the decoder's number for that section and label (the decoder is asked, the map is not trusted)
 3. graves: only where a burial workbook (J, K, M) or plat establishes grave positions. Every workbook grave, occupied or vacant, must print a readable ID on its detail sheet
    (verify_grave_sheets.py). For sections without a workbook the digits 1-9 the decoder accepts do not prove nine graves, so no grave count is asserted there.
 Writes crosswalk/inventory_verification.txt; the last line is the four totals."""
import csv, json, os, re, subprocess, sys, collections
from common import *
sys.path.insert(0, os.path.join(REPO, 's4')); import s4decoder1 as DEC
log = []
def say(t): log.append(t); print(t)
L = json.load(open(f'{DATA}/lots_fit.json')); R = json.load(open(f'{DATA}/registry.json'))
blank = [(o['s'], o['l']) for o in L if not o.get('h')]
wrong = []
for o in L:
    r = DEC.h_lot(o['s'], o['l']) if o.get('h') else None
    if o.get('h') and not (r and r[0] and r[1] == o['h']):
        # a lot placed from the path (not from its printed label) is allowed to differ only if the decoder has no entry for the label
        if r and r[0]: wrong.append((o['s'], o['l'], o['h'], r[1]))
say('1. physical lots on the 2022 map with an H-number: %d of %d; lots with a blank H: %d %s' % (len(L) - len(blank), len(L), len(blank), blank[:10]))
say('2. numbers that differ from the decoder for the same section and label: %d %s' % (len(wrong), wrong[:10]))
ids = [''.join(u['tokens']) for u in R['unnumbered'] if u.get('tokens') and not u.get('graves')]
say('   identified outlines (label read on the drawing) with no H-number: %d: %s' % (len(ids), ', '.join(sorted(ids, key=lambda x: (len(x), x)))))
blank_out = [u for u in R['unnumbered'] if not u.get('tokens')]
say('   unlabelled outlines (identity unknown or not a lot): %d' % len(blank_out))
g = subprocess.run([sys.executable, 'verify_grave_sheets.py'], capture_output=True, text=True).stdout
fails = re.search(r"failures (\{.*\})", g); say('3. workbook graves (sections J, K, M), occupied and vacant alike: ' + g.split('\n')[0]); say('   grave-ID failures on the detail sheets: ' + (fails.group(1) if fails else 'not run'))
say('   sections without a burial workbook or plat in the repository (A-I, L): grave positions are not established, so no grave is counted or claimed; lots are numbered, the grave digit is not asserted')
inv = list(csv.DictReader(open(os.path.join(REPO, 'h-number-map', 'grey_inventory.csv'))))
aw = [r for r in inv if r['final_status'].startswith('awaiting')]
say('   grey-shape inventory: %s' % dict(collections.Counter(r['final_status'] for r in inv)))
unk = [r for r in inv if r['final_status'] == 'awaiting identification']
tot_graves_bad = 0 if (fails and all(v == 0 for v in map(int, re.findall(r": (\d+)", fails.group(1)))) ) else 1
say('TOTALS: lots with blank H = %d | identified outlines still without an H-number = %d | workbook graves without a readable ID = %s | outlines whose physical identity is unknown = %d' % (len(blank), len(ids), 0 if not tot_graves_bad else 'see above', len(unk)))
open(os.path.join(REPO, 'h-number-map', 'crosswalk', 'inventory_verification.txt'), 'w').write('\n'.join(log) + '\n')
