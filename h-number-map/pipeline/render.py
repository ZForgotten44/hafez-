import fitz, pickle, math, sys
from glyphs import get_dr
K=4.0
SRC="/Users/mansyhafez/Downloads/Cemetery - Overall Map (1).pdf"
def draw_base(pg,k,only_maroon=False):
    src=fitz.open(SRC)[0]
    sh=pg.new_shape()
    n=0
    for x in get_dr(src):
        if only_maroon:
            c=(x['color'] if x['type'] in('s','fs') else x['fill'])
            if not c or not (c[0]>0.45 and c[1]<0.25 and c[2]<0.35): continue
        col=x['color'] if x['type'] in('s','fs') else None
        fill=x['fill'] if x['type'] in('f','fs') else None
        wid=(x['width'] or 0.5)*k
        for it in x['items']:
            if it[0]=='l': sh.draw_line(fitz.Point(it[1].x*k,it[1].y*k),fitz.Point(it[2].x*k,it[2].y*k))
            elif it[0]=='c': sh.draw_bezier(*[fitz.Point(p.x*k,p.y*k) for p in it[1:5]])
            elif it[0]=='re': sh.draw_rect(fitz.Rect(it[1])*k)
            elif it[0]=='qu': sh.draw_quad(it[1]*k)
        dash=x.get('dashes') or None
        if dash and dash.startswith('[]'): dash=None
        sh.finish(color=col,fill=fill,width=wid,closePath=x.get('closePath') or False,even_odd=bool(x.get('even_odd')),
                  lineCap=(x.get('lineCap') or (0,))[0] if x['type']!='f' else 0,lineJoin=x.get('lineJoin') or 0,dashes=dash,
                  stroke_opacity=x.get('stroke_opacity') if x.get('stroke_opacity') is not None else 1,fill_opacity=x.get('fill_opacity') if x.get('fill_opacity') is not None else 1)
        n+=1
        if n%4000==0: sh.commit(); sh=pg.new_shape()
    sh.commit()
def compact(f):
    # H001871 -> 1871 ; H001690A -> 1690A
    return f[1:].lstrip('0')

def lot_lengths(recs):
    import numpy as np
    from scipy.spatial import cKDTree
    C=np.array([r['ocen'] for r in recs]); tr=cKDTree(C)
    for i,r in enumerate(recs):
        u=np.array([math.cos(r['ang']),math.sin(r['ang'])]); nvec=np.array([-u[1],u[0]])
        best=None
        for j in tr.query_ball_point(C[i],14):
            if j==i: continue
            d=C[j]-C[i]; al=abs(d@u); pe=abs(d@nvec)
            if al>1.5 and pe<0.35*al+0.8 and (best is None or al<best): best=al
        r['lotlen']=best if best else 6.0
def build(out,recs,k=K,extra=None,base='file',full=False):
    doc=fitz.open(); pg=doc.new_page(width=792*k,height=612*k)
    if base=='file':
        b=fitz.open('base_k4.pdf'); pg.show_pdf_page(fitz.Rect(0,0,792*k,612*k),b,0)
    elif base: draw_base(pg,k)
    lot_lengths(recs)
    # erase the old (tiny) labels
    sh=pg.new_shape()
    for r in recs:
        for (x,y,m) in r['glo']:
            h=0.95*m*k
            sh.draw_rect(fitz.Rect(x*k-h,y*k-h,x*k+h,y*k+h))
    sh.finish(color=None,fill=(1,1,1)); sh.commit()
    draw_base(pg,k,only_maroon=True)   # put the maroon section names / callouts back on top of the erase boxes
    def put(txt,cx,cy,ang,fs,color=(0.05,0.1,0.55),font="hebo"):
        L=fitz.get_text_length(txt,fontname=font,fontsize=fs)
        u=(math.cos(ang),math.sin(ang)); n=(-u[1],u[0])
        S=fitz.Point(cx-u[0]*L/2+n[0]*0.35*fs, cy-u[1]*L/2+n[1]*0.35*fs)
        mat=fitz.Matrix(math.cos(ang),-math.sin(ang),math.sin(ang),math.cos(ang),0,0)
        pg.insert_text(S,txt,fontsize=fs,fontname=font,color=color,morph=(S,mat))
    for r in recs:
        txt=r['f'] if full else compact(r['f'])
        fs=min(2.4*r['om'],0.86*r['lotlen']/(0.6*len(txt)))*k
        fs=max(fs,2.6*k/4)
        put(txt,r['ocen'][0]*k,r['ocen'][1]*k,r['ang'],fs)
    if extra: extra(pg,put,k)
    doc.save(out,deflate=True); return doc
