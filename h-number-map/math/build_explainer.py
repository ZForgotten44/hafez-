"""Fill explainer_template.html: data, images (data URIs), snippets, script  ->  Cedar_Grove_Numbering_Explained.html"""
import json, re, base64, os, inspect, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
here = os.path.dirname(os.path.abspath(__file__)); os.chdir(here)
X = json.load(open('explainer_data.json'))
G = json.load(open('giant_parts.json')); X['giant']['parts'] = G['parts']
def grab(path, name):
    src = open(path).read().split('\n'); out = None
    for i, l in enumerate(src):
        if re.match(r'(def|[A-Za-z_]+ *=) *' + re.escape(name) + r'\b', l) or l.startswith('def ' + name + '('):
            j = i + 1
            while j < len(src) and (src[j].startswith((' ', '\t')) or src[j] == '' ): j += 1
            out = '\n'.join(src[i:j]).rstrip(); break
    return out
D = '../../s4/s4decoder1.py'; F = 'hformula.py'
DESC = {
 'build_B_decoder': ('Builds the table that turns a Section B label into its column and level.', ('Step 1 · the B and A sweep', '#p1')),
 'build_A_decoder': ('Builds the same table for Section A, including where the H-lots fall.', ('Step 2 · H-lots push labels along', '#p2')),
 '_build_dc_tables': ('Builds the running-total tables for sections D and C, so each row knows how many lots come before it.', ('Step 3 · rows of different widths', '#p3')),
 'h_lot': ('Takes a section and a label and returns the lot\'s H-number. This is the function the one-line formula reproduces.', ('Section 07 · the giant formula', '#giant')),
 'h_grave': ('Adds the grave digit (and the A or B letter) to a lot\'s H-number.', ('Step 6 · graves', '#p6')),
 'decode_h': ('Goes the other way: an H-number back to its old section and label.', ('Section 07 · reverse lookup', '#giant')),
 'pre': ('The sum term: how many lots all earlier levels of a two-section pass hold.', ('Step 3 · rows of different widths', '#p3')),
 'H_A_grid': ('Section A: label to H using 19 labels per row and three H-lots per row.', ('Step 2 · H-lots push labels along', '#p2')),
 'H_B_grid': ('Section B: label to H for the body, the last column and the H-lots.', ('Step 2 · Section B rules', '#p2')),
 'H_D': ('Section D: label to H across uneven rows, blocks and H-lots.', ('Step 3 · rows of different widths', '#p3')),
 'H_C': ('Section C: label to H using each row\'s top lot, twins and trios.', ('Step 4 · twins and trios', '#p4')),
 'H_F': ('Section F: 18 labels per row, plus the margin lots 199 to 210.', ('Step 5 · straight-line sections', '#p5')),
 'H_E': ('Section E: 19 per row with twins, plus the lettered lots in rows 9 to 12.', ('Step 4 · twins and trios', '#p4')),
 'H_G': ('Section G: 19 per row, plus lots 58 to 75.', ('Step 3 · running totals', '#p3')),
 'H_H': ('Section H: 23 per row, four rows.', ('Step 3 · running totals', '#p3')),
 'H_M': ('Section M: n + 2556 from lot 82, and a stored list below that.', ('Step 5 · straight-line sections', '#p5')),
 'H_K': ('Section K: the position of the label in a stored list of 115.', ('Step 5 · straight-line sections', '#p5')),
 'H_J': ('Section J: 2950 + n.', ('Step 5 · straight-line sections', '#p5')),
 'H_I': ('Section I: 3082 + n.', ('Step 5 · straight-line sections', '#p5')),
 'H_L': ('Section L: 3146 + (n − 68).', ('Step 5 · straight-line sections', '#p5')),
 'H': ('The dispatcher: parse the label, call the section\'s function, apply the known errata.', ('Section 07 · the giant formula', '#giant'))}
def items(path, names):
    out = []
    for n in names:
        src = grab(path, n)
        if src:
            d = DESC.get(n, ('', None))
            out.append(dict(name=n, file=path.replace('../../', ''), src=src, desc=d[0], demo=d[1]))
    return out
X['snips'] = [
 dict(title='Existing decoder', note='From s4/s4decoder1.py, the code that was already in the project. It builds and reads the legacy labels from per-section tables.', items=items(D, ['build_B_decoder', 'build_A_decoder', '_build_dc_tables', 'h_lot', 'h_grave', 'decode_h'])),
 dict(title='Arithmetic rebuild', note='From h-number-map/math/hformula.py, written for this page: closed forms for every section, checked against the decoder.', items=items(F, ['pre', 'H_A_grid', 'H_B_grid', 'H_D', 'H_C', 'H_F', 'H_E', 'H_G', 'H_H', 'H_M', 'H_K', 'H_J', 'H_I', 'H_L', 'H']))]
X['img'] = {}
for n in ('old_overview','new_overview','old_dense','new_dense','old_curved','new_curved'):
    X['img'][n] = 'data:image/jpeg;base64,' + base64.b64encode(open('img/%s.jpg' % n, 'rb').read()).decode()
html = open('explainer_page.html').read()
def img(m):
    p = 'img/' + m.group(1)
    for ext in ('.jpg', '.png'):
        if os.path.exists(p + ext):
            return 'data:image/%s;base64,%s' % ('jpeg' if ext == '.jpg' else 'png', base64.b64encode(open(p + ext, 'rb').read()).decode())
    raise SystemExit('missing image ' + p)
html = re.sub(r'__IMG_(\w+?)__', img, html)
from PIL import Image
def ar(m):
    n = m.group(1); p = 'img/' + n + ('.jpg' if os.path.exists('img/' + n + '.jpg') else '.png'); i = Image.open(p); return '%.4f' % (i.width / i.height)
html = re.sub(r'__AR_(\w+?)__', ar, html)
def b64(p): return base64.b64encode(open(p, 'rb').read()).decode()
FONTS = '@font-face{font-family:"Space Grotesk";font-style:normal;font-weight:300 700;font-display:swap;src:url(data:font/woff2;base64,%s) format("woff2")}' % b64('fonts/SpaceGrotesk-400.woff2')
for w in (400, 500, 600):
    FONTS += '@font-face{font-family:"IBM Plex Mono";font-style:normal;font-weight:%d;font-display:swap;src:url(data:font/woff2;base64,%s) format("woff2")}' % (w, b64('fonts/IBMPlexMono-%d.woff2' % w))
html = html.replace('/*__FONTS__*/', FONTS)
data = json.dumps(X, separators=(',', ':')).replace('</', '<\\/')
html = html.replace('/*__DATA__*/null', data).replace('/*__SCRIPT__*/', (open('explainer_a.js').read() + open('explainer_b.js').read().replace('/* ---------------- section 4','var IMG=X.img;\n/* ---------------- section 4',1)).replace('</script', '<\\/script'))
open('Cedar_Grove_Numbering_Explained.html', 'w').write(html)
print(len(html) // 1024, 'KB', [len(s['items']) for s in X['snips']])
