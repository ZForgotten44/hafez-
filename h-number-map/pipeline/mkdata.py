import pickle, json, math, importlib.util, collections
import numpy as np
from scipy.spatial import cKDTree
spec=importlib.util.spec_from_file_location("dec","/Users/mansyhafez/Desktop/hafez#/s4/s4decoder1.py")
dec=importlib.util.module_from_spec(spec); spec.loader.exec_module(dec)
recs,bad=pickle.load(open('final.pkl','rb'))

# approximate lot length along its own axis (for highlight box) - same heuristic as render.py
C=np.array([r['ocen'] for r in recs]); tr=cKDTree(C)
for i,r in enumerate(recs):
    u=np.array([math.cos(r['ang']),math.sin(r['ang'])]); nvec=np.array([-u[1],u[0]])
    best=None
    for j in tr.query_ball_point(C[i],14):
        if j==i: continue
        d=C[j]-C[i]; al=abs(d@u); pe=abs(d@nvec)
        if al>1.5 and pe<0.35*al+0.8 and (best is None or al<best): best=al
    r['lotlen']=best if best else 6.0

def compact(f):
    return f[1:].lstrip('0')

labels=[]
for r in recs:
    labels.append({
        "s": r['sec'], "l": r['txt'], "h": r['f'], "c": compact(r['f']),
        "x": round(float(r['ocen'][0]),2), "y": round(float(r['ocen'][1]),2),
        "a": round(math.degrees(r['ang']),1), "w": round(float(r['lotlen']),2), "hn": r['h']
    })

placed={(r['sec'],r['txt']) for r in recs}
missing=[]
for s in 'ABCDEFGHIJKLM':
    for row in dec.full_table(s):
        lab=row['lot_label']
        if (s,lab) in placed: continue
        note=""
        if lab.endswith('dr'): note="internal double-row key (map shows A/B rows)"
        elif s=='D' and lab.isdigit() and 367<=int(lab)<=384: note="shared base of a double-row lot (map shows A/B rows)"
        elif s=='E' and lab.isdigit() and 190<=int(lab)<=199: note="shared base of a double-row lot (map shows A/B rows)"
        missing.append({"s":s,"l":lab,"h":row['h_lot'],"note":note})

AFF=pickle.load(open('aff.pkl','rb'))
def tf(pi,x,y):
    A=AFF[pi]
    return A[0,0]*x+A[0,1]*y+A[0,2], A[1,0]*x+A[1,1]*y+A[1,2]

unmatched=[]
for (pi,sec),ls in bad.items():
    for l in ls:
        if len(l['txt'])>=2 and len(l['txt'])<=6 and any(ch.isdigit() for ch in l['txt']):
            ox,oy=tf(pi,l['cen'][0],l['cen'][1])
            unmatched.append({"region":sec,"label":l['txt'],"x":round(float(ox),1),"y":round(float(oy),1)})

stats=[]
for sec in 'ABCDEFGHIJKLM':
    exp=len(dec.full_table(sec)); got=sum(1 for r in recs if r['sec']==sec)
    uniq=len({r['h'] for r in recs if r['sec']==sec})
    stats.append({"s":sec,"placed":got,"expected":exp,"uniqueH":uniq})

json.dump(labels,open('labels.json','w'),separators=(',',':'))
json.dump(missing,open('missing.json','w'),separators=(',',':'))
json.dump(unmatched,open('unmatched.json','w'),separators=(',',':'))
json.dump(stats,open('stats.json','w'),separators=(',',':'))
print(len(labels),len(missing),len(unmatched))
print(sum(s['placed'] for s in stats),'/',sum(s['expected'] for s in stats))
