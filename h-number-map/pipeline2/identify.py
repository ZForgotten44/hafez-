"""Step 3: connect every label in the CAD drawing to a decoder lot and classify the result.

Evidence used for each lot (nothing here invents a lot or an H-number):
  * the label text itself (real text in the CAD file, no OCR),
  * the cell outline that encloses it (lots.py),
  * the decoder (s4/s4decoder1.py) which is the only source of H-numbers,
  * the old OCR placement (placed_lots.csv) as an *independent* cross-check of which legacy section a label belongs to,
  * neighbouring lots, to flag H-numbers that do not fit their surroundings."""
import json, re, csv, math, collections, importlib.util
import numpy as np
from scipy.spatial import cKDTree
from shapely.geometry import Polygon, Point
from shapely import STRtree
from common import *

SECTIONS = 'ABCDEFGHIJKLM'
LABEL_RE = re.compile(r'^[A-Z]?\d+[A-Z]{0,3}$')
LETTERS = {'H', 'A', 'B', 'C'}

def load_decoder():
    spec = importlib.util.spec_from_file_location('dec', DECODER); dec = importlib.util.module_from_spec(spec); spec.loader.exec_module(dec)
    return dec

def register_old(spans_xy):
    """affine (uniform scale + shift) from CAD units to the old overall-map units, refit on label matches"""
    rows = list(csv.DictReader(open(OLD_PLACED)))
    Q = np.array([[float(r['map_x']), float(r['map_y'])] for r in rows])
    A = np.array([[x, y] for t, x, y in spans_xy]); txt = [t for t, x, y in spans_xy]
    s = 0.506; t = Q.min(0) - s * A.min(0); tr = cKDTree(Q)
    for _ in range(8):
        d, j = tr.query(A * s + t)
        m = np.array([txt[i] == rows[j[i]]['old_lot_label'] for i in range(len(A))]) & (d < 3)
        Aa, Qq = A[m], Q[j[m]]; ca, cq = Aa.mean(0), Qq.mean(0)
        s = ((Aa - ca) * (Qq - cq)).sum() / ((Aa - ca) ** 2).sum(); t = cq - s * ca
    return s, t, rows

def decode_options(dec, tokens):
    """tokens: text pieces already in reading order.  Returns {(section,label): (hnum, htext)} for every spelling
    that the decoder recognises."""
    cands = []
    joined = ''.join(tokens); cands.append(joined)
    if len(tokens) > 1:
        cands.append(''.join(reversed(tokens)))
    for c in list(cands):
        m = re.match(r'^([A-Z]+)(\d+)$', c)
        if m: cands.append(m.group(2) + m.group(1))
    out = {}
    for c in dict.fromkeys(cands):
        for s in SECTIONS:
            n, f = dec.h_lot(s, c)
            if n is not None: out[(s, c)] = (n, f)
    return out

