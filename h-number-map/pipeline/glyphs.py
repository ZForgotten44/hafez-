import fitz, numpy as np, math
PDF="/Users/mansyhafez/Downloads/Cemetery Map - All Sections on Individual Pages (1).pdf"
def get_dr(page):
    M=page.rotation_matrix
    out=[]
    for x in page.get_drawings():
        if page.rotation:
            items=[]
            for it in x['items']:
                if it[0]=='re': items.append(('re',fitz.Rect(it[1])*M))
                elif it[0]=='qu': items.append(('qu',it[1]*M))
                else: items.append((it[0],)+tuple(p*M for p in it[1:] if isinstance(p,fitz.Point)))
            x=dict(x); x['items']=items; x['rect']=fitz.Rect(x['rect'])*M
        out.append(x)
    return out
def stroke_pts(x):
    pts=[]
    for it in x['items']:
        if it[0]=='l': pts += [(it[1].x,it[1].y),(it[2].x,it[2].y)]
        elif it[0]=='c': pts += [(it[1].x,it[1].y),(it[2].x,it[2].y),(it[3].x,it[3].y),(it[4].x,it[4].y)]
        elif it[0]=='re': r=it[1]; pts += [(r.x0,r.y0),(r.x1,r.y1)]
    return pts
def segs(x):
    out=[]
    for it in x['items']:
        if it[0]=='l': out.append([(it[1].x,it[1].y),(it[2].x,it[2].y)])
        elif it[0]=='c': out.append([(it[1].x,it[1].y),(it[2].x,it[2].y),(it[3].x,it[3].y),(it[4].x,it[4].y)])
    return out
def groups(page, maxdim=7.5):
    dr=[x for x in get_dr(page) if x['type']=='s' and max(x['rect'].width,x['rect'].height)<=maxdim and x['color'] is not None and sum(x['color'])<0.3]
    n=len(dr); par=list(range(n))
    def f(a):
        while par[a]!=a: par[a]=par[par[a]]; a=par[a]
        return a
    rects=[fitz.Rect(x['rect'])+(-0.25,-0.25,0.25,0.25) for x in dr]
    def _cross(p1,p2,p3,p4):
        d1=(p2[0]-p1[0])*(p3[1]-p1[1])-(p2[1]-p1[1])*(p3[0]-p1[0]); d2=(p2[0]-p1[0])*(p4[1]-p1[1])-(p2[1]-p1[1])*(p4[0]-p1[0])
        d3=(p4[0]-p3[0])*(p1[1]-p3[1])-(p4[1]-p3[1])*(p1[0]-p3[0]); d4=(p4[0]-p3[0])*(p2[1]-p3[1])-(p4[1]-p3[1])*(p2[0]-p3[0])
        return d1*d2<0 and d3*d4<0
    def touch(i,j):
        A=segs(dr[i]); B=segs(dr[j])
        for sa in A:
            for sb in B:
                for k in range(len(sa)-1 if len(sa)>2 else 1):
                    p1,p2=sa[k],sa[k+1] if len(sa)>2 else sa[1]
                    for m in range(len(sb)-1 if len(sb)>2 else 1):
                        p3,p4=sb[m],sb[m+1] if len(sb)>2 else sb[1]
                        if _cross(p1,p2,p3,p4): return True
                        for pt,(q1,q2) in ((p1,(p3,p4)),(p2,(p3,p4)),(p3,(p1,p2)),(p4,(p1,p2))):
                            v=np.array(q2)-np.array(q1); L2=v@v+1e-12
                            u=np.clip((np.array(pt)-np.array(q1))@v/L2,0,1)
                            if np.linalg.norm(np.array(q1)+u*v-np.array(pt))<0.22: return True
        return False
    order=sorted(range(n),key=lambda i:rects[i].x0)
    active=[]
    for i in order:
        active=[j for j in active if rects[j].x1>=rects[i].x0]
        for j in active:
            if rects[i].intersects(rects[j]) and f(i)!=f(j) and touch(i,j): par[f(i)]=f(j)
        active.append(i)
    g={}
    for i in range(n): g.setdefault(f(i),[]).append(i)
    res=[]
    for ids in g.values():
        S=[]; 
        for i in ids: S+=segs(dr[i])
        r=fitz.Rect(dr[ids[0]]['rect'])
        for i in ids[1:]: r|=dr[i]['rect']
        res.append(dict(segs=S,rect=r,n=len(ids),parts=[segs(dr[i]) for i in ids]))
    return res
if __name__=="__main__":
    d=fitz.open(PDF); import collections
    gs=groups(d[0]); print(len(gs))
    print(collections.Counter(g['n'] for g in gs))
    print(np.histogram([max(g['rect'].width,g['rect'].height) for g in gs],bins=[0,1,2,3,4,5,6,7,8,10,20])[0])
