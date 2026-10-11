import numpy as np, math, multiprocessing as mp
from recog import *
from feat import dense
_T=None
def _init():
    global _T; _T=Templates()
def rec_old(segs,depth=0):
    r=classify(dict(segs=segs),_T,coarse=12)
    if r and r['score']>=0.90: return [(r,segs)]
    if len(segs)>=8 and depth<3:
        best=None
        for k in range(3,len(segs)-2):
            a=classify(dict(segs=segs[:k]),_T,coarse=20); b=classify(dict(segs=segs[k:]),_T,coarse=20)
            if a and b:
                sc=min(a['score'],b['score'])
                if best is None or sc>best[0]: best=(sc,k)
        if best and best[0]>=0.86 and (not r or best[0]>r['score']+0.03):
            k=best[1]; return rec_old(segs[:k],depth+1)+rec_old(segs[k:],depth+1)
    return [(r,segs)] if r and r['score']>=0.72 else []
def rec(segs,depth=0):
    o=rec_old(segs)
    if o and all(x[0]['score']>=0.88 for x in o): return o
    nw=rec_new(segs)
    mo=min([x[0]['score'] for x in o],default=0); mn=min([x[0]['score'] for x in nw],default=0)
    return nw if (mn>mo+0.02 and nw) else o
def rec_new(segs,depth=0):
    r=classify(dict(segs=segs),_T,coarse=12)
    if r and r['score']>=0.93: return [(r,segs)]
    memo={}
    def cls(i,j):
        if (i,j) not in memo:
            rr=classify(dict(segs=segs[i:j]),_T,coarse=20) if j-i>=2 else None
            memo[(i,j)]=rr
        return memo[(i,j)]
    n=len(segs)
    def best_from(i,d):
        # segment segs[i:] into glyphs; returns (minscore, ngl, [(i,j,r)...]) or None
        whole=cls(i,n)
        opts=[]
        if whole and whole['score']>=0.88: opts.append((whole['score'],1,[(i,n,whole)]))
        if d<7:
            for k in range(i+2,n-1):
                a=cls(i,k)
                if a is None or a['score']<0.90: continue
                rest=best_from(k,d+1)
                if rest: opts.append((min(a['score'],rest[0]),1+rest[1],[(i,k,a)]+rest[2]))
        if not opts: return None
        return max(opts,key=lambda o:(round(o[0],2),-o[1]))
    if n>=5:
        res=best_from(0,0)
        if res and res[0]>=0.90 and (not r or r['score']<0.88):
            out=[]
            for i,j,rr in res[2]:
                rr2=classify(dict(segs=segs[i:j]),_T,coarse=12); out.append((rr2 or rr,segs[i:j]))
            return out
    return [(r,segs)] if r and r['score']>=0.72 else []
def work(g):
    m=max(g['rect'].width,g['rect'].height)
    if not (1.3<=m<=12): return []
    out=[]
    for r,segs in rec(g['segs']):
        P=np.vstack([np.array(s) for s in segs]); w=P.max(0)-P.min(0)
        if r['name']=='1' and len(segs)<2: continue
        r=dict(r); r['name']=r['name'].split('#')[0]; r['cands']=[c for c in r['cands']]; r['m']=float(max(w)); r['center']=tuple(P.mean(0)); r['nseg']=len(segs); out.append(r)
    return out
def build_glyphs2(page,procs=6):
    gs=[g for g in groups(page) if g['segs']]
    gs=[dict(segs=g['segs'],rect=g['rect']) for g in gs]
    with mp.get_context('fork').Pool(procs,initializer=_init) as p: res=p.map(work,gs,chunksize=20)
    return [r for rr in res for r in rr]
