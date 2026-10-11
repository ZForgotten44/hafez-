import pickle, numpy as np, collections
from run_all import *
from scipy import ndimage as ndi
labs=pickle.load(open('labels_all.pkl','rb'))
def regions(pi):
    lab,n=region_mask(d[pi],r=5)
    sizes=np.bincount(lab.ravel())[1:]
    ids=[i+1 for i in range(n) if sizes[i]>1500]
    info=[]
    for i in ids:
        ys,xs=np.nonzero(lab==i); info.append((i,xs.mean(),ys.mean(),len(xs)))
    return lab,info
SECMAP={}
def secmap(pi,info):
    if pi in (0,1,2,3,8): return {info[0][0]:'A BCD'[0]} if False else None
if __name__=="__main__":
    for pi in range(9):
        lab,info=regions(pi); print(pi,[(i,round(x),round(y),s) for i,x,y,s in info])
