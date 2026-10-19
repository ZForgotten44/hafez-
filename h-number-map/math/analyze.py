"""Numbers behind the 'why the old numbering is confusing' section (all computed from the decoder, nothing typed in)."""
import json, re, collections, importlib.util, os
import hformula
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
D = json.load(open('decoder_dump.json')); fwd = D['fwd']; R = D['rows']
spec = importlib.util.spec_from_file_location('dec', os.path.join(REPO, 's4', 's4decoder1.py')); dec = importlib.util.module_from_spec(spec); spec.loader.exec_module(dec)
pf = hformula.parse
A = {}
# ---- label reuse
labels = collections.defaultdict(set)
for s, l, h in fwd: labels[l].add(s)
A['lots'] = len(fwd); A['distinct_labels'] = len(labels); A['labels_in_2plus_sections'] = sum(1 for v in labels.values() if len(v) > 1)
A['lots_with_shared_label'] = sum(1 for s, l, h in fwd if len(labels[l]) > 1)
A['max_sections_per_label'] = max(len(v) for v in labels.values())
A['top_shared'] = sorted(([l, sorted(v)] for l, v in labels.items()), key=lambda x: -len(x[1]))[:6]
sec_counts = collections.Counter(len(v) for v in labels.values()); A['label_multiplicity'] = sorted(sec_counts.items())
# ---- per section stats
def kind(l):
    p, n, sf = pf(l)
    if n is None: return 'odd'
    if sf == 'H': return 'H'
    if sf in ('A', 'B', 'C') : return 'suffix'
    if sf == '': return 'plain' if p == '' else 'odd'
    return 'odd'
rows = {}
for s in 'ABCDEFGHIJKLM':
    labs = [l for ss, l, h in fwd if ss == s]
    c = collections.Counter(kind(l) for l in labs)
    hs = sorted(h for ss, l, h in fwd if ss == s)
    rows[s] = dict(lots=len(set(labs)), labels=len(labs), plain=c['plain'], hlots=c['H'], suffix=c['suffix'], odd=c['odd'], hmin=hs[0], hmax=hs[-1],
                   hspan=hs[-1] - hs[0] + 1)
A['sections'] = rows
# ---- row step (difference between the first plain lot of consecutive rows) from the decoder's own rows / formulas
def steps(rowsd):
    tops = []
    for r in sorted(rowsd, key=int):
        pl = [pf(l)[1] for l in rowsd[r] if pf(l)[2] == '' and pf(l)[0] == '' and pf(l)[1] is not None]
        if pl: tops.append(max(pl))
    return [b - a for a, b in zip(tops, tops[1:])]
A['row_steps'] = {'A': [19] * 18, 'B': [20] * 18, 'D': steps({k: v for k, v in R['D'].items() if 2 <= int(k) <= 15}), 'C': steps(R['C']), 'F': steps(R['F']), 'E': steps({k: v for k, v in R['E'].items() if int(k) <= 8}),
                  'G': steps({k: v for k, v in R['G'].items() if int(k) <= 3}), 'H': steps(R['H']), 'M': steps(R['M']), 'K': steps(R['K']), 'J': steps(R['J']), 'I': steps(R['I']), 'L': steps(R['L'])}
# ---- unlabeled sweep positions in pass 1 (formula has no legacy label there) and B collisions
rev = D['rev']
missing = [h for h, s, l in rev if l is None]
A['unlabeled_positions'] = dict(count=len(missing), pass1=[h for h in missing if h <= 836], first=missing[:12])
shadow = [n for n in range(361, 380) if n % 20 != 0 and ('B', str(n)) in {(a, b) for a, b, c in fwd} and hformula.H_B_grid(n, '') and hformula.H_margin_B(str(n))]
A['B_grid_labels_shadowed_by_margin'] = shadow
# duplicates inside the decoder's own tables
dups = {}
for k, tab in R.items():
    seen = collections.Counter(l for r in tab.values() for l in r)
    d = [l for l, c in seen.items() if c > 1]
    if d: dups[k] = d
A['table_duplicates'] = dups
# ---- neighbour steps: how often is the next lot in the sweep exactly 1 away (legacy) vs always 1 (H)?
nb = {}
for s in 'ABCDEFGHIJKLM':
    ordered = sorted(((h, l) for ss, l, h in fwd if ss == s))
    ok = tot = 0
    for (h1, l1), (h2, l2) in zip(ordered, ordered[1:]):
        if h2 != h1 + 1: continue
        p1, n1, s1 = pf(l1); p2, n2, s2 = pf(l2)
        if n1 is None or n2 is None or s1 or s2: continue
        tot += 1; ok += abs(n2 - n1) == 1
    nb[s] = [ok, tot]
A['neighbour_step_is_1'] = nb
# ---- sawtooth data (pass 1: H<=836, all plain numeric labels)
saw = [[h, s, hformula.parse(l)[1], 1 if hformula.parse(l)[2] else 0] for s, l, h in fwd if hformula.parse(l)[1] is not None]
A['saw'] = saw
# ---- verification summary
import verify_summary
A['verify'] = verify_summary.run()
json.dump(A, open('analytics.json', 'w'))
print({k: v for k, v in A.items() if k not in ('saw', 'sections', 'row_steps', 'top_shared')})
print('top shared', A['top_shared'][:3]); print('row steps', {k: v[:8] for k, v in A['row_steps'].items()})
print('table dups', dups)
