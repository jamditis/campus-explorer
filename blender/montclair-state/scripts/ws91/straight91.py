# ws91 core: straighten boundary loops of meshes (RDP keypoints + projection + kink smoothing), propagate to interior
import math,collections
def loops_of(F):
    ec=collections.Counter()
    for f in F:
        for i in range(len(f)):
            a,b=f[i],f[(i+1)%len(f)]; ec[(min(a,b),max(a,b))]+=1
    adj=collections.defaultdict(list)
    for (a,b),c in ec.items():
        if c==1: adj[a].append(b); adj[b].append(a)
    seen=set();loops=[]
    for s in list(adj):
        if s in seen or len(adj[s])!=2: continue
        L=[s];seen.add(s);cur=s;ok=True
        while True:
            nx=[x for x in adj[cur] if x not in seen]
            if len(adj[cur])!=2: ok=False
            if not nx: break
            cur=nx[0];seen.add(cur);L.append(cur)
        if ok and len(L)>=4 and s in adj[L[-1]]: loops.append(L)
    return loops
def pdist(p,a,b):
    dx,dy=b[0]-a[0],b[1]-a[1]; L2=dx*dx+dy*dy
    if L2<1e-12: return math.hypot(p[0]-a[0],p[1]-a[1]),0.0
    t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/L2))
    return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy),t
def rdp(P,i0,i1,eps,out):
    best=-1;bi=None
    for i in range(i0+1,i1):
        d,_=pdist(P[i],P[i0],P[i1])
        if d>best: best=d;bi=i
    if bi is not None and best>eps:
        rdp(P,i0,bi,eps,out); rdp(P,bi,i1,eps,out)
    else: out.append(i1)
def straighten_loop(P,eps,clamp,smooth=2):
    n=len(P); cx=sum(p[0] for p in P)/n; cy=sum(p[1] for p in P)/n
    s=max(range(n),key=lambda i:(P[i][0]-cx)**2+(P[i][1]-cy)**2)
    Q=P[s:]+P[:s]+[P[s]]
    m=max(range(len(Q)),key=lambda i:(Q[i][0]-Q[0][0])**2+(Q[i][1]-Q[0][1])**2)
    keys=[0]; rdp(Q,0,m,eps,keys); rdp(Q,m,n,eps,keys)
    keys=sorted(set(keys))
    NQ=[None]*n
    for a,b in zip(keys[:-1],keys[1:]):
        A,B=Q[a],Q[b]; dx,dy=B[0]-A[0],B[1]-A[1]; L2=dx*dx+dy*dy or 1e-12
        for i in range(a,b+1):
            if i==n: continue
            p=Q[i]; t=((p[0]-A[0])*dx+(p[1]-A[1])*dy)/L2; t=max(0,min(1,t))
            NQ[i]=(A[0]+t*dx,A[1]+t*dy)
    # corner angles at keys
    def ang(k):
        a=keys[(keys.index(k)-1)%len(keys)] if k!=0 else keys[-2]; b=keys[(keys.index(k)+1)%len(keys)] if k!=0 else keys[1]
        A,B,C=Q[a%n],Q[k%n],Q[b%n]
        u=(B[0]-A[0],B[1]-A[1]); v=(C[0]-B[0],C[1]-B[1])
        nu=math.hypot(*u) or 1e-9; nv=math.hypot(*v) or 1e-9
        return math.degrees(math.acos(max(-1,min(1,(u[0]*v[0]+u[1]*v[1])/nu/nv))))
    soft=set(k%n for k in keys[:-1] if ang(k)<28)
    if smooth:
        S=list(NQ)
        for k in soft:
            for i in range(k-smooth,k+smooth+1):
                tot=[0,0];w=0
                for j in range(i-smooth,i+smooth+1):
                    g=math.exp(-((i-j)/max(1,smooth*0.7))**2/2); q=NQ[j%n]; tot[0]+=g*q[0]; tot[1]+=g*q[1]; w+=g
                S[i%n]=(tot[0]/w,tot[1]/w)
        NQ=S
    out=[None]*n; disp=[]
    for i in range(n):
        o=Q[i]; q=NQ[i]; d=math.hypot(q[0]-o[0],q[1]-o[1])
        if d>clamp: q=(o[0]+(q[0]-o[0])*clamp/d,o[1]+(q[1]-o[1])*clamp/d); d=clamp
        out[(i+s)%n]=q; disp.append(d)
    return out,len(keys)-1,max(disp) if disp else 0
def wobble(P):
    # mean abs deviation of each vertex from line through its ±3 neighbours (lateral jitter metric)
    n=len(P);t=0
    for i in range(n):
        d,_=pdist(P[i],P[(i-3)%n],P[(i+3)%n]); t+=d
    return t/n
