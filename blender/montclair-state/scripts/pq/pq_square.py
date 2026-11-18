# pq: square off short diagonal chamfers in the po tier outlines (building axes); output data/pq/polys_sq.json (then po_nest -> data/pq/polys.json)
import json, math, numpy as np, sys
D=json.load(open('data/po/polys.json')); th=D['th']; c,s=math.cos(th),math.sin(th)
MAXL=float(sys.argv[1]) if len(sys.argv)>1 else 4.0
def toL(p): return (c*p[0]+s*p[1], -s*p[0]+c*p[1])
def toW(q): return [c*q[0]-s*q[1], s*q[0]+c*q[1]]
def diag(a,b):
    ang=math.degrees(math.atan2(b[1]-a[1],b[0]-a[0]))%90
    return 15<ang<75
def inter(p1,p2,p3,p4):
    x1,y1=p1;x2,y2=p2;x3,y3=p3;x4,y4=p4
    d=(x1-x2)*(y3-y4)-(y1-y2)*(x3-x4)
    if abs(d)<1e-9: return None
    t=((x1-x3)*(y3-y4)-(y1-y3)*(x3-x4))/d
    return (x1+t*(x2-x1), y1+t*(y2-y1))
NS=[0]
def square(ring):
    P=[toL(p) for p in ring]; changed=True
    while changed and len(P)>4:
        changed=False; n=len(P)
        for i in range(n):
            a,b=P[i],P[(i+1)%n]; L=math.hypot(b[0]-a[0],b[1]-a[1])
            if L>MAXL or not diag(a,b): continue
            p0=P[(i-1)%n]; p3=P[(i+2)%n]
            if diag(p0,a) or diag(b,p3): continue
            q=inter(p0,a,b,p3)
            if q is None or math.hypot(q[0]-a[0],q[1]-a[1])>MAXL: continue
            P[i]=q; del P[(i+1)%n]; NS[0]+=1; changed=True; break
    return [toW(q) for q in P]
for t in D['tiers']:
    t['ext']=square(t['ext']); t['holes']=[square(h) for h in t['holes']]
json.dump(D,open('data/pq/polys_sq.json','w')); print('SQUARED',NS[0])
