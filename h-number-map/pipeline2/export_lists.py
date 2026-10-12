"""Step 11: plain CSV lists that go with the map (same registry the site and PDFs use)."""
import csv, json, os
from common import *
def run():
    R = json.load(open(f'{DATA}/registry.json')); L = json.load(open(f'{DATA}/lots_fit.json')); out = os.path.join(REPO, 'h-number-map')
    with open(f'{out}/verified_lots.csv', 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['h_number', 'legacy_section', 'legacy_lot', 'map_x', 'map_y', 'outline', 'section_evidence'])
        for o in sorted(L, key=lambda o: (o['hn'], o['h'])):
            w.writerow([o['h'], o['s'], o['l'], o['cx'], o['cy'], 'drawn' if o['poly'] else 'label only', 'two independent readings' if 'old_ocr_agrees' in o['ev'] else 'inferred from surrounding lots'])
    with open(f'{out}/unresolved_locations.csv', 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['kind', 'reason', 'h_number_candidate', 'legacy_section', 'legacy_lot', 'label_on_drawing', 'map_x', 'map_y', 'outline'])
        for r in R['review']:
            w.writerow(['visible lot, identity unresolved', ' | '.join(r.get('reasons', [])), r.get('htext', ''), r.get('section', ''), r.get('legacy', ''), ''.join(r['tokens']), r['pt'][0], r['pt'][1], r['geom']])
        for u in R['known_unplaced']:
            w.writerow(['known H-number, map position unresolved', u['note'] or 'No label on the drawing resolves to this decoder lot', u['htext'], u['section'], u['legacy'], '', '', '', ''])
    print('wrote verified_lots.csv (%d) and unresolved_locations.csv (%d)' % (len(L), len(R['review']) + len(R['known_unplaced'])))
if __name__ == '__main__': run()
