"""Bring grey_inventory.csv up to date with the current numbering: a shape whose cell now carries an H-number is marked numbered, and the totals are written.
final_status: numbered | native numbering (crypt) | not a grave | awaiting a number (lot identified) | awaiting identification"""
import csv, json, os, collections
from common import *
p = os.path.join(REPO, 'h-number-map', 'grey_inventory.csv'); rows = list(csv.DictReader(open(p)))
L = json.load(open(f'{DATA}/lots_fit.json')); byc = {o['cell']: o for o in L if o.get('cell') is not None}
out = []
for r in rows:
    o = byc.get(int(r['cell']))
    if o: fs, h = 'numbered', o['h']
    elif r['class'].startswith('(d) not an H grave'): fs, h = 'native numbering (crypt)', ''
    elif r['class'].startswith('(d)'): fs, h = 'not a grave', ''
    elif r['status'].startswith('awaiting'): fs, h = 'awaiting identification', ''
    else: fs, h = 'awaiting a number (lot identified)', ''
    r['final_status'] = fs; r['h_number'] = h
    if o and not r['status'].startswith('numbered'): r['identity'] = r['identity'] + ' [numbered in v2: %s %s = %s]' % (o['s'], o['l'], o['h'])
    out.append(r)
cols = list(rows[0].keys()) + [c for c in ('final_status', 'h_number') if c not in rows[0]]
with open(p, 'w', newline='') as f:
    w = csv.DictWriter(f, cols); w.writeheader(); w.writerows(out)
print(collections.Counter(r['final_status'] for r in out))
