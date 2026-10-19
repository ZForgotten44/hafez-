"""Step 4b: propose positions for everything classify.py left open, from the path alone.  Nothing here is verified.

The H-numbers run along one fixed path, so a lot whose H-number is h must sit close to the lots with h-1 and h+1 (and, when those
are missing, h-2 and h+2 ...).  For each held-back lot we list every H-number its label could mean, keep the ones that pass this
test, and accept a proposal only when it is the only one that passes.  Each proposal is PROVISIONAL and carries a confidence:
  high    both path neighbours (h-1 and h+1) are close, no other reading passes
  medium  one path neighbour is close (the other is missing or a known level jump), no other reading passes
  low     weaker evidence (more distant neighbours, a repaired label, or matched only by position)
Output: data/provisional.json (read by build_site.py, build_pdf.py, export_lists.py) and out/proposed_fixes.csv."""
import json, re, csv, math, collections, itertools
import numpy as np
from scipy.optimize import linear_sum_assignment
from shapely.geometry import Polygon
from common import *
from identify import load_decoder, SECTIONS

T1 = 32.0          # largest believable distance between lots h and h+1 (p95 of the placed path steps is 38; most steps are < 18)
def tol(gap): return T1 + 14.0 * (gap - 1)

def run():
    R = json.load(open(f'{DATA}/registry.json')); L = json.load(open(f'{DATA}/lots_fit.json')); I = json.load(open(f'{DATA}/identified.json')); C = json.load(open(f'{DATA}/cells.json'))
    G = {g['id']: g for g in I['groups']}; cells = {c['id']: c for c in C}
    dec = load_decoder(); table = {(r['section'], r['lot_label']): r for s in SECTIONS for r in dec.full_table(s)}
    byH = {(r['hnum']) : r for r in []}
    placed = collections.defaultdict(list)
    for o in L: placed[o['hn']].append((o['cx'], o['cy'], o['s'], o['l']))
    def dist(pt, h):
        return min((math.hypot(pt[0] - x, pt[1] - y) for x, y, _, _ in placed[h]), default=None)
    def neigh(pt, h, maxgap=3):
        """(distance to nearest placed lot below, its gap, distance above, gap)"""
        out = []
        for sgn in (-1, 1):
            r = (None, None)
            for g in range(1, maxgap + 1):
                d = dist(pt, h + sgn * g) if 1 <= h + sgn * g <= 3185 else None
                if d is not None: r = (d, g); break
            out.append(r)
        return out
    def test(pt, h):
        """returns (fits, strength, text) for the claim 'a lot at pt is H-number h'"""
        if placed.get(h): return False, 0, 'H%06d is already on another lot' % h
        (dp, gp), (dn, gn) = neigh(pt, h)
        fp = dp is not None and dp <= tol(gp); fn = dn is not None and dn <= tol(gn)
        if fp and fn: return True, 3, 'both path neighbours are close (%.0f and %.0f units away)' % (dp, dn)
        if fp or fn:
            d, g = (dp, gp) if fp else (dn, gn); other = dn if fp else dp
            return True, 2 if g == 1 else 1, 'the neighbour %s is close (%.0f units)%s' % ('before it' if fp else 'after it', d, '' if other is None else ', the other is %.0f units away' % other)
        return False, 0, 'it is far from its path neighbours (%s)' % (', '.join('%.0f' % v for v in (dp, dn) if v is not None) or 'none placed')
    CONF = {3: 'high', 2: 'medium', 1: 'low'}
    items = []
    def add(r, ri, group, status, conf, prop, reason, check, kind='lot'):
        items.append(dict(ri=ri, group=group, status=status, conf=conf, kind=kind, pt=r['pt'], cell=r['cell'], tokens=r['tokens'], prop=prop, reason=reason, check=check))
    claimed_h = {}
    # ---- group 1 and 2: which of the possible readings puts the lot next to its path neighbours?
    for ri, r in enumerate(R['review']):
        f = r['flags'][0]
        if f not in ('label_not_in_region_section', 'section_undetermined'): continue
        g = G[r['gid']]; opts = [(o[0], o[1], o[2], o[3]) for o in g['opts']]
        res = [(s, l, n, t) + test(r['pt'], n) for s, l, n, t in opts]
        ok = [x for x in res if x[4]]
        grp = 1 if f == 'label_not_in_region_section' else 2
        if len(ok) == 1:
            s, l, n, t, _, st, why = ok[0]
            conf = CONF[st]
            if len(opts) > 1 and st == 1: conf = 'low'
            add(r, ri, grp, 'provisional', conf, dict(section=s, label=l, htext=t, hnum=n),
                'Of the %d section%s that use the label %s, only Section %s puts this lot where H%06d belongs: %s.' % (len(opts), '' if len(opts) == 1 else 's', ''.join(r['tokens']), s, n, why),
                'Is this lot really Section %s, lot %s? (it sits in the %s area of the map)' % (s, l, r.get('region') or 'nearby'))
        elif len(ok) > 1:
            best = max(ok, key=lambda x: x[5]); second = sorted([x[5] for x in ok])[-2]
            if best[5] > second and best[5] >= 2:
                s, l, n, t, _, st, why = best
                add(r, ri, grp, 'provisional', 'low', dict(section=s, label=l, htext=t, hnum=n), 'Several sections could fit; Section %s fits best: %s.' % (s, why), 'Is this lot Section %s, lot %s, and not %s?' % (s, l, ', '.join('Section %s' % x[0] for x in ok if x is not best)))
            else:
                items.append(dict(ri=ri, group=grp, status='open', conf='', kind='lot', pt=r['pt'], cell=r['cell'], tokens=r['tokens'], prop=None, reason='%d sections fit equally well (%s).' % (len(ok), ', '.join('%s %s' % (x[0], x[3]) for x in ok)), check='Which of these sections is this lot in: %s?' % ', '.join(x[0] for x in ok)))
        else:
            items.append(dict(ri=ri, group=grp, status='open', conf='', kind='lot', pt=r['pt'], cell=r['cell'], tokens=r['tokens'], prop=None,
                              reason='None of the %d reading%s puts this lot next to its path neighbours.' % (len(opts), '' if len(opts) == 1 else 's'), check='Which section and lot is this really?'))
    # ---- group 3: duplicate labels, two drawn places for one lot
    dup = collections.defaultdict(list)
    for ri, r in enumerate(R['review']):
        if r['flags'][0] == 'duplicate_label_in_section': dup[(r['section'], r['legacy'])].append(ri)
    for (s, l), ids in dup.items():
        sc = []
        for ri in ids:
            r = R['review'][ri]; fit, st, why = test(r['pt'], r['hnum']); sc.append((st if fit else -1, ri, why))
        sc.sort(reverse=True)
        n, t = R['review'][ids[0]]['hnum'], R['review'][ids[0]]['htext']
        for k, (st, ri, why) in enumerate(sc):
            r = R['review'][ri]
            if k == 0 and st > 0 and (len(sc) == 1 or sc[1][0] < st):
                add(r, ri, 3, 'provisional', CONF[st] if sc[1][0] < 0 else 'low', dict(section=s, label=l, htext=t, hnum=n),
                    'The drawing shows %s-%s in %d places. This one sits where H%06d belongs: %s.' % (s, l, len(ids), n, why),
                    'Is this the real %s-%s? What is the other lot with the same label called?' % (s, l))
            else:
                items.append(dict(ri=ri, group=3, status='open', conf='', kind='lot', pt=r['pt'], cell=r['cell'], tokens=r['tokens'], prop=None,
                                  reason='Same label as another lot (%s-%s). %s' % (s, l, 'It does not sit where H%06d belongs.' % n if st < 0 else 'Both places fit equally.' if st > 0 else ''), check='What is this lot really called?'))
    # ---- group 4: H-number out of step with its spatial neighbours
    for ri, r in enumerate(R['review']):
        if r['flags'][0] != 'inconsistent_with_neighbours': continue
        fit, st, why = test(r['pt'], r['hnum'])
        if fit:
            add(r, ri, 4, 'provisional', CONF[st], dict(section=r['section'], label=r['legacy'], htext=r['htext'], hnum=r['hnum']),
                'The label %s-%s decodes to H%06d, far from the lots around it on the map, but %s, so the numbering path does reach this lot here.' % (r['section'], r['legacy'], r['hnum'], why),
                'Is the label right, so the numbering really jumps here? If not, what is the lot called?')
        else:
            items.append(dict(ri=ri, group=4, status='open', conf='', kind='lot', pt=r['pt'], cell=r['cell'], tokens=r['tokens'], prop=None,
                              reason='%s-%s decodes to H%06d but %s.' % (r['section'], r['legacy'], r['hnum'], why), check='Is the label right, or was the lot relabelled? What is the true order along this row?'))
    # ---- group 5: labels the table does not know -> nearby real labels
    labels_by_sec = collections.defaultdict(set)
    for (s, l) in table: labels_by_sec[s].add(l)
    def variants(tok):
        v = set(); t = ''.join(tok); m = re.match(r'^([A-Z])(\d+[A-Z]*)$', t)
        if m: v.add(m.group(2));
        digits = re.match(r'^(\d+)([A-Z]*)$', t.lstrip('ABCDEFGHIJKLM') if m else t)
        base = (m.group(2) if m else t); m2 = re.match(r'^(\d+)([A-Z]*)$', base)
        if m2:
            d, suf = m2.group(1), m2.group(2)
            for i in range(len(d) - 1): v.add(d[:i] + d[i + 1] + d[i] + d[i + 2:] + suf)     # swapped digits
            for i in range(len(d)):
                for c in '0123456789': v.add(d[:i] + c + d[i + 1:] + suf)                      # one digit off
            for sf in ('', 'H', 'A', 'B'): v.add(d + sf)                                       # suffix dropped or changed
            if suf: v.add(d)
        for s in SECTIONS:
            if m and (s + base) in labels_by_sec[s]: v.add(s + base)
        v.discard(t); return v
    for ri, r in enumerate(R['review']):
        if r['flags'][0] != 'label_not_in_decoder': continue
        reg = r.get('region'); ok = []
        for l in variants(r['tokens']):
            for s in SECTIONS:
                if (s, l) in table:
                    n = table[(s, l)]['h_lot_number']; t = table[(s, l)]['h_lot']
                    fit, st, why = test(r['pt'], n)
                    if fit and st >= 2: ok.append((s, l, n, t, st, why))
        if len(ok) == 1:
            s, l, n, t, st, why = ok[0]
            add(r, ri, 5, 'provisional', 'low', dict(section=s, label=l, htext=t, hnum=n),
                'The drawing says "%s", which is not a lot in the numbering table. The closest real label, %s-%s (H%06d), fits this spot: %s.' % (''.join(r['tokens']), s, l, n, why),
                'Is this lot really %s-%s? Is "%s" a typo on the drawing?' % (s, l, ''.join(r['tokens'])))
        else:
            items.append(dict(ri=ri, group=5, status='open', conf='', kind='lot', pt=r['pt'], cell=r['cell'], tokens=r['tokens'], prop=None,
                              reason='"%s" is not in the numbering table and %s.' % (''.join(r['tokens']), 'no close real label fits this spot' if not ok else '%d close labels fit (%s)' % (len(ok), ', '.join('%s-%s' % (x[0], x[1]) for x in ok))), check='What is this lot really called?'))
    # ---- unplaced H-numbers: where on the map should each one be?
    taken = {it['prop']['hnum'] for it in items if it['status'] == 'provisional'}
    for it in items:
        if it['status'] == 'provisional': placed[it['prop']['hnum']].append((it['pt'][0], it['pt'][1], it['prop']['section'], it['prop']['label']))
    exp = []; seen = set()
    for u in R['known_unplaced']:
        h = u['hnum']
        if h in taken or placed.get(h) or u['legacy'].endswith('dr'): continue
        if (h, u['legacy']) in seen: continue
        seen.add((h, u['legacy']))
        below = next(((g, placed[h - g][0]) for g in range(1, 7) if placed.get(h - g)), None)
        above = next(((g, placed[h + g][0]) for g in range(1, 7) if placed.get(h + g)), None)
        if below and above:
            a, b = np.array(below[1][:2]), np.array(above[1][:2]); gb, ga = below[0], above[0]; t = gb / (gb + ga)
            p = a + (b - a) * t; sep = float(np.hypot(*(a - b))); conf = 'medium' if (gb == 1 and ga == 1 and sep <= 2 * T1) else 'low' if sep <= tol(gb + ga) else None
            reason = 'H%06d sits between H%06d and H%06d on the path, which are %.0f units apart.' % (h, h - gb, h + ga, sep)
        elif below or above:
            g0, q = below or above; p = np.array(q[:2]); conf = 'low'; reason = 'H%06d follows H%06d on the path; the lot on the other side is also missing.' % (h, h - g0 if below else h + g0)
        else: p = None; conf = None; reason = 'No neighbour on the path is placed.'
        exp.append(dict(htext=u['htext'], hnum=h, section=u['section'], label=u['legacy'], x=None if p is None else round(float(p[0]), 1), y=None if p is None else round(float(p[1]), 1), conf=conf, reason=reason, check='Is there a lot at this spot? Where is %s-%s on the ground?' % (u['section'], u['legacy']), cell=None, ri=None))
    # ---- group 6: unlabeled outlines <-> expected positions (one to one)
    free = [(ri, r) for ri, r in enumerate(R['review']) if r['flags'][0] == 'outline_without_label']
    cand_e = [e for e in exp if e['x'] is not None and e['conf']]
    if free and cand_e:
        M = np.full((len(free), len(cand_e)), 1e6)
        for i, (ri, r) in enumerate(free):
            for j, e in enumerate(cand_e): M[i, j] = math.hypot(r['pt'][0] - e['x'], r['pt'][1] - e['y'])
        ri_, ci_ = linear_sum_assignment(M)
        used = set()
        for i, j in zip(ri_, ci_):
            d = M[i, j]; ri, r = free[i]; e = cand_e[j]
            second = np.sort(M[i])[1] if M.shape[1] > 1 else 1e6
            if d <= 14 and second > d * 1.5:
                e['cell'] = r['cell']; e['ri'] = ri; e['x'], e['y'] = r['pt']
                add(r, ri, 6, 'provisional', 'medium' if d <= 8 else 'low', dict(section=e['section'], label=e['label'], htext=e['htext'], hnum=e['hnum']),
                    'This empty outline lies %.0f units from where H%06d (%s-%s) should be, and no other empty outline is closer.' % (d, e['hnum'], e['section'], e['label']),
                    'Is this empty lot %s-%s?' % (e['section'], e['label'])); used.add(ri)
        for ri, r in free:
            if ri not in used:
                items.append(dict(ri=ri, group=6, status='open', conf='', kind='lot', pt=r['pt'], cell=r['cell'], tokens=[], prop=None, reason='No missing H-number is expected within 14 units of this empty outline.', check='Is this a real lot? What is it called? Or is it a road, path or building corner?'))
    # ---- why is each remaining item open?  and which open items belong to one block?
    placed0 = collections.defaultdict(int)
    for o in L: placed0[o['hn']] += 1
    for it in items:
        if it['status'] != 'open': continue
        r = R['review'][it['ri']]; g = G.get(r['gid']); cat = 'unknown'
        if g and g['opts'] and r['flags'][0] in ('label_not_in_region_section', 'section_undetermined'):
            taken = [placed0.get(o[2], 0) > 0 for o in g['opts']]
            cat = 'not_in_table' if all(taken) else 'no_fit'
            if cat == 'not_in_table':
                it['reason'] = 'The label "%s" exists in %d section%s, but in each one its H-number is already on a different lot. So this lot is probably not in the numbering table at all.' % (''.join(r['tokens']), len(g['opts']), '' if len(g['opts']) == 1 else 's')
        it['cat'] = cat
        if cat == 'not_in_table': it['check'] = 'Is this a real lot that the numbering table is missing? If so, what is it called and which section is it in?'
    from scipy.cluster.hierarchy import fcluster, linkage
    op = [it for it in items if it['status'] == 'open']
    if len(op) > 1:
        cl = fcluster(linkage(np.array([it['pt'] for it in op]), 'single'), 18, 'distance')
        for it, c in zip(op, cl): it['block'] = int(c)
        sizes = collections.Counter(it['block'] for it in op)
        for it in op:
            if sizes[it['block']] < 3: it['block'] = None
    # loose numbers (no outline) that repeat a label drawn elsewhere
    for it in items:
        r = R['review'][it['ri']]
        if it['status'] == 'open' and r['geom'] != 'outlined' and it['group'] in (3, 4) : it['reason'] = 'A loose number with no lot outline. ' + it['reason']; it['check'] = 'Is this a real lot, or a scale/annotation (a row of loose numbers every 5)?'
    # ---- blocks: open items that sit together get one question
    blocks = []
    byblock = collections.defaultdict(list)
    for it in items:
        if it['status'] == 'open' and it.get('block'): byblock[it['block']].append(it)
    allp = [(o['cx'], o['cy'], o['s'], o['l']) for o in L]
    for bid, mem in sorted(byblock.items(), key=lambda kv: -len(kv[1])):
        P = np.array([m['pt'] for m in mem]); cx, cy = P.mean(0)
        labs = sorted({''.join(m['tokens']) for m in mem if m['tokens']}, key=lambda t: (int(re.sub(r'\D', '', t) or 0), t))
        near = collections.Counter()
        for x, y, s_, l_ in allp:
            if any(math.hypot(x - p[0], y - p[1]) <= 26 for p in P): near[s_] += 1
        cats = collections.Counter(m.get('cat') for m in mem)
        nit = cats.get('not_in_table', 0)
        txt = '%d lots drawn around (%d, %d), labelled %s%s.' % (len(mem), cx, cy, ', '.join(labs[:6]) + (' … ' + labs[-1] if len(labs) > 6 else ''), '' if not near else ' Verified lots next to them are in Section %s.' % ' and '.join(k for k, _ in near.most_common(2)))
        q = ('%d of these %d lots have labels whose H-numbers already belong to other lots in every section that uses them, so they are probably not in the numbering table. ' % (nit, len(mem)) if nit else '') + 'What is this block, and should its lots get H-numbers?'
        blocks.append(dict(id=int(bid), n=len(mem), x=round(float(cx), 1), y=round(float(cy), 1), labels=labs, near=dict(near), text=txt, question=q, not_in_table=nit))
        for m in mem: m['block_text'] = txt; m['check'] = q
    prov_h = {it['prop']['hnum']: it for it in items if it['status'] == 'provisional'}
    exp_open = [e for e in exp if e['ri'] is None]
    out = dict(items=sorted(items, key=lambda i: i['ri']), expected=exp_open, blocks=blocks)
    json.dump(out, open(f'{DATA}/provisional.json', 'w'))
    c = collections.Counter((i['group'], i['status'], i['conf']) for i in items)
    for k in sorted(c): print(k, c[k])
    print('expected markers', len(exp_open), collections.Counter(e['conf'] for e in exp_open), 'of', len(R['known_unplaced']), 'unplaced')
    print('placed by provisional lots', len(prov_h))
    # ---- proposed_fixes.csv: one row per item, with an empty column for the answer
    GROUP = {1: 'label in the wrong section', 2: 'short label, many sections', 3: 'same label drawn twice', 4: 'H-number out of step', 5: 'label not in the table', 6: 'outline without label', 7: 'H-number with no position'}
    import os
    with open(os.path.join(OUT, 'proposed_fixes.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['group', 'status', 'map_x', 'map_y', 'label_on_drawing', 'proposed_section', 'proposed_label', 'proposed_H', 'confidence', 'reason', 'still_needed', 'user_confirm_Y_N'])
        for it in out['items']:
            p = it['prop'] or {}
            w.writerow([GROUP[it['group']], 'provisional' if it['status'] == 'provisional' else 'open', round(it['pt'][0], 1), round(it['pt'][1], 1), ''.join(it['tokens']), p.get('section', ''), p.get('label', ''), p.get('htext', ''), it['conf'], it['reason'], it['check'], ''])
        for e in exp_open:
            w.writerow([GROUP[7], 'expected position' if e['conf'] else 'open', e['x'] if e['x'] is not None else '', e['y'] if e['y'] is not None else '', '', e['section'], e['label'], e['htext'], e['conf'] or '', e['reason'], 'Is there a lot here? Where is %s-%s on the ground?' % (e['section'], e['label']), ''])
    # ---- decisions_needed.md in its new state
    NAMES = {1: ('Label drawn in the wrong section', 'label_not_in_region_section'), 2: ('Short labels that exist in many sections', 'section_undetermined'), 3: ('The same label drawn twice', 'duplicate_label_in_section'),
             4: ('H-number out of step with its neighbours', 'inconsistent_with_neighbours'), 5: ('Label the numbering table does not know', 'label_not_in_decoder'), 6: ('Outlined lot with no label', 'outline_without_label')}
    tot_prov = sum(1 for i in items if i['status'] == 'provisional'); tot_open = len(items) - tot_prov
    md = ['# Cedar Grove: decisions still needed, after the path check', '',
          'Method: every H-number sits between H-1 and H+1 on the numbering path, so a lot must stand next to the lots that hold those numbers. Each held-back lot was tested against every number its label could mean, and a proposal was accepted only when it was the **only** one that passes. Nothing here is verified. Proposals are drawn in blue on the map ("Inferred from the path, please confirm"); verified lots did not change.', '',
          'Before: 218 lots held for review, 68 H-numbers with no position. **Now: %d lots inferred (provisional), %d lots still open, %d H-numbers still without a lot (%d of them have an expected spot).**' % (tot_prov, tot_open, len(exp_open), sum(1 for e in exp_open if e['conf'])), '']
    for g in range(1, 7):
        mem = [i for i in items if i['group'] == g]; pr = [i for i in mem if i['status'] == 'provisional']; op = [i for i in mem if i['status'] == 'open']
        c = collections.Counter(i['conf'] for i in pr)
        md.append('**%d. %s (%d lots)**' % (g, NAMES[g][0], len(mem)))
        md.append('- Inferred: %d (high %d, medium %d, low %d). Still open: %d.' % (len(pr), c['high'], c['medium'], c['low'], len(op)))
        for i in pr[:2]: md.append('  - e.g. `%s` -> %s %s (%s, %s confidence): %s' % (''.join(i['tokens']), i['prop']['section'], i['prop']['label'], i['prop']['htext'], i['conf'], i['reason']))
        cats = collections.Counter(i.get('cat') for i in op)
        if cats.get('not_in_table'): md.append('  - %d open lots carry a label whose H-number is already on another lot in every section that uses it, so they are probably **not in the numbering table** (see blocks below).' % cats['not_in_table'])
        qs = collections.Counter(i['check'] for i in op)
        for q, n in qs.most_common(2): md.append('  - Question (%d lots): %s' % (n, q))
        md.append('')
    md.append('**Blocks that need one answer each (%d)**' % len(blocks))
    for b in blocks: md.append('- %s %s' % (b['text'], b['question']))
    md += ['', '**7. H-numbers with no lot (68 before)**',
           '- Placed on an inferred lot: %d. Expected spot with no outline drawn: %d (medium %d, low %d). No neighbour on the path is placed, so no spot can be given: %d.' % (len(prov_h), sum(1 for e in exp_open if e['conf']), sum(1 for e in exp_open if e['conf'] == 'medium'), sum(1 for e in exp_open if e['conf'] == 'low'), sum(1 for e in exp_open if not e['conf'])),
           '- Question: for each expected spot (dashed ring on the map and `proposed_fixes.csv`), is there a lot there, and what is it called? This includes the Section A "H" lots that start every row (20H, 39H, 58H ...).', '',
           'Fill the last column of `pipeline2/out/proposed_fixes.csv` (Y or N) or just tell me; a yes turns a proposal into a verified lot.', '']
    open(os.path.join(OUT, 'decisions_needed.md'), 'w').write('\n'.join(md))
    print('blocks', [(b['n'], b['x'], b['y']) for b in blocks])
if __name__ == '__main__': run()
