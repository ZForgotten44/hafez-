import numpy as np, fitz
from glyphs import *
def dense(g,step=0.08):
    P=[]
    for s in g['segs']:
        if len(s)==2:
            a=np.array(s[0]);b=np.array(s[1]); L=np.linalg.norm(b-a); k=max(2,int(L/step)+1)
            P.append(a+(b-a)*np.linspace(0,1,k)[:,None])
        else:
            p0,p1,p2,p3=[np.array(q) for q in s]
            L=np.linalg.norm(p1-p0)+np.linalg.norm(p2-p1)+np.linalg.norm(p3-p2); k=max(6,int(L/step)+1); t=np.linspace(0,1,k)[:,None]
            P.append((1-t)**3*p0+3*(1-t)**2*t*p1+3*(1-t)*t**2*p2+t**3*p3)
    return np.vstack(P)
def signature(P):
    c=P.mean(0); r=np.linalg.norm(P-c,axis=1); rms=np.sqrt((r**2).mean())
    q=np.quantile(r/rms,np.linspace(0.02,0.98,16))
    # second moments
    Q=(P-c)/rms; cov=np.cov(Q.T); ev=np.linalg.eigvalsh(cov)
    L=sum(np.linalg.norm(np.array(s[-1])-np.array(s[0])) for s in [[(0,0),(0,0)]])
    return np.concatenate([q,ev,[len(P)*0.08/rms/4]])  # rough length ratio

from PIL import Image, ImageDraw
def render(g,size=64,rot=0.0):
    P=dense(g,0.05)
    c=P.mean(0); ca,sa=np.cos(rot),np.sin(rot)
    Q=(P-c)@np.array([[ca,-sa],[sa,ca]]).T
    s=(size*0.42)/max(np.abs(Q).max(),1e-6)
    im=Image.new("L",(size,size),255); dr=ImageDraw.Draw(im)
    for x,y in Q*s+size/2: dr.ellipse([x-1.3,y-1.3,x+1.3,y+1.3],fill=0)
    return im
