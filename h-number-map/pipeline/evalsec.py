import pickle, numpy as np, collections, math
from assemble import wrap
from assign import *
PLAN={0:{1:'A'},1:{1:'B'},2:{1:'C'},3:{1:'D'},4:{1:'H',2:'E'},5:{1:'G',2:'F'},6:{3:'K',4:'J',7:'I'},7:{1:'L',3:'L'},8:{1:'M'}}
import itertools
def chars_for(gls,ang):
    u=np.array([math.cos(ang),math.sin(ang)])
    gl2=sorted(gls,key=lambda g:np.array(g['center'])@u)
    out=[]
    for g in gl2:
        cl=[]
        for (nm,sc,ph) in g['cands']:
            if sc<g['score']-0.10: continue
            if nm=='9':
                same=abs(wrap(ph-ang))<math.pi/2
                cl.append(('9' if same else '6',sc)); cl.append(('6' if same else '9',sc-0.06))
            else: cl.append((nm,sc))
            if nm=='1': cl.append(('I',sc-0.08))
        out.append(cl)
    return out
def decode_cands(sec,l):
    h,f=dec.h_lot(sec,l['txt'])
    if h is not None: return h,f,l['txt']
    import re
    mm=re.match(r'^([A-Z]+)(\d+)$',l['txt'])
    if mm:
        t=mm.group(2)+mm.group(1); h,f=dec.h_lot(sec,t)
        if h is not None: return h,f,t
    best=None
    for flip,pen in ((0,0.0),(math.pi,0.05)):
        ch=chars_for(l['gls'],l['ang']+flip)
        if not ch or len(ch)>7: continue
        # two-line labels: allow letters after digits regardless of read order
        for combo in itertools.product(*[c[:3] for c in ch]):
            t=''.join(x[0] for x in combo); sc=sum(x[1] for x in combo)-pen
            h,f=dec.h_lot(sec,t)
            if h is None:
                import re
                mm=re.match(r'^([A-Z]+)(\d+)$',t)
                if mm: t=mm.group(2)+mm.group(1); h,f=dec.h_lot(sec,t)
            if h is not None and (best is None or sc>best[0]): best=(sc,h,f,t)
    if best: return best[1],best[2],best[3]
    return None,None,None
def try_drop(sec,l,found):
    """second chance for undecodable strings: drop one glyph (stray bar/junk) and retry, only for lots not yet found"""
    best=None
    for flip,pen in ((0,0.0),(math.pi,0.05)):
        ch=chars_for(l['gls'],l['ang']+flip)
        if not ch or len(ch)>8 or len(ch)<2: continue
        for drop in range(len(ch)):
            cc=ch[:drop]+ch[drop+1:]
            for combo in itertools.product(*[c[:2] for c in cc]):
                t=''.join(x[0] for x in combo); sc=sum(x[1] for x in combo)-pen-0.15
                cands=[t]
                import re
                mm=re.match(r'^([A-Z]+)(\d+)$',t)
                if mm: cands.append(mm.group(2)+mm.group(1))
                for tt in cands:
                    h,f=dec.h_lot(sec,tt)
                    if h is not None and (sec,tt) not in found and (best is None or sc>best[0]): best=(sc,h,f,tt)
    return best
def collect():
    recs=[]; bad=collections.defaultdict(list)
    for pi in range(9):
        lab,info=regions(pi)
        for l in labs[pi]:
            x,y=l['cen']; xi,yi=int(round(x)),int(round(y))
            if not(0<=yi<lab.shape[0] and 0<=xi<lab.shape[1]): continue
            r=lab[yi,xi]
            if r==0 or r not in PLAN[pi]: continue
            sec=PLAN[pi][r]
            h,f,txt=decode_cands(sec,l)
            gl=[(g['center'][0],g['center'][1],g['m']) for g in l['gls']]
            if h is None: bad[(pi,sec)].append(l)
            else: recs.append(dict(page=pi,sec=sec,txt=txt,h=h,cen=l['cen'],ang=l['ang'],m=l['m'],gl=gl))
    found={(r['sec'],r['txt']) for r in recs}
    for (pi,sec),ls in list(bad.items()):
        keep=[]
        for l in ls:
            b=try_drop(sec,l,found)
            if b and len(l['gls'])>=2:
                sc,h,f,tt=b; found.add((sec,tt))
                recs.append(dict(page=pi,sec=sec,txt=tt,h=h,cen=l['cen'],ang=l['ang'],m=l['m'],gl=[(g['center'][0],g['center'][1],g['m']) for g in l['gls']]))
            else: keep.append(l)
        bad[(pi,sec)]=keep
    return recs,bad
if __name__=="__main__":
    recs,bad=collect()
    cnt=collections.Counter(r['sec'] for r in recs)
    uniq=collections.defaultdict(set)
    for r in recs: uniq[r['sec']].add(r['h'])
    for s in 'ABCDEFGHIJKLM':
        exp=len(dec.full_table(s)); print(s,'ok',cnt[s],'unique H',len(uniq[s]),'expected',exp,'bad',sum(len(v) for k,v in bad.items() if k[1]==s))
    pickle.dump((recs,dict(bad)),open('recs.pkl','wb'))
