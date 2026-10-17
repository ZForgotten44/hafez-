import json, importlib.util, os, hformula as F, re
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
spec = importlib.util.spec_from_file_location('dec', os.path.join(REPO, 's4', 's4decoder1.py')); dec = importlib.util.module_from_spec(spec); spec.loader.exec_module(dec)
D = json.load(open('decoder_dump.json')); A = json.load(open('analytics.json')); G = json.load(open('giant_parts.json'))
# anatomy: the first two rows of every section, in sweep order (what a person walking the row would read)
def inv(d, r): return [lab for c in range(1, 23) for lab, (cc, rr) in d.items() if cc == c and rr == r][:22]
anat = {}
for s, dd in (('A', dec.A_DECODER), ('B', dec.B_DECODER)):
    anat[s] = [[l for l in [next((k for k, v in dd.items() if v == (c, r)), None) for c in range(1, 23)]] for r in (1, 2)]
for s in 'CDEFGHIJKLM':
    R = D['rows'][s]; ks = sorted(R, key=int)
    anat[s] = [R[ks[0]], R[ks[1]]]
anat['Bm'] = [D['rows']['Bm'][str(i)] for i in range(1, 10)]
def kind(l):
    if l is None: return 'gap'
    p, n, sf = F.parse(l)
    if n is None: return 'odd'
    if sf == 'H': return 'h'
    if sf in ('A', 'B', 'C'): return 'suffix'
    if p or sf: return 'odd'
    return 'plain'
chips = {s: [[[l, kind(l), (F.H(s if s != 'Bm' else 'B', l)[0] if l else None)] for l in row] for row in rows] if s != 'Bm' else None for s, rows in anat.items() if s != 'Bm'}
lots = json.load(open('../pipeline2/data/lots_fit.json'))
maplots = [[o['s'], o['l'], o['h'], o['hn'], [[round(x, 1), round(y, 1)] for x, y in o['poly']] if o['poly'] else None, o['cx'], o['cy']] for o in lots]
bbox = [359.86, 231.75, 1680.99, 925.88]
data = dict(fwd=D['fwd'], A=dict((k, v) for k, v in A.items()), chips=chips, maplots=maplots, bbox=bbox, giant=dict(expr=G['expr'], decl=G['decl']),
            rows=dict((k, D['rows'][k]) for k in ('D', 'C', 'E', 'G')), consts=D['consts'],
            W=dict(WD=F.WD, WC=F.WC, WF=F.WF, WE=F.WE, WG=F.WG, WH=F.WH, CT=F.CT, TR=sorted(F.CTRIO), CTW=F.CTW))
json.dump(data, open('explainer_data.json', 'w'), separators=(',', ':'))
print('data bytes', os.path.getsize('explainer_data.json'))

# ---- v2 additions: per-label trace (row, place, tier), missing H values, pass ranges
data = json.load(open('explainer_data.json'))
trace = {}
grp = {'B': 'Bm', 'D': 'Dm', 'F': 'Fm'}
for s, l, h in D['fwd']:
    if l.endswith('dr'): continue
    rk = pl = None
    if s in ('A', 'B') and not (s == 'B' and h > 2331):
        dd = dec.A_DECODER if s == 'A' else dec.B_DECODER
        if l in dd: pl, rk = dd[l]
    if rk is None:
        for g in ([grp[s]] if s in grp and h > 2331 else []) + [s]:
            R = D['rows'].get(g)
            if not R: continue
            for r, lst in R.items():
                if l in lst: rk, pl = int(r), lst.index(l) + 1; break
            if rk is not None: break
    v, tier = F.H(s, l)
    trace[s + '|' + l] = [rk, pl, {'closed': 0, 'rows': 1, 'list': 2, 'errata': 3}.get(tier, 3)]
data['trace'] = trace
hs = set(r[2] for r in D['fwd'])
data['missingH'] = sorted(set(range(1, 3186)) - hs)
json.dump(data, open('explainer_data.json', 'w'), separators=(',', ':'))
print('trace', len(trace), 'none rows', sum(1 for v in trace.values() if v[0] is None), 'missing', len(data['missingH']))
