import json, collections, hformula
def run():
    D = json.load(open('decoder_dump.json')); ok = collections.Counter(); bad = 0; per = collections.defaultdict(lambda: collections.Counter())
    for s, l, h in D['fwd']:
        v, t = hformula.H(s, l)
        if v == h: ok[t] += 1; per[s][t] += 1
        else: bad += 1
    return dict(total=len(D['fwd']), matched=sum(ok.values()), mismatched=bad, tiers=dict(ok), per_section={s: dict(c) for s, c in per.items()})
