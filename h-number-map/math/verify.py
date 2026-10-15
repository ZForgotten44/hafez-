import json, collections, importlib
import hformula; importlib.reload(hformula)
D = json.load(open('decoder_dump.json')); fwd = D['fwd']
ok = collections.Counter(); bad = []
for s, l, h in fwd:
    try: v, t = hformula.H(s, l)
    except Exception as e: v, t = None, 'EXC %s' % e
    if v == h: ok[(s, t)] += 1
    else: bad.append((s, l, h, v, t))
print('matched', sum(ok.values()), 'of', len(fwd), '| mismatches', len(bad))
by = collections.defaultdict(list)
for b in bad: by[b[0]].append(b)
for s in by: print(s, len(by[s]), by[s][:6])
tiers = collections.Counter()
for (s, t), c in ok.items(): tiers[t] += c
print(dict(tiers))
