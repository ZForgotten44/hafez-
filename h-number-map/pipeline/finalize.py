import pickle, numpy as np, math, collections, json
from evalsec import *
from scipy.spatial import cKDTree
def dedupe(recs):
    by=collections.defaultdict(list)
    for r in recs: by[(r['sec'],r['h'],r['txt'])].append(r)
    uniq={k:v[0] for k,v in by.items() if len(v)==1}
    out=list(uniq.values())
    # neighbour-H consistency for duplicates
    for (sec,h,txt),cands in by.items():
        if len(cands)==1: continue
        pool=[r for r in uniq.values() if r['sec']==sec and r['page']==cands[0]['page']]
        if not pool: out.append(cands[0]); continue
        tr=cKDTree([p['cen'] for p in pool]); best=None
        for c in cands:
            _,idx=tr.query(c['cen'],k=min(6,len(pool))); idx=np.atleast_1d(idx)
            hs=[pool[i]['h'] for i in idx]; med=np.median(hs); score=abs(h-med)
            if best is None or score<best[0]: best=(score,c)
        out.append(best[1])
    return out
if __name__=="__main__":
    recs,bad=collect()
    recs=dedupe(recs)
    REG=pickle.load(open('reg.pkl','rb'))
    AFF=pickle.load(open('aff.pkl','rb'))
    for r in recs:
        r['f']=dec.h_lot(r['sec'],r['txt'])[1]
        A=AFF[r['page']]; s=A[0,0]
        tf=lambda x,y:(A[0,0]*x+A[0,1]*y+A[0,2],A[1,0]*x+A[1,1]*y+A[1,2])
        r['ocen']=tf(*r['cen']); r['om']=r['m']*s; r['glo']=[(*tf(x,y),m*s) for x,y,m in r['gl']]
    pickle.dump((recs,bad),open('final.pkl','wb'))
    cnt=collections.Counter(r['sec'] for r in recs)
    tot=0
    for s in 'ABCDEFGHIJKLM':
        exp=len(dec.full_table(s)); print(s,cnt[s],'/',exp); tot+=cnt[s]
    print('total',tot,'/ 3147')
