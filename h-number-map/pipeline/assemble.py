import numpy as np, math, collections
from recog import *
SYM={'0','8','H','1'}      # 180-degree symmetric
PAIR={'9':'6'}         # 9 <-> 6 by 180 rotation
def wrap(a): return (a+math.pi)%(2*math.pi)-math.pi
def cmean(angles,mod=2*math.pi):
    k=2*math.pi/mod; z=np.exp(1j*k*np.array(angles)).sum(); return np.angle(z)/k
def build_glyphs(page,T,minsc=0.72):
    out=[]
    for g in groups(page):
        if not g['segs']: continue
        m=max(g['rect'].width,g['rect'].height)
        if not (2.0<=m<=9): continue
        r=classify(g,T)
        if r is None or r['score']<minsc: continue
        r['m']=m; r['rect']=g['rect']; out.append(r)
    return out
def strings_from(glyphs):
    n=len(glyphs); par=list(range(n))
    def f(a):
        while par[a]!=a: par[a]=par[par[a]]; a=par[a]
        return a
    C=np.array([g['center'] for g in glyphs]); mref=float(np.median([g['m'] for g in glyphs if g['m']>2.6]) if any(g['m']>2.6 for g in glyphs) else 3.4)
    for g in glyphs: g['mm']=max(g['m'],0.85*mref) if g['m']<1.3*mref else g['m']

    from scipy.spatial import cKDTree
    tr=cKDTree(C)
    for i,g in enumerate(glyphs):
        if g['name'] in('H','A','B','C'): pass
        m=g['mm']
        for j in tr.query_ball_point(C[i],1.9*m):
            if j<=i: continue
            h=glyphs[j]; d=C[j]-C[i]
            # candidate reading axis: from either glyph's phi (mod 180)
            ok=False
            for a in (g['phi'],h['phi']):
                u=np.array([math.cos(a),math.sin(a)]); nn=np.array([u[1],-u[0]])
                along=abs(d@u); perp=abs(d@nn)
                ok|= (0.22*m<=along<=1.5*m and perp<=0.45*m)
            dphi=abs((g['phi']-h['phi']+math.pi/2)%math.pi-math.pi/2)
            if ok and abs(math.log(g['mm']/h['mm']))<0.5 and dphi<math.radians(28): par[f(i)]=f(j)
    comp=collections.defaultdict(list)
    for i in range(n): comp[f(i)].append(i)
    return list(comp.values())
def resolve(glyphs,ids,ref=None):
    """return (text, angle, center, height) for a component"""
    gl=[glyphs[i] for i in ids]
    asym=[g['phi'] for g in gl if g['name'] not in SYM and g['name']!='9']
    if asym: ang=cmean(asym)
    elif ref is not None: ang=ref
    else:
        ang=cmean([2*g['phi'] for g in gl])/2  # mod 180
    u=np.array([math.cos(ang),math.sin(ang)])
    gl2=sorted(gl,key=lambda g:np.array(g['center'])@u)
    chars=[]
    txt=''
    for g in gl2:
        cl=[]
        for (nm,sc,ph) in g['cands']:
            if sc<g['score']-0.10: continue
            if nm=='9': cl.append(('9' if abs(wrap(ph-ang))<math.pi/2 else '6',sc)); cl.append(('6' if abs(wrap(ph-ang))<math.pi/2 else '9',sc-0.06))
            else: cl.append((nm,sc))
        chars.append(cl)

        c=g['name']
        if c=='9': c='9' if abs(wrap(g['phi']-ang))<math.pi/2 else '6'
        txt+=c
    cen=np.mean([g['center'] for g in gl],0)
    return txt,ang,cen,float(np.mean([g['m'] for g in gl])),len(gl),chars
