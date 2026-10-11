import json, math, html as htmlmod, re
from collections import defaultdict

BASE = open('base.svg.frag').read()
LABELS = json.load(open('labels.json'))          # placed lots (on the map)
MISSING = json.load(open('missing.json'))        # cataloged lots with NO map position
UNMATCHED = json.load(open('unmatched.json'))     # labels read off the map that match no catalog entry
STATS = json.load(open('stats.json'))

SEC_NAME = {
 'A':'Section A','B':'Section B','C':'Section C','D':'Section D','E':'Section E',
 'F':'Section F','G':'Section G','H':'Section H','I':'Section I','J':'Section J',
 'K':'Section K','L':'Section L','M':'Section M'
}
SEC_ORDER = ['A','B','C','D','E','F','G','H','I','J','K','L','M']

def esc(s):
    return htmlmod.escape(str(s), quote=True)

# ---- section bounding boxes (from placed labels) ----
bbox = {}
for l in LABELS:
    b = bbox.setdefault(l['s'], [l['x'], l['x'], l['y'], l['y']])
    b[0] = min(b[0], l['x']); b[1] = max(b[1], l['x'])
    b[2] = min(b[2], l['y']); b[3] = max(b[3], l['y'])

# ---- overall content bbox (all sections, + unmatched markers, + margin) ----
cxs = [v[0] for v in bbox.values()] + [v[1] for v in bbox.values()] + [u['x'] for u in UNMATCHED]
cys = [v[2] for v in bbox.values()] + [v[3] for v in bbox.values()] + [u['y'] for u in UNMATCHED]
MARGIN = 14
CONTENT_BBOX = [min(cxs)-MARGIN, max(cxs)+MARGIN, min(cys)-MARGIN, max(cys)+MARGIN]

# ---- unified search index: placed + unplaced cataloged lots ----
SEARCH = []
for l in LABELS:
    SEARCH.append({'s': l['s'], 'l': l['l'], 'h': l['h'], 'c': l['c'], 'hn': l['hn'],
                    'placed': True, 'x': l['x'], 'y': l['y'], 'a': l['a'], 'w': l['w']})
for m in MISSING:
    if m['l'].endswith('dr'):
        continue  # internal double-row bookkeeping key, not a real searchable lot
    hm = re.match(r'^H0*(\d+)$', m['h'])
    hn = int(hm.group(1)) if hm else None
    SEARCH.append({'s': m['s'], 'l': m['l'], 'h': m['h'], 'c': m['h'][1:].lstrip('0') or '0', 'hn': hn,
                    'placed': False})
SEARCH_JSON = json.dumps(SEARCH, separators=(',', ':'))

# ---- lot cells: grouped hit-rect + label, replaces bare <text> ----
lotcell_parts = []
for i, l in enumerate(LABELS):
    fs = max(1.4, min(2.3, l['w']*0.36))
    deg = -l['a']
    hw = l['w']; hh = max(2.6, l['w']*0.42)
    title = f"Section {l['s']} &#183; Lot {esc(l['l'])} &#8594; {esc(l['h'])}"
    lotcell_parts.append(
        f'<g class="lotcell" data-i="{i}" transform="translate({l["x"]:.2f} {l["y"]:.2f}) rotate({deg:.1f})">'
        f'<rect class="hit" x="{-hw/2:.2f}" y="{-hh/2:.2f}" width="{hw:.2f}" height="{hh:.2f}"/>'
        f'<text class="lot" font-size="{fs:.2f}">{esc(l["c"])}<title>{title}</title></text>'
        f'</g>'
    )
LOTCELLS = "".join(lotcell_parts)

# ---- unmatched markers ----
unmatched_parts = []
for i, u in enumerate(UNMATCHED):
    title = f"Unmatched label near Section {u['region']}: &#8220;{esc(u['label'])}&#8221;"
    unmatched_parts.append(
        f'<g class="unresolved" data-u="{i}" transform="translate({u["x"]:.2f} {u["y"]:.2f})">'
        f'<circle r="1.6"/><title>{title}</title></g>'
    )
UNMATCHED_MARKS = "".join(unmatched_parts)

