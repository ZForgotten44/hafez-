"""Crosswalk between the two numbering versions (v1 = s4/s4decoder_v1.py, frozen; v2 = s4/s4decoder1.py) and the H-ID view of the burial workbooks.

Writes into h-number-map/crosswalk/:
  crosswalk_v1_to_v2.csv                      one line per affected grave (the numbering v2 ships: east-tip lots M 11, 12, 16 kept)
  crosswalk_v1_to_v2_if_east_tip_withdrawn.csv the same if staff confirm M 11, 12 and 16 were withdrawn (three numbers fewer)
  records_h_ids_v2.csv                         every burial-workbook grave (sections J, K, M) with its v1 and v2 H-ID, record ID first, no names
  crosswalk_search.html                        one file: search any H-ID (old or new), or section + lot + grave, in either map version
  crosswalk_checks.txt                         the verification that was run (see verify_crosswalk())
Names are never copied: the workbooks key people by section, lot and grave, and both H-IDs are derived from that key."""
import csv, importlib.util, json, os, re, sys, collections
import openpyxl
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, '..', '..')); OUT = os.path.join(REPO, 'h-number-map', 'crosswalk')
sys.path.insert(0, os.path.join(REPO, 's4'))
os.makedirs(OUT, exist_ok=True)

def load(path, patch=None):
    src = open(path).read()
    if patch: src = src.replace(*patch)
    spec = importlib.util.spec_from_loader('dec_' + str(abs(hash(path + str(patch)))), loader=None); m = importlib.util.module_from_spec(spec)
    exec(compile(src, path, 'exec'), m.__dict__); return m

V1 = load(os.path.join(REPO, 's4', 's4decoder_v1.py'))
V2 = load(os.path.join(REPO, 's4', 's4decoder1.py'))
V2W = load(os.path.join(REPO, 's4', 's4decoder1.py'), ("M_EASTTIP_STATUS = 'active'", "M_EASTTIP_STATUS = 'withdrawn'"))
SECS = 'ABCDEFGHIJKLM'

def lot_tables(dec):
    """section -> {lot_label: (H, route_row)}; every section A-M comes from the decoder's own full_table, so the crosswalk covers all moved lots"""
    out = {}
    for sec in SECS:
        out[sec] = {}
        try: rows = dec.full_table(sec)
        except Exception: rows = []
        for r in rows: out[sec][r['lot_label']] = (r['h_lot_number'], r.get('row_r'))
    rws = dict(M=dec._M_ROWS, K=dec._K_ROWS, J=dec._J_ROWS, I=dec._I_ROWS, L=dec._L_ROWS)
    for s_, rows in rws.items():
        row_of = {}
        for r, lots in rows.items():
            for l in lots: row_of.setdefault(l, r)
        for l, (h, _) in list(out[s_].items()): out[s_][l] = (h, row_of.get(l))
    return out
import subprocess, tempfile
_rp = os.path.join(tempfile.gettempdir(), 's4decoder_review_d990927.py'); open(_rp, 'wb').write(subprocess.check_output(['git', '-C', REPO, 'show', 'd990927:s4/s4decoder1.py']))
VREV = load(_rp)
T1, T2, T2W, TR = lot_tables(V1), lot_tables(V2), lot_tables(V2W), lot_tables(VREV)

def records(sec):
    p = os.path.join(REPO, 'Section %s.xlsx' % sec)
    if not os.path.exists(p): return None
    ws = openpyxl.load_workbook(p, read_only=True).worksheets[0]; out = collections.OrderedDict()
    for r in ws.iter_rows(min_row=2, values_only=True):
        if not r[0]: continue
        m = re.match(r'CEDARGROVE-%s-(\w+)-(\d+)-?' % sec, r[0])
        if m: out.setdefault(m.group(1), []).append((int(m.group(2)), r[0], r[2]))
    return out
REC = {s: records(s) for s in SECS}

def hg(h, g): return 'H%07d' % (h * 10 + g)
def hl(h): return 'H%06d' % h

