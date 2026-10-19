"""Step 1: read the CAD export (vector PDF/AI) and dump every drawing + every text span.
The lot numbers in this file are real text, not stroke glyphs, so they never need OCR."""
import json, math, pymupdf
from common import *

def r(v): return round(v, 3)
def run():
    page = pymupdf.open(AI_SRC)[0]
    draws = []
    for d in page.get_drawings():
        items = []
        for it in d['items']:
            op = it[0]
            if op == 'l': items.append(['l', r(it[1].x), r(it[1].y), r(it[2].x), r(it[2].y)])
            elif op == 'c': items.append(['c'] + [r(v) for p in it[1:5] for v in (p.x, p.y)])
            elif op == 're': items.append(['re', r(it[1].x0), r(it[1].y0), r(it[1].x1), r(it[1].y1)])
            elif op == 'qu':
                q = it[1]; items.append(['qu'] + [r(v) for p in (q.ul, q.ur, q.lr, q.ll) for v in (p.x, p.y)])
        draws.append(dict(color=[round(c, 2) for c in (d['color'] or ())], fill=[round(c, 2) for c in (d['fill'] or ())],
                          w=round(d['width'] or 0, 2), closed=bool(d.get('closePath')), items=items))
    spans = []
    for b in page.get_text('dict')['blocks']:
        for l in b.get('lines', []):
            ang = math.degrees(math.atan2(l['dir'][1], l['dir'][0]))
            for s in l['spans']:
                if s['text'].strip():
                    spans.append(dict(t=s['text'].strip(), size=round(s['size'], 2), ang=round(ang, 1),
                                      bbox=[r(v) for v in s['bbox']], origin=[r(v) for v in s['origin']]))
    json.dump(dict(page=[page.rect.width, page.rect.height], draws=draws, spans=spans), open(f'{DATA}/ai_raw.json', 'w'))
    print('drawings', len(draws), 'text spans', len(spans))
if __name__ == '__main__': run()
