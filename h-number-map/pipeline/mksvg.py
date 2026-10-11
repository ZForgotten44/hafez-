import fitz, json, math, pickle, re
from glyphs import get_dr

SRC="/Users/mansyhafez/Downloads/Cemetery - Overall Map (1).pdf"

def num(v):
    return round(v,2)

def path_from_items(items):
    d=[]
    cur=None
    for it in items:
        if it[0]=='l':
            a,b=it[1],it[2]
            if cur is None or (abs(cur[0]-a.x)>0.01 or abs(cur[1]-a.y)>0.01):
                d.append(f"M{num(a.x)} {num(a.y)}")
            d.append(f"L{num(b.x)} {num(b.y)}")
            cur=(b.x,b.y)
        elif it[0]=='c':
            p0,p1,p2,p3=it[1],it[2],it[3],it[4]
            if cur is None or (abs(cur[0]-p0.x)>0.01 or abs(cur[1]-p0.y)>0.01):
                d.append(f"M{num(p0.x)} {num(p0.y)}")
            d.append(f"C{num(p1.x)} {num(p1.y)} {num(p2.x)} {num(p2.y)} {num(p3.x)} {num(p3.y)}")
            cur=(p3.x,p3.y)
        elif it[0]=='re':
            r=it[1]
            d.append(f"M{num(r.x0)} {num(r.y0)} L{num(r.x1)} {num(r.y0)} L{num(r.x1)} {num(r.y1)} L{num(r.x0)} {num(r.y1)} Z")
            cur=None
        elif it[0]=='qu':
            q=it[1]
            d.append(f"M{num(q.ul.x)} {num(q.ul.y)} L{num(q.ur.x)} {num(q.ur.y)} L{num(q.lr.x)} {num(q.lr.y)} L{num(q.ll.x)} {num(q.ll.y)} Z")
            cur=None
    return " ".join(d)

def build_base_svg():
    src=fitz.open(SRC)[0]
    groups={}  # style-key -> list of path d
    for x in get_dr(src):
        col=x['color'] if x['type'] in ('s','fs') else None
        fill=x['fill'] if x['type'] in ('f','fs') else None
        wid=x['width'] or 0.5
        maroon = bool(col and col[0]>0.45 and col[1]<0.25 and col[2]<0.35) or bool(fill and fill[0]>0.45 and fill[1]<0.25 and fill[2]<0.35)
        key=('fill' if fill else 'stroke', maroon, round(wid,2) if not fill else None)
        d=path_from_items(x['items'])
        if not d: continue
        groups.setdefault(key,[]).append(d)
    parts=[]
    layer_order=[('stroke',False),('fill',False),('stroke',True),('fill',True)]
    for kind,maroon in layer_order:
        for key,ds in groups.items():
            if key[0]!=kind or key[1]!=maroon: continue
            dd=" ".join(ds)
            cls = "mr" if maroon else "bk"
            if kind=='fill':
                parts.append(f'<path class="{cls}f" d="{dd}"/>')
            else:
                w=key[2]
                parts.append(f'<path class="{cls}s" style="stroke-width:{w}" d="{dd}"/>')
    return "\n".join(parts)

if __name__=="__main__":
    svg=build_base_svg()
    open('base.svg.frag','w').write(svg)
    print(len(svg), 'chars')