def graves_of(s, lot):
    if REC[s] and lot in REC[s]: return [(g, rid, 'burial workbook lot and grave') for g, rid, st in REC[s][lot]]
    return [(g, '', 'lot position (no burial records for this section; graves 1-6 as in the published tables)' if not REC[s] else 'lot position (lot not in the burial workbook; graves 1-6)') for g in range(1, 7)]

def reason_of(s, lot, o, n):
    if not o: return 'new lot in the current numbering: verified distinct outline inserted in route order'
    if not n: return 'retired: no number in the current numbering (pending staff confirmation)'
    if s == 'B': return 'B: the v1 last-column rule is removed; labels sit at their own places between their neighbours (and B 20 / plain lots added)'
    if s == 'D': return 'D: row heads relabelled to the printed lots, row 15 reads 293 not 274, plain 311/322/333 and 20H/9H added'
    if s == 'M': return 'M: real lot (burial workbook, 2022 drawing) numbered in route order; moved by lots inserted before it'
    return 'moved by the lots inserted earlier on the route (see crosswalk/shift_table_lots.csv for the run and reason)'

def build_rows(T_old, T_new):
    rows = []
    for s in SECS:
        for lot in sorted(set(T_old[s]) | set(T_new[s]), key=lambda x: (int(re.sub(r'\D', '', x) or 0), x)):
            o = T_old[s].get(lot); n = T_new[s].get(lot)
            if o and n and o[0] == n[0]: continue            # unaffected: same H in both versions
            if o and n: change = 'renumbered %+d' % (n[0] - o[0])
            elif n: change = 'new lot: no v1 number'
            else: change = 'retired: no v2 number (pending staff confirmation)'
            for g, rid, basis in graves_of(s, lot):
                rows.append(dict(reason=reason_of(s, lot, o, n), section=s, lot_label=lot, route_row_v2=(n[1] if n else ''), route_row_v1=(o[1] if o else ''), grave=g, v1_h_lot=hl(o[0]) if o else '', v2_h_lot=hl(n[0]) if n else '',
                                 v1_h_grave=hg(o[0], g) if o else '', v2_h_grave=hg(n[0], g) if n else '', change=change, record_id=rid, anchor=basis))
    return rows

def write_csv(path, rows):
    cols = ['section', 'lot_label', 'route_row_v2', 'route_row_v1', 'grave', 'v1_h_lot', 'v2_h_lot', 'v1_h_grave', 'v2_h_grave', 'change', 'reason', 'record_id', 'anchor']
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, cols); w.writeheader(); w.writerows(rows)

def records_csv(path):
    with open(path, 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['record_id', 'section', 'lot_label', 'grave', 'status', 'v1_h_grave', 'review_commit_h_grave', 'v2_h_grave', 'changed_since_review', 'changed_since_v1'])
        for s in 'JKM':
            for lot, gl in REC[s].items():
                o = T1[s].get(lot); n = T2[s].get(lot); r_ = TR[s].get(lot)
                for g, rid, st in gl:
                    w.writerow([rid, s, lot, g, st, hg(o[0], g) if o else '', hg(r_[0], g) if r_ else '', hg(n[0], g) if n else '', 'yes' if (not r_ or not n or r_[0] != n[0]) else 'no', 'yes' if (not o or not n or o[0] != n[0]) else 'no'])

def decode(dec, h):
    """lot-level reverse lookup through the decoder itself: (section, lot) or None"""
    try:
        r = dec.decode_h(h)
    except Exception: return None
    return r

