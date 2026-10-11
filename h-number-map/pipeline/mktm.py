import pickle, numpy as np, math
from recog import *
gs,X,lab,C=pickle.load(open('cl2.pkl','rb'))
want={0:'8',1:'1',2:'5',3:'9',4:'2',5:'0',7:'H',8:'3',10:'7',11:'A',15:'4',21:'B',26:'C'}
pairs=[]
for k,name in want.items():
    idx=[i for i in range(len(gs)) if lab[i]==k]
    i=min(idx,key=lambda i:np.linalg.norm(X[i]-C[k])); pairs.append((name,gs[i],math.pi/2))
res,rl,rc,RX=pickle.load(open('resid.pkl','rb'))
extra={4:'2',41:'2',3:'0',10:'8'}
for k,name in extra.items():
    idx=[i for i in range(len(res)) if rl[i]==k and res[i]['page']<=3]
    if not idx: continue
    i=min(idx,key=lambda i:np.linalg.norm(RX[i]-rc[k]))
    pairs.append((name+'#'+str(k),res[i]['g'],math.pi/2))
import fitz
from glyphs import groups, PDF
d=fitz.open(PDF)
gs2=[g for g in groups(d[3]) if g['segs'] and 548<=g['rect'].x0+g['rect'].width/2<=568 and 280<=g['rect'].y0<=620]
gs2=sorted(gs2,key=lambda g:-g['rect'].y0)
for idx,name in {7:'D',9:'E',10:'F',13:'G',21:'J',23:'K',25:'L',27:'M',29:'N',33:'P',35:'Q',37:'R',39:'S',41:'T',43:'U'}.items():
    pairs.append((name,gs2[idx],math.pi/2))
make_templates(pairs); print([p[0] for p in pairs])