# ---- section overview overlay (clickable region + clean label, shown only at low zoom) ----
sec_overlay_parts = []
for s in SEC_ORDER:
    if s not in bbox:
        continue
    x0, x1, y0, y1 = bbox[s]
    pad = 3
    x0 -= pad; x1 += pad; y0 -= pad; y1 += pad
    cx, cy = (x0+x1)/2, (y0+y1)/2
    sec_overlay_parts.append(
        f'<g class="sechit" data-sec="{s}">'
        f'<rect x="{x0:.2f}" y="{y0:.2f}" width="{x1-x0:.2f}" height="{y1-y0:.2f}"/>'
        f'<text x="{cx:.2f}" y="{cy:.2f}">Section {s}<title>Section {s} &#8212; {SEC_NAME[s]}</title></text>'
        f'</g>'
    )
SECTION_OVERLAY = "".join(sec_overlay_parts)

# ---- JSON blobs ----
STATS_JSON = json.dumps(STATS, separators=(',', ':'))
BBOX_JSON = json.dumps(bbox, separators=(',', ':'))
CONTENT_BBOX_JSON = json.dumps(CONTENT_BBOX, separators=(',', ':'))

total_placed = sum(s['uniqueH'] for s in STATS)
total_expected = sum(s['expected'] for s in STATS)
total_pct = round(100*total_placed/total_expected)

# ---- sidebar section list (plain: letter, name, no pct/pdf icon) ----
sec_list_items = []
for s in SEC_ORDER:
    sec_list_items.append(
        f'<li data-sec="{s}"><span class="nm">{s}</span><span class="lbl">{SEC_NAME[s]}</span></li>'
    )
SEC_LIST = "".join(sec_list_items)

# ---- coverage table: merged, every cataloged lot, searchable ----
# status: mapped | unmapped(no coords) ; separate unmatched-on-drawing list stays distinct
cov_index = []
for l in LABELS:
    cov_index.append({'s': l['s'], 'l': l['l'], 'h': l['h'], 'status': 'mapped'})
for m in MISSING:
    if m['l'].endswith('dr'):
        continue
    note = m['note'] or ''
    cov_index.append({'s': m['s'], 'l': m['l'], 'h': m['h'], 'status': 'unmapped', 'note': note})
COV_INDEX_JSON = json.dumps(cov_index, separators=(',', ':'))

cov_rows = []
for s in STATS:
    pct = round(100*s['uniqueH']/s['expected']) if s['expected'] else 100
    cov_rows.append(
        f'<tr><td class="mono">{s["s"]}</td><td class="num mono">{s["uniqueH"]:,}</td>'
        f'<td class="num mono">{s["expected"]:,}</td>'
        f'<td class="num"><span class="bar"><span style="width:{pct}%"></span></span> {pct}%</td></tr>'
    )
COVERAGE_ROWS = "".join(cov_rows)

# ---- unmatched-on-drawing table (distinct category) ----
unmatched_rows_html = "".join(
    f'<tr><td class="mono">{esc(u["region"])}</td><td class="mono">{esc(u["label"])}</td></tr>' for u in UNMATCHED
)

TPL = open('template4.html').read()
out = TPL
subs = {
    '__TOTAL_PLACED__': f'{total_placed:,}',
    '__TOTAL_EXPECTED__': f'{total_expected:,}',
    '__TOTAL_PCT__': str(total_pct),
    '__SEC_LIST__': SEC_LIST,
    '__BASE_SVG__': BASE,
    '__UNMATCHED_MARKS__': UNMATCHED_MARKS,
    '__LOTCELLS__': LOTCELLS,
    '__SECTION_OVERLAY__': SECTION_OVERLAY,
    '__COVERAGE_ROWS__': COVERAGE_ROWS,
    '__UNMATCHED_ROWS__': unmatched_rows_html,
    '__UNMATCHED_COUNT__': str(len(UNMATCHED)),
    '__SEARCH_JSON__': SEARCH_JSON,
    '__STATS_JSON__': STATS_JSON,
    '__BBOX_JSON__': BBOX_JSON,
    '__CONTENT_BBOX_JSON__': CONTENT_BBOX_JSON,
    '__COV_INDEX_JSON__': COV_INDEX_JSON,
}
for k, v in subs.items():
    out = out.replace(k, v)

missing_tokens = [k for k in subs if k in out]
print('unreplaced tokens:', missing_tokens)
print('final size:', len(out), 'bytes ~', round(len(out)/1024/1024, 2), 'MB')
bad = [i for i, b in enumerate(out.encode('utf-8')) if b >= 0x80]
print('non-ascii bytes:', len(bad))

open('site4.html', 'w').write(out)