def verify_crosswalk(rows, rowsW):
    """checks, all run against the decoders (not against this file's own logic):
       1. every v2 H-grave ID decodes (decoder.decode_h on the lot part) to the same section and lot, and the grave digit is the grave
       2. every v1 H-grave ID decodes under the v1 decoder to the same section, lot and grave
       3. for sections with burial records, every workbook grave is present in the crosswalk or unchanged, and the record's section-lot-grave is the row's
       4. no two lots share a v2 H-number in M, K, J, I, L; first and last IDs of K, J, I, L against the rebuilt tables
       5. the hazard: how many old IDs now name a different lot"""
    log = []; bad = 0
    for r in rows:
        if r['v2_h_grave']:
            h = int(r['v2_h_grave'][1:]); lot_h, g = divmod(h, 10); d = V2.decode_h(lot_h)
            ok = d and d['section'] == r['section'] and d['lot_label'] == r['lot_label'] and g == r['grave']
            if not ok: bad += 1; log.append('v2 mismatch %s' % r)
        if r['v1_h_grave']:
            h = int(r['v1_h_grave'][1:]); lot_h, g = divmod(h, 10); d = V1.decode_h(lot_h)
            ok = d and d['section'] == r['section'] and d['lot_label'] == r['lot_label'] and g == r['grave']
            if not ok: bad += 1; log.append('v1 mismatch %s' % r)
    log.append('1-2. %d crosswalk graves: v2 and v1 IDs decode back to their own section, lot and grave; failures: %d' % (len(rows), bad))
    nrec = 0; badrec = 0; changed_graves = 0
    for s in 'JKM':
        for lot, gl in REC[s].items():
            for g, rid, st in gl:
                nrec += 1
                n = T2[s].get(lot); o = T1[s].get(lot)
                if not n: badrec += 1; log.append('record without v2 lot: %s' % rid); continue
                d = V2.decode_h(n[0])
                if not (d and d['section'] == s and d['lot_label'] == lot): badrec += 1
                if not o or o[0] != n[0]: changed_graves += 1
    chg = {(r['section'], r['lot_label'], r['grave']) for r in rows if r['record_id']}
    miss = sum(1 for s in 'JKM' for lot, gl in REC[s].items() for g, rid, st in gl if ((not T1[s].get(lot)) or T1[s][lot][0] != T2[s][lot][0]) and (s, lot, g) not in chg)
    log.append('3. %d burial-workbook graves (J, K, M): every one resolves to a v2 lot with the same section and lot; %d of them changed ID and %d of those are missing from the crosswalk' % (nrec, changed_graves, miss))
    for s in SECS:
        hs = [h for h, _ in T2[s].values()]
        log.append('4. Section %s: %d lots, v2 first %s last %s, v1 first %s last %s, duplicates %d' % (s, len(hs), hl(min(hs)), hl(max(hs)), hl(min(h for h, _ in T1[s].values())), hl(max(h for h, _ in T1[s].values())), len(hs) - len(set(hs))))
    old_now = collections.Counter()
    for s in SECS:
        for lot, (h, _) in T1[s].items():
            d = V2.decode_h(h)
            if d and (d['section'], d['lot_label']) != (s, lot): old_now['old lot ID now names another lot'] += 1
            elif not d: old_now['old lot ID no longer exists'] += 1
            else: old_now['unchanged'] += 1
    log.append('5. old lot IDs of M, K, J, I, L under the v2 decoder: %s' % dict(old_now))
    log.append('   withdrawn scenario: v2W has %d M lots, K starts %s, L ends %s' % (len(T2W['M']), hl(min(h for h, _ in T2W['K'].values())), hl(max(h for h, _ in T2W['L'].values()))))
    return log, bad + badrec

