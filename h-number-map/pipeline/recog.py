import numpy as np, math, pickle, fitz
from scipy.ndimage import gaussian_filter
from feat import dense
from glyphs import groups, PDF
G=36
def norm_pts(P):
    c=P.mean(0); Q=P-c; rms=np.sqrt((Q**2).sum(1).mean()); return Q/rms, c, rms
def splat(Q):  # Q: (A,N,2) -> (A,G,G)
    A,N,_=Q.shape
    sc=G*0.5/2.6
    xy=np.clip(np.round(Q*sc+G/2).astype(int),0,G-1)
    img=np.zeros((A,G,G),np.float32)
    a=np.repeat(np.arange(A),N)
    np.add.at(img,(a,xy[:,:,1].ravel(),xy[:,:,0].ravel()),1.0)
    img=np.stack([gaussian_filter(i,1.15) for i in img])
    v=img.reshape(A,-1); v=v-v.mean(1,keepdims=True); v/= (np.linalg.norm(v,axis=1,keepdims=True)+1e-9)
    return v
def rotm(t): c,s=math.cos(t),math.sin(t); return np.array([[c,-s],[s,c]])
def resample(P,n=90):
    if len(P)<=n: return P
    idx=np.linspace(0,len(P)-1,n).astype(int); return P[idx]
def sparse_dense(g,step=0.06):
    P=dense(g,step); return P
class Templates:
    def __init__(self,path='templates.pkl'):
        self.names,self.V=pickle.load(open(path,'rb'))
        self.bias=np.array([0.07 if n in ('D','E','F','G','J','K','L','M','N','P','Q','R','S','T','U') else 0.0 for n in self.names])
def make_templates(pairs,path='templates.pkl'):
    """pairs: list of (name, group, rot_to_upright) """
    names=[];V=[]
    for name,g,rot in pairs:
        P=dense(g,0.06); Q,_,_=norm_pts(P); Q=Q@rotm(rot).T
        v=splat(resample(Q,200)[None])[0]; names.append(name); V.append(v)
    pickle.dump((names,np.array(V)),open(path,'wb'))
def classify(g,T,coarse=10):
    P=dense(g,0.06)
    if len(P)<8: return None
    Q,c,rms=norm_pts(P); Q=resample(Q,200)
    angs=np.deg2rad(np.arange(0,360,coarse))
    # glyph = template rotated by phi  => unrotate glyph by -phi
    R=np.stack([Q@rotm(-a).T for a in angs])
    v=splat(R); S=v@T.V.T-T.bias  # (A,T)
    a,t=np.unravel_index(S.argmax(),S.shape)
    # refine
    fa=np.deg2rad(np.arange(np.rad2deg(angs[a])-coarse,np.rad2deg(angs[a])+coarse+1,2))
    R=np.stack([Q@rotm(-x).T for x in fa]); v=splat(R); S2=v@T.V.T-T.bias
    a2,t2=np.unravel_index(S2.argmax(),S2.shape)
    # best per template score for ambiguity checks
    best=S2.max(0); bi=S2.argmax(0)
    cd={}
    for j,nm in enumerate(T.names):
        b=nm.split('#')[0]; sc=float(best[j])
        if b not in cd or sc>cd[b][0]: cd[b]=(sc,float(fa[bi[j]]))
    cands=sorted(((b,sc,ph) for b,(sc,ph) in cd.items()),key=lambda t:-t[1])[:4]
    return dict(name=T.names[t2],phi=float(fa[a2]),score=float(S2[a2,t2]),second=float(np.sort(best)[-2]),center=c,rms=rms,cands=cands)
