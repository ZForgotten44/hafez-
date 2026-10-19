"""Dump the decoder's complete numbering (every H-number 1..3185, every legacy label it accepts) to JSON for the explainer."""
import importlib.util, json, collections, os
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
spec = importlib.util.spec_from_file_location('dec', os.path.join(REPO, 's4', 's4decoder1.py')); dec = importlib.util.module_from_spec(spec); spec.loader.exec_module(dec)
SECS = 'ABCDEFGHIJKLM'
# forward map: every (section,label) the decoder accepts -> H (include double-row A/B variants)
fwd = {}
for s in SECS:
    for r in dec.full_table(s): fwd[(s, r['lot_label'])] = r['h_lot_number']
for s, base in [('D', b) for b in dec._D_DR_PAIRS]: 
    for suf in 'AB': fwd[('D', base + suf)] = dec.h_lot('D', base + suf)[0]
for lab, base in dec._E_DR_SUFFIX_MAP.items(): fwd[('E', lab)] = dec.h_lot('E', lab)[0]
# reverse sweep: for every H, which label does the decoder print?
rev = {}
for h in range(1, dec._S4_MAX_H + 1):
    d = dec.decode_h(h); rev[h] = (d['section'], d['lot_label']) if d else None
bad = [h for h, v in rev.items() if v is None or v[1] is None]
print('forward labels', len(fwd), 'sweep positions', len(rev), 'positions with no printable label:', len(bad))
round_trip_fail = [(h, v) for h, v in rev.items() if v and v[1] is not None and fwd.get(v) != h]
print('H -> label -> H round-trip failures:', len(round_trip_fail), round_trip_fail[:12])
json.dump(dict(fwd=[[s, l, h] for (s, l), h in sorted(fwd.items(), key=lambda kv: (kv[1], kv[0]))], rev=[[h, v[0] if v else None, v[1] if v else None] for h, v in rev.items()],
               rows=dict(D=dec._D_ROWS, C=dec._C_ROWS, F=dec._F_ROWS, E=dec._E_ROWS, G=dec._G_ROWS, H=dec._H_ROWS, M=dec._M_ROWS, K=dec._K_ROWS, J=dec._J_ROWS, I=dec._I_ROWS, L=dec._L_ROWS,
                         Bm=dec._B_MARGIN_ROWS, Dm=dec._D_MARGIN_ROWS, Fm=dec._F_MARGIN_ROWS), consts=dict(N=22, SWEEP=44, ROWS=19, OFFSET=836, DC_MAX=dec._DC_MAX_H, EF_MAX=dec._EF_MAX_H, S2_MAX=dec._S2_MAX_H, S3_MAX=dec._S3_MAX_H, S4_MAX=dec._S4_MAX_H)),
          open('decoder_dump.json', 'w'))
# label reuse
by = collections.defaultdict(set)
for (s, l), h in fwd.items(): by[l].add(s)
print('distinct label strings', len(by), 'of', len(fwd), 'lots; labels used in 2+ sections:', sum(1 for v in by.values() if len(v) > 1), 'max sections sharing one label:', max(len(v) for v in by.values()))
print(sorted(by.items(), key=lambda kv: -len(kv[1]))[:5])
print('pass-1 positions without label:', [h for h in bad if h <= 836][:40], len([h for h in bad if h <= 836]))