def run():
    dec = load_decoder()
    D = json.load(open(f'{DATA}/ai_raw.json')); C = json.load(open(f'{DATA}/cells.json'))
    polys = [Polygon(c['poly']).buffer(0) for c in C]; tree = STRtree(polys)
    spans = [s for s in D['spans'] if s['size'] < 3.1]
    # ---- keep only spans that look like lot labels
    lab_spans = []
    for s in spans:
        t = s['t'].replace(' ', '') if re.fullmatch(r'\d+ ?[A-Z]', s['t']) else s['t']
        if LABEL_RE.match(t) or t in LETTERS:
            lab_spans.append(dict(s, t=t, cx=(s['bbox'][0] + s['bbox'][2]) / 2, cy=(s['bbox'][1] + s['bbox'][3]) / 2))
    # ---- group by cell (label point inside outline); outside any outline -> stand-alone label
    by_cell = collections.defaultdict(list); loose = []
    for s in lab_spans:
        hit = tree.query(Point(s['cx'], s['cy']), predicate='within')
        (by_cell[int(hit[0])] if len(hit) else loose).append(s)
    groups = []
    for ci, ss in by_cell.items():
        groups.append(dict(cell=ci, spans=ss))
    # stand-alone: letters attach to the nearest number span within a lot-label distance
    nums = [s for s in loose if s['t'] not in LETTERS]; lets = [s for s in loose if s['t'] in LETTERS]
    gl = [dict(cell=None, spans=[s]) for s in nums]
    if nums:
        ntree = cKDTree([[s['cx'], s['cy']] for s in nums])
        for L in lets:
            d, k = ntree.query([L['cx'], L['cy']])
            if d < 6: gl[k]['spans'].append(L)
            else: gl.append(dict(cell=None, spans=[L]))
    groups += gl
    # ---- reading order, geometry
    for g in groups:
        ss = g['spans']
        a = math.radians(np.median([s['ang'] for s in ss])); u = np.array([math.cos(a), math.sin(a)])
        ss.sort(key=lambda s: np.array([s['cx'], s['cy']]) @ u)
        g['tokens'] = [s['t'] for s in ss]; g['ang'] = math.degrees(a)
        g['pt'] = (float(np.mean([s['cx'] for s in ss])), float(np.mean([s['cy'] for s in ss])))
        g['bbox'] = [min(s['bbox'][0] for s in ss), min(s['bbox'][1] for s in ss), max(s['bbox'][2] for s in ss), max(s['bbox'][3] for s in ss)]
        g['opts'] = decode_options(dec, g['tokens'])
    # ---- registration to old OCR placement (cross-check anchors)
    s_, t_, old = register_old([(s['t'], s['cx'], s['cy']) for s in lab_spans if s['t'] not in LETTERS])
    otree = cKDTree([[float(r['map_x']), float(r['map_y'])] for r in old])
    for g in groups:
        x, y = g['pt'][0] * s_ + t_[0], g['pt'][1] * s_ + t_[1]
        d, j = otree.query([x, y]); r = old[j]
        g['old'] = dict(section=r['section'], label=r['old_lot_label'], h=r['h_number'], dist=round(float(d), 2)) if d < 1.5 else None
    # ---- resolve section.  Region first (which legacy section does this part of the cemetery belong to?),
    #      then decode the label inside that section only.
    anc_sec = [r['section'] for r in old]
    for gi, g in enumerate(groups):
        g['id'] = gi; g['section'] = None; g['label'] = None; g['evidence'] = []; g['flags'] = []
        x, y = g['pt'][0] * s_ + t_[0], g['pt'][1] * s_ + t_[1]
        d, idx = otree.query([x, y], k=9, distance_upper_bound=28 * s_ / 0.5 * 0.5)
        votes = collections.Counter(anc_sec[i] for i, dd in zip(idx, d) if np.isfinite(dd))
        tot = sum(votes.values())
        g['region'] = dict(votes) if tot else {}
        g['region_sec'] = votes.most_common(1)[0][0] if tot else None
        g['region_agree'] = round(votes.most_common(1)[0][1] / tot, 2) if tot else 0
        opts = g['opts']; secs = sorted({s for s, _ in opts}); g['cands'] = secs
        if not opts:
            g['flags'].append('label_not_in_decoder'); continue
        o = g['old']
        if o and (o['section'], o['label']) in opts:
            g['section'], g['label'] = o['section'], o['label']; g['evidence'].append('old_ocr_agrees')
        elif g['region_sec'] and g['region_agree'] >= 0.6 and g['region_sec'] in secs:
            g['section'] = g['region_sec']; g['label'] = next(l for ss, l in opts if ss == g['section'])
            g['evidence'].append('region_vote_%d%%' % round(100 * g['region_agree']))
        elif len(secs) == 1 and not tot:
            k = next(iter(opts)); g['section'], g['label'] = k; g['evidence'].append('only_section_with_label_no_region_data'); g['flags'].append('no_region_evidence')
        else:
            g['flags'].append('label_not_in_region_section' if tot else 'section_undetermined')
        if o and g['section'] and o['section'] != g['section']: g['flags'].append('old_ocr_disagrees')
    # ---- areas with no region evidence (e.g. the mausoleum garden): a connected cluster of labels must all belong to ONE
    #      section, so keep a section only if it is the single section in which every label of the cluster exists
    und = [g for g in groups if 'section_undetermined' in g['flags']]
    if und:
        from scipy.sparse.csgraph import connected_components
        from scipy.sparse import coo_matrix
        ut = cKDTree([g['pt'] for g in und]); pairs = ut.query_pairs(14.0, output_type='ndarray')
        n = len(und); M = coo_matrix((np.ones(len(pairs)), (pairs[:, 0], pairs[:, 1])), shape=(n, n))
        _, comp = connected_components(M, directed=False)
        for c in set(comp):
            mem = [und[i] for i in range(n) if comp[i] == c]
            if len(mem) < 6: continue
            common = set(mem[0]['cands'])
            for g in mem[1:]: common &= set(g['cands'])
            if len(common) == 1:
                sec = next(iter(common))
                for g in mem:
                    g['section'] = sec; g['label'] = next(l for ss, l in g['opts'] if ss == sec)
                    g['flags'].remove('section_undetermined'); g['evidence'].append('cluster_of_%d_labels_fit_only_section_%s' % (len(mem), sec))
    # ---- H numbers + duplicate claims
    claim = collections.defaultdict(list)
    for g in groups:
        if g['section']:
            n, f = g['opts'][(g['section'], g['label'])]; g['hnum'], g['htext'] = n, f
            claim[(g['section'], g['label'])].append(g['id'])
    for key, ids in claim.items():
        if len(ids) > 1:
            for i in ids: groups[i]['flags'].append('duplicate_label_in_section')
    # ---- plausibility vs neighbours (same section, H-number should be close to neighbours' median)
    sec_pts = collections.defaultdict(list)
    for g in groups:
        if g['section'] and 'duplicate_label_in_section' not in g['flags']: sec_pts[g['section']].append(g)
    for s, gs in sec_pts.items():
        if len(gs) < 8: continue
        tr = cKDTree([g['pt'] for g in gs]); H = np.array([g['hnum'] for g in gs], float)
        d, idx = tr.query([g['pt'] for g in gs], k=min(7, len(gs)))
        for i, g in enumerate(gs):
            nb = H[idx[i][1:]]; med = np.median(nb)
            g['nbr_dev'] = float(abs(H[i] - med))
    for g in groups: g['opts'] = [[a, b, n, f] for (a, b), (n, f) in g['opts'].items()]
    json.dump(dict(scale=s_, shift=list(t_), groups=groups, cells=len(C)), open(f'{DATA}/identified.json', 'w'), default=float)
    st = collections.Counter()
    for g in groups:
        st['section' if g['section'] else 'none'] += 1
        for f in g['flags']: st[f] += 1
    print('groups', len(groups), dict(st))
if __name__ == '__main__': run()