SEARCH = r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Cedar Grove H-ID lookup, v1 and v2</title>
<style>body{font:18px/1.45 system-ui,Arial,sans-serif;margin:0;background:#fbfaf6;color:#0c2340}main{max-width:880px;margin:0 auto;padding:28px 20px 60px}h1{font-size:28px;margin:0 0 4px}p.s{color:#566;margin:0 0 20px}
input{font:22px ui-monospace,Menlo,monospace;padding:12px 14px;width:100%;box-sizing:border-box;border:2px solid #0c2340;border-radius:10px}.row{display:flex;gap:10px;margin:10px 0 18px}.row button{font:16px system-ui;padding:8px 14px;border:1px solid #0c2340;background:#fff;border-radius:8px;cursor:pointer}
.card{background:#fff;border:1px solid #cfd3da;border-radius:12px;padding:16px 18px;margin:12px 0}.card b.t{display:block;font-size:14px;letter-spacing:.04em;text-transform:uppercase;color:#566;margin-bottom:4px}.big{font:700 26px ui-monospace,Menlo,monospace}.warn{border-color:#c9892f;background:#fdf3e1}.ok{border-color:#3f9a63}.muted{color:#566;font-size:15px}code{font-family:ui-monospace,Menlo,monospace}</style></head><body><main>
<h1>Cedar Grove H-ID lookup</h1><p class="s">Type an H-ID (H002620, H0026203, 2620) or a section, lot and grave (M 61 3). Both numbering versions are searched: v1 is the numbering before the Section M rebuild, v2 is the current one (it includes the route-order rebuild of this pass).</p>
<input id="q" autofocus placeholder="H0026203   or   M 61 3" autocomplete="off"><div class="row"><button data-q="M 61 3">M 61 3</button><button data-q="H002620">H002620</button><button data-q="H0026203">H0026203</button><button data-q="K 1">K 1</button><button data-q="L 107">L 107</button></div><div id="out"></div>
<p class="muted">Map versions. <b>v1</b>: H000001 to H003185. <b>v2</b>: H000001 to H003218: Section B corrected (the last-column rule removed, plain lots added), Section M's six lots 56, 57, 62, 63, 68, 69 inserted in route order, every number after them moved up. Sections A and C to H are the same in both versions; in B the 19 labels 12, 31, 50 ... moved to their own places and the plain lots 40 ... 360 were added (see the lot list). An old ID can name a different grave in v2, so always say which version a number came from. Burial records are keyed by section, lot and grave, not by H-ID, so a person stays with the same grave when the H-ID changes.</p>
<script>
var D=__DATA__;  /* lots: [section, lot, v1 H or 0, v2 H or 0, route row v2, graves in records or 0] ; unchanged ranges are the same in both versions */
var V1={},V2={},BYL={};D.lots.forEach(function(r){if(r[2])V1[r[2]]=r;if(r[3])V2[r[3]]=r;BYL[r[0]+'|'+r[1]]=r});
function H(n,g){return 'H'+String(n*10+g).padStart(7,'0')}function L(n){return 'H'+String(n).padStart(6,'0')}
function card(cls,t,body){return '<div class="card '+cls+'"><b class="t">'+t+'</b>'+body+'</div>'}
function lotText(r){return 'Section '+r[0]+', lot '+r[1]}
function parse(q){q=q.trim().toUpperCase();var m=q.match(/^H?0*(\d+)$/);if(m){var d=m[1];var n=+d;var raw=q.replace(/^H/,'');
  if(raw.length>=7||(n>=100000&&raw.length>=7)){return {lot:Math.floor(n/10),g:n%10}}return {lot:n,g:0}}
  m=q.match(/^([A-Z])[\s\-]*([0-9A-Z]+)(?:[\s\-]+(\d))?$/);if(m)return {sec:m[1],label:m[2],g:m[3]?+m[3]:0};return null}
function show(){var q=document.getElementById('q').value,o=document.getElementById('out');o.innerHTML='';if(!q.trim())return;var p=parse(q);if(!p){o.innerHTML=card('warn','Not understood','Type H002620, H0026203 or M 61 3.');return}
 var h='';
 if(p.lot!==undefined){var n=p.lot,g=p.g,a=V1[n],b=V2[n],same=!(a||b);
  if(n>3218||n<1){o.innerHTML=card('warn','Out of range','H-numbers run from H000001 to H003218 in v2 (H003185 in v1).');return}
  var w=g?' grave '+g:'';var idv=g?H(n,g):L(n);
  if(same){h+=card('ok','Same in v1 and v2','<span class="big">'+idv+'</span><br>No lot carries this number in either version (it is an unused route number or outside H000001 to H003218).');o.innerHTML=h;return}
  if(b)h+=card(a&&a[0]==b[0]&&a[1]==b[1]?'ok':'warn','As a v2 (current) ID','<span class="big">'+idv+'</span><br>'+lotText(b)+w+(b[5]?'<br><span class="muted">'+b[5]+' graves in the burial records for this lot</span>':'')+'<br>Its v1 (old) ID was '+(b[2]?(g?H(b[2],g):L(b[2])):'none: this lot had no v1 number')+'.');
  else h+=card('warn','As a v2 (current) ID','<span class="big">'+idv+'</span><br>No lot carries this number in v2 (it is not in a section that moved, or it is retired).');
  if(a)h+=card(b&&a[0]==b[0]&&a[1]==b[1]?'ok':'warn','As a v1 (old) ID','<span class="big">'+idv+'</span><br>'+lotText(a)+w+'<br>In v2 that same lot'+w+' is <b class="big" style="font-size:20px">'+(a[3]?(g?H(a[3],g):L(a[3])):'RETIRED')+'</b>'+(b&&(a[0]!=b[0]||a[1]!=b[1])?'<br><b>Careful:</b> the number '+idv+' now belongs to '+lotText(b)+w+', a different grave.':''));
  else h+=card('','As a v1 (old) ID','No lot had this number in v1'+(b?': it was assigned to '+lotText(b)+' in the v2 rebuild.':'.'));
 }else{var r=BYL[p.sec+'|'+p.label];if(!r){o.innerHTML=card('warn','Not a lot in the numbering','Section '+p.sec+' lot '+p.label+' is not in the numbering table (check the label).');return}
  var g=p.g,w=g?' grave '+g:'';
  h+=card('ok','Section '+p.sec+', lot '+p.label+w,'v1 (old): <span class="big">'+(r[2]?(g?H(r[2],g):L(r[2])):'none')+'</span><br>v2 (current): <span class="big">'+(r[3]?(g?H(r[3],g):L(r[3])):'RETIRED')+'</span>'+(r[4]?'<br><span class="muted">route row '+r[4]+' in v2'+(r[5]?'; '+r[5]+' graves in the burial records':'')+'</span>':''));}
 o.innerHTML=h}
document.getElementById('q').addEventListener('input',show);Array.prototype.forEach.call(document.querySelectorAll('button[data-q]'),function(b){b.onclick=function(){document.getElementById('q').value=b.dataset.q;show()}});show();
</script></main></body></html>'''

def run():
    rows = build_rows(T1, T2); rowsW = build_rows(T1, T2W)
    write_csv(os.path.join(OUT, 'crosswalk_v1_to_v2.csv'), rows); write_csv(os.path.join(OUT, 'crosswalk_v1_to_v2_if_east_tip_withdrawn.csv'), rowsW); records_csv(os.path.join(OUT, 'records_h_ids_v2.csv'))
    lots = []
    for s in SECS:
        for lot in set(T1[s]) | set(T2[s]):
            o = T1[s].get(lot); n = T2[s].get(lot)
            lots.append([s, lot, o[0] if o else 0, n[0] if n else 0, (n[1] if n else 0) or 0, len(REC[s][lot]) if REC[s] and lot in REC[s] else 0])
    open(os.path.join(OUT, 'crosswalk_search.html'), 'w').write(SEARCH.replace('__DATA__', json.dumps(dict(lots=lots), separators=(',', ':'))))
    with open(os.path.join(OUT, 'label_aliases.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['section', 'label_on_map', 'table_key', 'h_lot', 'basis', 'status'])
        for lab, h in V2.B_H_ROW_ALIASES.items():
            d = V2.decode_h(h); w.writerow(['B', lab, d['lot_label'], hl(h), 'same position in the 19-lot north-edge H row on the old sheet and the 2022 drawing (jon_questions/B_H_suffix_row.png)', 'either label finds the lot; which one is the ledger name is a question for Jon (Q5)'])
    log, bad = verify_crosswalk(rows, rowsW)
    log.insert(0, 'crosswalk_v1_to_v2.csv: %d affected graves (%d lots), withdrawn scenario: %d graves' % (len(rows), len({(r['section'], r['lot_label']) for r in rows}), len(rowsW)))
    open(os.path.join(OUT, 'crosswalk_checks.txt'), 'w').write('\n'.join(log) + '\n\nfailures: %d\n' % bad); print('\n'.join(log)); print('failures', bad)
    return bad
if __name__ == '__main__': sys.exit(1 if run() else 0)
