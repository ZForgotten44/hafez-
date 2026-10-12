"""Step 4: final classification of every lot.

  verified      label text, enclosing outline (or drawn label position), section and decoder all agree and the
                H-number fits its neighbours.
  review        something visible on the map could not be tied to exactly one decoder lot (reason given).
  known_unplaced decoder lots that no label on the drawing resolves to.
Nothing is guessed: review items keep the candidate H-number only as a *candidate* and are never drawn as H-numbers."""
import json, collections, re
from shapely.geometry import Polygon
from common import *
from identify import load_decoder, SECTIONS

DEV_LIMIT = 100         # an H-number this far from the median of its 6 neighbours is treated as a numbering conflict
REASONS = {
 'label_not_in_decoder': 'The label on the drawing is not a lot the decoder knows.',
 'label_not_in_region_section': 'The label does not exist in the legacy section this part of the map belongs to.',
 'section_undetermined': 'No region evidence: this label exists in many sections, so it cannot be tied to one lot.',
 'duplicate_label_in_section': 'Two places on the drawing carry the same legacy label for the same section.',
 'inconsistent_with_neighbours': 'The decoded H-number is far from the H-numbers of the lots around it (numbering conflict).',
 'old_ocr_disagrees': 'An independent earlier reading of the drawing placed this label in a different section.',
 'outline_without_label': 'An outlined lot on the drawing has no label text inside it.',
 'no_region_evidence': 'No independent region evidence was available for the section.',
}

def run():
    dec = load_decoder()
    I = json.load(open(f'{DATA}/identified.json')); G = I['groups']; C = json.load(open(f'{DATA}/cells.json'))
    table = {(r['section'], r['lot_label']): r for s in SECTIONS for r in dec.full_table(s)}
    lots, review = [], []
    for g in G:
        flags = list(g['flags'])
        if g.get('nbr_dev', 0) > DEV_LIMIT: flags.append('inconsistent_with_neighbours')
        rec = dict(gid=g['id'], cell=g['cell'], pt=[round(g['pt'][0], 2), round(g['pt'][1], 2)], ang=round(g['ang'], 1),
                   tokens=g['tokens'], geom='outlined' if g['cell'] is not None else 'label_only', evidence=g['evidence'], flags=flags,
                   cands=g['cands'], region=g.get('region_sec'))
        if g['section']:
            rec.update(section=g['section'], legacy=g['label'], hnum=g['hnum'], htext=g['htext'])
        if g['section'] and not [f for f in flags if f != 'weak_section_vote']:
            rec['status'] = 'verified'; lots.append(rec)
        else:
            rec['status'] = 'review'
            rec['reasons'] = [REASONS.get(f, f) for f in flags if f in REASONS] or ['Weak section vote at an area boundary.']
            review.append(rec)
    # decoder lots with no verified cell
    claimed = {(r['section'], r['legacy']) for r in lots}
    cand_review = {(r['section'], r['legacy']) for r in review if 'section' in r}
    claimed_base = set()
    for s, l in claimed:                       # double rows: the A/B rows stand for the shared base lot
        m = re.match(r'^(\d+)([AB])$', l)
        if m: claimed_base.add((s, m.group(1)))
    known_unplaced = []
    for (s, l), r in sorted(table.items()):
        if (s, l) in claimed: continue
        if (s, l) in claimed_base: continue
        note = ''
        if l.endswith('dr'): note = 'internal bookkeeping key for a double-row lot (the map draws its A/B rows)'
        elif (s, l) in cand_review: note = 'a drawing label decodes to this lot but is held for review (see review list)'
        known_unplaced.append(dict(section=s, legacy=l, htext=r['h_lot'], hnum=r['h_lot_number'], note=note))
    labelled = {g['cell'] for g in G if g['cell'] is not None}
    for c in C:
        if c['id'] not in labelled:
            poly = Polygon(c['poly']).buffer(0); p = poly.representative_point()
            review.append(dict(gid=None, cell=c['id'], pt=[round(p.x, 2), round(p.y, 2)], ang=0, tokens=[], geom='outlined', status='review',
                               evidence=[], flags=['outline_without_label'], cands=[], reasons=['An outlined lot on the drawing has no label text inside it.']))
    out = dict(verified=lots, review=review, known_unplaced=known_unplaced, cells=len(C))
    json.dump(out, open(f'{DATA}/registry.json', 'w'))
    print('verified', len(lots), 'outlined', sum(r['geom'] == 'outlined' for r in lots), 'label_only', sum(r['geom'] == 'label_only' for r in lots))
    print('review', len(review), collections.Counter(f for r in review for f in r['flags']).most_common())
    print('known_unplaced', len(known_unplaced), collections.Counter(k['section'] for k in known_unplaced))
    h = collections.Counter(r['htext'] for r in lots); print('duplicate H among verified', [k for k, v in h.items() if v > 1][:10])
    print('verified evidence', collections.Counter(e.split('_vote')[0] if e.startswith('region') else e for r in lots for e in r['evidence']).most_common())
if __name__ == '__main__': run()
