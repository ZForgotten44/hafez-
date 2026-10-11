import fitz, pickle, numpy as np, math, collections, json, importlib.util, sys
from assemble import *
from assemble2 import build_glyphs2
from region import region_mask
spec=importlib.util.spec_from_file_location("dec","/Users/mansyhafez/Desktop/hafez#/s4/s4decoder1.py"); dec=importlib.util.module_from_spec(spec); spec.loader.exec_module(dec)
PDFP=PDF; T=Templates(); d=fitz.open(PDFP); REG=pickle.load(open('reg.pkl','rb'))
LETTERS={'H','A','B','C'}
def page_labels(page):
    gl=build_glyphs2(page)
    comps=strings_from(gl)
    L=[]
    for c in comps:
        txt,ang,cen,m,n,chars=resolve(gl,c)
        L.append(dict(txt=txt,ang=ang,cen=cen,m=m,n=n,chars=chars,ids=c,gls=[gl[i] for i in c],sym=all((gl[i]['name'] in SYM or gl[i]['name']=='9') for i in c)))
    # fix all-symmetric strings using nearest asymmetric neighbor angle
    good=[l for l in L if not l['sym']]
    if good:
        from scipy.spatial import cKDTree
        tr=cKDTree([g['cen'] for g in good])
        for l in L:
            if l['sym']:
                _,j=tr.query(l['cen']); ref=good[j]['ang']
                t,a,c,m,n,ch=resolve(gl,l['ids'],ref=ref); l.update(txt=t,ang=a,chars=ch)
    # attach letter-only strings as 2nd line
    digs=[l for l in L if any(ch.isdigit() for ch in l['txt'])]
    used=set()
    for l in L:
        if l['txt'] and all(ch in LETTERS for ch in l['txt']) and l['n']<=3:
            u=np.array([math.cos(l['ang']),math.sin(l['ang'])]); nn=np.array([u[1],-u[0]])
            best=None
            for k,s in enumerate(digs):
                dd=np.array(l['cen'])-np.array(s['cen'])
                if abs(s['ang']-l['ang'])>0.5 and abs(abs(s['ang']-l['ang'])-2*math.pi)>0.5 and abs(abs(s['ang']-l['ang'])-math.pi)>0.5: pass
                su=np.array([math.cos(s['ang']),math.sin(s['ang'])]); sn=np.array([su[1],-su[0]])
                al,pe=dd@su,dd@sn
                if -2.4*s['m']<=pe<=-0.3*s['m'] and abs(al)<=(s['n']*0.75*s['m'])/2+0.9*s['m']:
                    score=abs(al)+abs(pe)
                    if best is None or score<best[0]: best=(score,k)
            if best:
                s=digs[best[1]]; s['txt']=s['txt']+l['txt']; s['n']+=l['n']; s['chars']=s['chars']+l['chars']; s['gls']=s['gls']+l['gls']; used.add(id(l))
    L=[l for l in L if id(l) not in used]
    # drop implausible strings: all-'1' runs >3, and short strings whose angle disagrees with neighbours
    L=[l for l in L if not (len(set(l['txt']))==1 and l['txt'][0]=='1' and len(l['txt'])>3)]
    big=[l for l in L if l['n']>=3]
    if big:
        from scipy.spatial import cKDTree
        tr=cKDTree([l['cen'] for l in big]); keep=[]
        for l in L:
            if l['n']>=3: keep.append(l); continue
            _,idx=tr.query(l['cen'],k=min(6,len(big)))
            idx=np.atleast_1d(idx); a=2*np.array([big[i]['ang'] for i in idx]); ref=np.angle(np.exp(1j*a).mean())/2
            dev=abs((l['ang']-ref+math.pi/2)%math.pi-math.pi/2)
            if dev<=math.radians(25): keep.append(l)
        L=keep
    return L,gl
if __name__=="__main__":
    out={}
    for pi in range(9):
        L,gl=page_labels(d[pi]); out[pi]=L; print(pi,len(gl),len(L))
    pickle.dump(out,open('labels_all.pkl','wb'))
