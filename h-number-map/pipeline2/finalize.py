"""Step 5c: close every open case, following the staff rules (no review list is left).

  1. Numbers inferred by resolve.py (the lot must stand next to the lots h-1 and h+1) are accepted.
  2. Replicated labels are removed.  A second drawing of a label that already has its lot is dropped when it is only a loose number;
     when it is a lot outline next to the lot that holds the label it is the same lot drawn twice: it keeps the one H-number and the
     number is written once (the twin carries no second label).
  3. Gap filling: an H-number that has no lot sits between h-1 and h+1 on the path, so the nearest unnumbered outline to that spot
     gets it (mutual nearest, repeated until nothing changes, because each new lot gives its neighbours a spot to look at).
  4. The block of graves between the mausoleums (labelled 1-68) is not part of the numbering: no number, no review.
  5. Any outline still left is not in the numbering table; it is listed as 'unnumbered', not as a case to review.
Reads data/registry_raw.json; writes data/registry.json (verified + resolved, review empty) and
out/resolution_log.csv with one row per decision."""
import json, csv, math, os, collections, shutil
import numpy as np
from scipy.optimize import linear_sum_assignment
from shapely.geometry import Polygon
from common import *

TWIN_DIST = 45.0         # a second outline this close to the lot that owns the label is the same lot drawn twice
BLOCKS_NO_NUMBER = [(594.9, 377.8, 50), (589.6, 321.4, 14)]   # graves between the mausoleums (labels 1-68), centre and size as found by resolve.py
BLOCK_R = 40.0

