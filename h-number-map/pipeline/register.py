import numpy as np, fitz, math, collections
from glyphs import get_dr
def long_segments(page,minlen):
    out=[]
    for x in get_dr(page):
        if x['type']!='s' or not x['color'] or sum(x['color'])>0.3: continue
        for it in x['items']:
            if it[0]!='l': continue
            a=np.array([it[1].x,it[1].y]); b=np.array([it[2].x,it[2].y]); L=np.linalg.norm(b-a)
            if L>=minlen: out.append((a[0],a[1],b[0],b[1]))
    return np.array(out)
def prep(S):
    a=S[:,:2]; b=S[:,2:]; v=b-a; L=np.linalg.norm(v,axis=1); ang=np.arctan2(v[:,1],v[:,0])%math.pi
    return dict(a=a,b=b,L=L,ang=ang,m=(a+b)/2)
def vote(P,O,maxp=400,seed=0):
    rng=np.random.default_rng(seed)
    idx=rng.permutation(len(P['L']))[:maxp]
    votes=collections.Counter()
    for i in idx:
        d=np.abs(O['ang']-P['ang'][i]); d=np.minimum(d,math.pi-d)
        j=np.where(d<math.radians(0.6))[0]
        s=O['L'][j]/P['L'][i]
        k=(s>0.15)&(s<0.9); j=j[k]; s=s[k]
        t=O['m'][j]-s[:,None]*P['m'][i]
        key=np.stack([np.round(np.log(s)/0.012),np.round(t[:,0]/1.2),np.round(t[:,1]/1.2)],1).astype(int)
        for kk in map(tuple,key): votes[kk]+=1
    return votes
def refine(P,O,s,t,iters=4):
    from scipy.spatial import cKDTree
    tr=cKDTree(O['m'])
    for it in range(iters):
        Pm=P['m']*s+t
        dd,jj=tr.query(Pm,distance_upper_bound=2.0)
        ok=np.isfinite(dd)&(np.abs(P['L']*s-O['L'][np.minimum(jj,len(O['L'])-1)])<0.15*P['L']*s+0.3)
        if ok.sum()<20: break
        X=P['m'][ok]; Y=O['m'][jj[ok]]
        A=np.column_stack([X.ravel()*0+1,X.ravel()]) # solve s,tx,ty jointly
        n=len(X); M=np.zeros((2*n,3)); rhs=np.zeros(2*n)
        M[0::2,0]=X[:,0]; M[0::2,1]=1; M[1::2,0]=X[:,1]; M[1::2,2]=1
        rhs[0::2]=Y[:,0]; rhs[1::2]=Y[:,1]
        sol,*_=np.linalg.lstsq(M,rhs,rcond=None); s,tx,ty=sol; t=np.array([tx,ty])
    return s,t,int(ok.sum())
def register(page,overall,seed=0):
    P=prep(long_segments(page,6)); O=prep(long_segments(overall,1.5))
    v=vote(P,O,seed=seed)
    (ks,kx,ky),c=v.most_common(1)[0]
    s=math.exp(ks*0.012); t=np.array([kx*1.2,ky*1.2])
    s,t,n=refine(P,O,s,t)
    return s,t,n,c,v.most_common(3)
