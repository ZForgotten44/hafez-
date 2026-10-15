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
def items(path, names): return [dict(name=n, file=path.replace('../../', ''), src=grab(path, n)) for n in names if grab(path, n)]
X['snips'] = [
 dict(title='The old system: the project decoder', note='These build and read the legacy labels. Each section has its own table or rule, which is the confusing part.', items=items(D, ['build_B_decoder', 'build_A_decoder', '_build_dc_tables', 'h_lot', 'h_grave', 'decode_h'])),
 dict(title='The arithmetic rebuild', note='Closed forms for every section, written for this page and checked against the decoder.', items=items(F, ['pre', 'H_A_grid', 'H_B_grid', 'H_D', 'H_C', 'H_F', 'H_E', 'H_G', 'H_H', 'H_M', 'H_K', 'H_J', 'H_I', 'H_L', 'H']))]
html = open('explainer_template.html').read()
def img(m):
    p = 'img/' + m.group(1)
    for ext in ('.jpg', '.png'):
        if os.path.exists(p + ext):
            return 'data:image/%s;base64,%s' % ('jpeg' if ext == '.jpg' else 'png', base64.b64encode(open(p + ext, 'rb').read()).decode())
    raise SystemExit('missing image ' + p)
html = re.sub(r'__IMG_(\w+?)__', img, html)
data = json.dumps(X, separators=(',', ':')).replace('</', '<\\/')
html = html.replace('/*__DATA__*/null', data).replace('/*__SCRIPT__*/', open('explainer.js').read().replace('</script', '<\\/script'))
open('Cedar_Grove_Numbering_Explained.html', 'w').write(html)
print(len(html) // 1024, 'KB', [len(s['items']) for s in X['snips']])
