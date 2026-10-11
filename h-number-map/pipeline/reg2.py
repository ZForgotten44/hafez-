import numpy as np, fitz, pickle, math
from scipy.spatial import cKDTree
from register import long_segments, prep
d=fitz.open("/Users/mansyhafez/Downloads/Cemetery Map - All Sections on Individual Pages (1).pdf")
o=fitz.open("/Users/mansyhafez/Downloads/Cemetery - Overall Map (1).pdf")[0]
O=prep(long_segments(o,1.2)); tr=cKDTree(O['m'])
REG=pickle.load(open('reg.pkl','rb'))
AFF={}
for pi in range(9):
    s,t=REG[pi]; P=prep(long_segments(d[pi],5))
    A=np.array([[s,0,t[0]],[0,s,t[1]]])  # x' = A @ [x,y,1]
    for it in range(8):
        X=np.column_stack([P['m'],np.ones(len(P['m']))]); Y=X@A.T
        dd,jj=tr.query(Y,distance_upper_bound=1.2 if it<3 else 0.5)
        ok=np.isfinite(dd)
        # also require similar length & angle
        L2=O['L'][np.minimum(jj,len(O['L'])-1)]
        ang=np.abs(O['ang'][np.minimum(jj,len(O['L'])-1)]-P['ang']); ang=np.minimum(ang,math.pi-ang)
        ok&=(np.abs(L2-P['L']*s)<0.25*P['L']*s+0.5)&(ang<math.radians(2))
        Xo=X[ok]; Yo=O['m'][jj[ok]]
        sol,*_=np.linalg.lstsq(Xo,Yo,rcond=None); A=sol.T
    res=np.linalg.norm(Xo@A.T-Yo,axis=1)
    print(pi,'n',ok.sum(),'rms',round(float(np.sqrt((res**2).mean())),3),'A',np.round(A,4).tolist())
    AFF[pi]=A
pickle.dump(AFF,open('aff.pkl','wb'))