def run():
    raw = f'{DATA}/registry_raw.json'
    R = json.load(open(raw)); L = json.load(open(f'{DATA}/lots_fit_raw.json')); P = json.load(open(f'{DATA}/provisional.json'))
    C = {c['id']: c for c in json.load(open(f'{DATA}/cells.json'))}
    pv = {i['ri']: i for i in P['items']}
    placed = collections.defaultdict(list)                       # H-number -> [(x, y)]
    for o in L: placed[o['hn']].append((o['cx'], o['cy']))
    log = []; new_verified = []; used_h = set()

    def mk(r, section, label, htext, hnum, ev, extra=None):
        rec = dict(gid=r.get('gid'), cell=r['cell'], pt=r['pt'], ang=r.get('ang', 0), tokens=r.get('tokens', []), geom=r['geom'], evidence=[ev], flags=[], cands=r.get('cands', []),
                   region=r.get('region'), section=section, legacy=label, hnum=hnum, htext=htext, status='verified')
        if extra: rec.update(extra)
        return rec

    # 1. inferred from the path (an H-number goes to one lot only: the best-supported proposal wins, the others fall through to the rules below)
    done = set(); CONF = {'high': 0, 'medium': 1, 'low': 2}
    def pathdist(pt, h):
        ds = [min(math.hypot(pt[0] - x, pt[1] - y) for x, y in placed[h + g]) for g in (-1, 1) if placed.get(h + g)]
        return sum(ds) if ds else 1e6
    props = sorted(((ri, it) for ri, it in pv.items() if it['status'] == 'provisional'),
                   key=lambda t: (CONF.get(t[1]['conf'], 3), pathdist(R['review'][t[0]]['pt'], t[1]['prop']['hnum'])))
    for ri, it in props:
        r = R['review'][ri]; q = it['prop']
        if q['hnum'] in used_h: continue
        new_verified.append(mk(r, q['section'], q['label'], q['htext'], q['hnum'], 'resolved_path'))
        placed[q['hnum']].append(tuple(r['pt'])); used_h.add(q['hnum']); done.add(ri)
        log.append(['numbered from the path', ''.join(r['tokens']), q['htext'], q['section'] + ' ' + q['label'], it['conf'], it['reason']])

    # 4. graves between the mausoleums: no number, no review (the open blocks resolve.py found at these two spots)
    gb = {b['id'] for b in P['blocks'] for (bx, by, _) in BLOCKS_NO_NUMBER if math.hypot(b['x'] - bx, b['y'] - by) < 15}
    graves = [ri for ri, it in pv.items() if ri not in done and it.get('block') in gb]
    gset = set(graves); done |= gset
    unnumbered = []
    for ri in graves:
        r = R['review'][ri]; unnumbered.append(dict(cell=r['cell'], pt=r['pt'], tokens=r['tokens'], geom=r['geom'], graves=True))
        log.append(['no number (graves between the mausoleums)', ''.join(r['tokens']), '', '', '', 'Not part of the H-numbering'])

    # 2. replicated labels
    owner = {}
    for rec in new_verified: owner[(rec['section'], rec['legacy'])] = rec
    for o in L: owner.setdefault((o['s'], o['l']), dict(pt=(o['cx'], o['cy']), hnum=o['hn'], htext=o['h']))
    for ri, r in enumerate(R['review']):
        if ri in done: continue
        flags = r['flags'][0]
        keys = []
        if r.get('section') and r.get('legacy'): keys.append((r['section'], r['legacy']))
        it = pv.get(ri)
        if flags == 'duplicate_label_in_section' and keys:
            own = owner.get(keys[0]); same = own is not None
            pos = own['pt'] if own and 'pt' in own else None
            if same and pos is not None and math.hypot(pos[0] - r['pt'][0], pos[1] - r['pt'][1]) <= TWIN_DIST and r['geom'] == 'outlined':
                new_verified.append(mk(r, r['section'], r['legacy'], own['htext'], own['hnum'], 'merged_duplicate', dict(twin=True)))
                log.append(['same lot drawn twice: one number', ''.join(r['tokens']), own['htext'], '%s %s' % keys[0], '', 'second outline %.0f units from the lot that holds the label' % math.hypot(pos[0] - r['pt'][0], pos[1] - r['pt'][1])]); done.add(ri); continue
            if r['geom'] != 'outlined':
                log.append(['replicated label removed (loose number)', ''.join(r['tokens']), r.get('htext', ''), '%s %s' % keys[0], '', 'the label already has its lot']); done.add(ri); continue
        if r['geom'] != 'outlined' and ri not in done:     # loose numbers repeating labels elsewhere: scale / annotation rows
            log.append(['replicated label removed (loose number)', ''.join(r['tokens']), r.get('htext', ''), (r.get('section', '') + ' ' + r.get('legacy', '')).strip(), '', 'a loose number without a lot outline repeats a label that is already used']); done.add(ri)

    # 2b. the same label drawn on adjacent outlines with no owner yet: one lot drawn twice, one H-number
    grp = collections.defaultdict(list)
    for ri, r in enumerate(R['review']):
        if ri in done or r['geom'] != 'outlined' or r['flags'][0] != 'duplicate_label_in_section' or not r.get('legacy'): continue
        grp[(r['section'], r['legacy'])].append(ri)
    for key, ids in grp.items():
        if key in owner or len(ids) < 2: continue
        pts = [R['review'][i]['pt'] for i in ids]
        if max(math.hypot(a[0] - b[0], a[1] - b[1]) for a in pts for b in pts) > TWIN_DIST: continue
        h = R['review'][ids[0]]
        if placed.get(h['hnum']): continue
        for k, i in enumerate(ids):
            new_verified.append(mk(R['review'][i], key[0], key[1], h['htext'], h['hnum'], 'merged_duplicate', dict(twin=k > 0)))
            done.add(i)
        placed[h['hnum']].append(tuple(pts[0])); used_h.add(h['hnum']); owner[key] = dict(pt=pts[0], hnum=h['hnum'], htext=h['htext'])
        log.append(['same lot drawn %d times: one number' % len(ids), ''.join(h['tokens']), h['htext'], '%s %s' % key, '', 'outlines %.0f units apart or less, same label' % max(math.hypot(a[0] - b[0], a[1] - b[1]) for a in pts for b in pts)])
    # 2c. an outline whose label text is exactly a label the numbering still has no lot for
    miss0 = {}
    for u in R['known_unplaced']:
        if u['legacy'].endswith('dr') or u['hnum'] in used_h or placed.get(u['hnum']): continue
        miss0[(u['section'], u['legacy'])] = u
    byc = collections.defaultdict(list)
    for ri, r in enumerate(R['review']):
        if ri in done or r['geom'] != 'outlined' or r['cell'] is None: continue
        t = ''.join(r['tokens'])
        for (s_, l_), u in miss0.items():
            if l_ == t and s_ in (r.get('cands') or []): byc[(s_, l_)].append(ri)
    for key, ids in byc.items():
        u = miss0[key]
        if len(ids) != 1: continue
        r = R['review'][ids[0]]
        sib = [o for o in L if o['s'] == key[0] and math.hypot(o['cx'] - r['pt'][0], o['cy'] - r['pt'][1]) <= 70]
        if not sib: continue
        new_verified.append(mk(r, u['section'], u['legacy'], u['htext'], u['hnum'], 'resolved_label'))
        placed[u['hnum']].append(tuple(r['pt'])); used_h.add(u['hnum']); done.add(ids[0])
        log.append(['numbered by its label next to its own section', ''.join(r['tokens']), u['htext'], '%s %s' % key, '', 'only outline with this label; %d lots of Section %s within 70 units' % (len(sib), key[0])])

    # 3. gap filling for the outlines that are still open
    cand = [ri for ri, r in enumerate(R['review']) if ri not in done and r['geom'] == 'outlined' and r['cell'] is not None]
    missing = [u for u in R['known_unplaced'] if not u['legacy'].endswith('dr')]
    seen = set(); miss = []
    for u in missing:
        if u['hnum'] in used_h or placed.get(u['hnum']) or u['hnum'] in seen: continue
        seen.add(u['hnum']); miss.append(u)
    def expect(h):
        below = next(((g, placed[h - g][0]) for g in range(1, 7) if placed.get(h - g)), None)
        above = next(((g, placed[h + g][0]) for g in range(1, 7) if placed.get(h + g)), None)
        if below and above:
            a, b = np.array(below[1]), np.array(above[1]); t = below[0] / (below[0] + above[0])
            sep = float(np.hypot(*(a - b)))
            if sep > 32.0 + 14.0 * (below[0] + above[0] - 1): return None, None, None      # the path jumps here (a pass boundary): no spot between the two
            return a + (b - a) * t, sep, below[0] + above[0]
        if below or above:
            g, q = below or above; return np.array(q), 0.0, g
        return None, None, None
    changed = True; rounds = 0
    while changed and cand and miss:
        changed = False; rounds += 1
        E = []
        for u in miss:
            p, sep, gap = expect(u['hnum'])
            if p is None: continue
            E.append((u, p, sep, gap))
        if not E: break
        M = np.full((len(cand), len(E)), 1e6)
        for i, ri in enumerate(cand):
            for j, (u, p, sep, gap) in enumerate(E): M[i, j] = math.hypot(R['review'][ri]['pt'][0] - p[0], R['review'][ri]['pt'][1] - p[1])
        ri_, ci_ = linear_sum_assignment(M)
        picks = []
        for i, j in zip(ri_, ci_):
            d = M[i, j]; u, p, sep, gap = E[j]
            lim = 16.0 if sep else 20.0
            if d > lim: continue
            row = np.sort(M[i]); col = np.sort(M[:, j])
            if (len(row) > 1 and row[1] < d * 1.3 and row[1] < lim) or (len(col) > 1 and col[1] < d * 1.3 and col[1] < lim): continue   # not obvious: another outline is as close
            picks.append((d, i, j))
        for d, i, j in sorted(picks):
            ri = cand[i]; u = E[j][0]; r = R['review'][ri]
            new_verified.append(mk(r, u['section'], u['legacy'], u['htext'], u['hnum'], 'resolved_gap'))
            placed[u['hnum']].append(tuple(r['pt'])); used_h.add(u['hnum']); done.add(ri)
            log.append(['numbered by its neighbours (the number missing between h-1 and h+1)', ''.join(r['tokens']), u['htext'], '%s %s' % (u['section'], u['legacy']), '', 'nearest outline %.0f units from the spot between its path neighbours' % d])
            changed = True
        cand = [ri for ri in cand if ri not in done]; miss = [u for u in miss if u['hnum'] not in used_h]

    # 5. what is left is not in the numbering table
    for ri, r in enumerate(R['review']):
        if ri in done: continue
        unnumbered.append(dict(cell=r['cell'], pt=r['pt'], tokens=r['tokens'], geom=r['geom'], graves=False))
        log.append(['outline without an H-number (not in the numbering table)', ''.join(r['tokens']), '', '', '', 'no free H-number near it'])
    verified = R['verified'] + new_verified
    still = [u for u in R['known_unplaced'] if u['hnum'] not in {v['hnum'] for v in new_verified} and not any(
        placed.get(u['hnum']) for _ in [0])]
    out = dict(verified=verified, review=[], known_unplaced=[u for u in R['known_unplaced'] if u['hnum'] not in used_h], unnumbered=unnumbered, cells=R['cells'])
    json.dump(out, open(f'{DATA}/registry.json', 'w'))
    with open(os.path.join(OUT, 'resolution_log.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['decision', 'label_on_drawing', 'h_number', 'section_lot', 'confidence', 'why']); w.writerows(log)
    c = collections.Counter(l[0] for l in log)
    nu = [u for u in unnumbered if not u['graves']]; gr = [u for u in unnumbered if u['graves']]
    md = ['# Cedar Grove: every open case is closed', '',
          'The review list is empty. Each case was settled by one of the rules below; every decision is one row in `resolution_log.csv`.', '',
          '| Rule | Lots |', '|---|---|',
          '| Number worked out from the path: the lot must stand next to the lots with H-1 and H+1 | %d |' % c['numbered from the path'],
          '| The number missing between H-1 and H+1 goes to the outline that stands there | %d |' % c['numbered by its neighbours (the number missing between h-1 and h+1)'],
          '| Outline whose label is exactly a label the numbering still lacked a lot for, next to its own section | %d |' % c['numbered by its label next to its own section'],
          '| Same lot drawn twice: one H-number, written once | %d lots (%d outlines) |' % (sum(v for k, v in c.items() if k.startswith('same lot drawn')), sum(v * 2 for k, v in c.items() if k.startswith('same lot drawn'))),
          '| Loose number that only repeats a label already used: removed | %d |' % c['replicated label removed (loose number)'],
          '| Graves between the mausoleums (labels 1 to 68): no number, no review | %d |' % len(gr),
          '| Outline that is not in the numbering table and has no free H-number near it: drawn grey, no number | %d |' % len(nu), '',
          'H-numbers with no lot drawn on the map: **%d** (`h_numbers_without_lot.csv`). 18 of them are the Section A "H" lots that start every row.' % len(out['known_unplaced']), '',
          'Nothing was renumbered: no H-number moved. If the grey outlines should get numbers, say which rule (append after H003185, or insert).', '']
    open(os.path.join(OUT, 'decisions_needed.md'), 'w').write('\n'.join(md))
    shutil.copy(os.path.join(OUT, 'resolution_log.csv'), os.path.join(REPO, 'h-number-map', 'resolution_log.csv'))
    shutil.copy(os.path.join(OUT, 'decisions_needed.md'), os.path.join(REPO, 'h-number-map', 'decisions_needed.md'))
    print('resolved. verified', len(R['verified']), '+', len(new_verified), '| unnumbered outlines', len(unnumbered), '| H-numbers still without a lot', len(out['known_unplaced']), '| gap rounds', rounds)
    for k, v in c.most_common(): print('  ', v, k)
if __name__ == '__main__': run()
