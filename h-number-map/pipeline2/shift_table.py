"""Shift table: decoder at the review commit (d990927) vs the production decoder now.
Writes crosswalk/shift_table_lots.csv (one row per physical lot), shift_runs.csv (continuous runs), shift_boundaries.csv (net shift at each section boundary),
shift_focus_B20.csv (19A, B 20 and neighbours before/after), and returns the four lead counts."""
import csv, importlib.util, os, re, subprocess, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, '..', '..')); OUT = os.path.join(REPO, 'h-number-map', 'crosswalk')
REVIEW_COMMIT = 'd990927'
def load(src, name):
    spec = importlib.util.spec_from_loader(name, loader=None); m = importlib.util.module_from_spec(spec); exec(compile(src, name, 'exec'), m.__dict__); return m
OLD = load(subprocess.check_output(['git', '-C', REPO, 'show', REVIEW_COMMIT + ':s4/s4decoder1.py']).decode(), 'dec_review')
NEW = load(open(os.path.join(REPO, 's4', 's4decoder1.py')).read(), 'dec_now')
SECS = 'ABCDEFGHIJKLM'
def table(dec):
    out = {}
    for s in SECS:
        try: rows = dec.full_table(s)
        except Exception: continue
        for r in rows: out[(s, r['lot_label'])] = r['h_lot_number']
    return out
T_OLD, T_NEW = table(OLD), table(NEW)
# D row-head H lots: the review decoder keyed row r's head as 20(r-1)H; the printed lot is 20rH (same route slot) -> same physical lot
_snap = {('D', '%dH' % (20 * k)): T_OLD.pop(('D', '%dH' % (20 * k))) for k in range(1, 15)}
for (_, l), h in _snap.items(): T_OLD[('D', '%dH' % (int(l[:-1]) + 20))] = h
# why a lot is new: documented rule + evidence
def new_reason(s, l):
    if s == 'B' and l in ('20', '19A'): return 'B level 1: the first row of the route is 20H, 20, 19A, 19 ... 1 (drawing y-order, B_20_vs_19A below); distinct lot, inserted'
    if s == 'C': return 'C H-twin: an H lot printed directly before its plain lot in the same row (every-4-labels pattern); distinct outline, inserted'
    if s == 'D': return 'D row-head H lot: printed H lot ahead of the row (20H, 40H ... 333H); distinct outline, inserted'
    if s == 'L': return 'L strip 1 to 13 lies on the route between M and K (pass 5 to pass 6); distinct outlines, inserted'
    return 'inserted: verified distinct lot'
rows = []
keys = sorted(set(T_OLD) | set(T_NEW), key=lambda k: (T_NEW.get(k, T_OLD.get(k)) if k in T_NEW else 10**7 + T_OLD[k], k))
ins_new = sorted(T_NEW[k] for k in T_NEW if k not in T_OLD)
import bisect
for k in sorted(T_NEW, key=lambda k: T_NEW[k]):
    s, l = k; n = T_NEW[k]; o = T_OLD.get(k)
    before = bisect.bisect_left(ins_new, n)
    if o is None: st, shift, why = 'inserted', '', new_reason(s, l)
    elif o == n: st, shift, why = 'unchanged', 0, ''
    else:
        st, shift = 'shifted', n - o
        why = '%d lots inserted earlier on the route (last one before it: H%06d)' % (before, max(h for h in ins_new if h < n)) if before else 'see note'
        if shift != before: why += ' | NOTE: shift differs from insert count (%d)' % before
    rows.append(dict(section=s, physical_lot_label=l, old_H=('H%06d' % o) if o else '', new_H='H%06d' % n, shift=shift, status=st, reason=why))
removed = [k for k in T_OLD if k not in T_NEW]
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, 'shift_table_lots.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, list(rows[0])); w.writeheader(); w.writerows(rows)
# continuous runs of one shift value in route order
runs = []; cur = None
for r in rows:
    sh = r['shift'] if r['status'] != 'inserted' else 'inserted'
    if cur and cur['key'] == sh and cur['sec'] == r['section']: cur['last'] = r
    else:
        if cur: runs.append(cur)
        cur = dict(key=sh, sec=r['section'], first=r, last=r, n=0)
    cur['n'] += 1
runs.append(cur)
with open(os.path.join(OUT, 'shift_runs.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['section', 'kind', 'shift', 'lots_in_run', 'first_lot', 'first_old_H', 'first_new_H', 'last_lot', 'last_old_H', 'last_new_H'])
    for c in runs:
        a, b = c['first'], c['last']; w.writerow([c['sec'], 'inserted' if c['key'] == 'inserted' else ('unchanged' if c['key'] == 0 else 'shifted'), '' if c['key'] == 'inserted' else c['key'], c['n'], a['physical_lot_label'], a['old_H'], a['new_H'], b['physical_lot_label'], b['old_H'], b['new_H']])
# section boundaries: net shift of last lot of the previous section and first of the next (route order)
secs = []
for r in rows:
    if not secs or secs[-1][0] != r['section']: secs.append([r['section'], r, r])
    else: secs[-1][2] = r
with open(os.path.join(OUT, 'shift_boundaries.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['section_run_in_route_order', 'first_lot', 'first_new_H', 'first_shift_vs_review', 'last_lot', 'last_new_H', 'last_shift_vs_review'])
    for s, a, b in secs: w.writerow([s, a['physical_lot_label'], a['new_H'], a['shift'], b['physical_lot_label'], b['new_H'], b['shift']])
# focus rows: B 20 / 19A and neighbours in route order
foc = [i for i, r in enumerate(rows) if r['section'] == 'B' and r['physical_lot_label'] in ('20', '19A')]
lo, hi = min(foc) - 2, max(foc) + 3
with open(os.path.join(OUT, 'shift_focus_B20.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, list(rows[0])); w.writeheader(); w.writerows(rows[max(lo, 0):hi])
ins = [r for r in rows if r['status'] == 'inserted']; sh = [r for r in rows if r['status'] == 'shifted']
print('inserted', len(ins), collections.Counter(r['section'] for r in ins)); print('shifted', len(sh), collections.Counter(r['section'] for r in sh)); print('removed', removed)
print('mismatched shifts', [r for r in sh if 'NOTE' in r['reason']][:5])
for r in rows[max(lo, 0):hi]: print(r)
