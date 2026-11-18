import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from collections import Counter
exec(open('scripts/we/we_probe2.py').read().split("V,P,N=mesh(O['QS_footway_313027436")[0])
for wn in ['QS_footway_313027436_UNVERIFIED','QS_footway_313027428_UNVERIFIED','QS_footway_313027430_UNVERIFIED','QS_footway_313027432_UNVERIFIED','QS_footway_313027437_UNVERIFIED','QS_footway_546643369_UNVERIFIED','QS_footway_313027435_UNVERIFIED','QS_footway_313027429_UNVERIFIED']:
    V,P,N=mesh(O[wn]); ec=Counter()
    for p,q in zip(P,N):
        if q.z<0.5: continue
        for i in range(len(p)): ec[tuple(sorted((p[i],p[(i+1)%len(p)])))]+=1
    ex=[];hot=[]
    for (a,b),c in ec.items():
        if c!=1: continue
        A,B=V[a],V[b]; n=max(1,int((B-A).length/0.25))
        for k in range(n+1):
            p=A+(B-A)*(k/n)
            for ang in np.linspace(0,2*np.pi,16,endpoint=False):
                x=p.x+0.3*np.cos(ang); y=p.y+0.3*np.sin(ang)
                if top(SL,x,y) is not None: continue
                g=top(G,x,y)
                if g is None: break
                e=p.z-g[0]; ex.append(e)
                if e>0.07: hot.append((round(p.x),round(p.y),round(e,2)))
                break
    ex=np.array(ex); cl=Counter((h[0]//2*2,h[1]//2*2) for h in hot)
    print('EXP',wn[11:20],len(ex),'p50 %.3f p90 %.3f max %.3f'%(np.median(ex),np.percentile(ex,90),ex.max()),'hot',len(hot),dict(cl),flush=True)
b=O['MO Health Drop-In Center walls+parapet+roof (best-effort; UNVERIFIED)'] if 'MO Health Drop-In Center walls+parapet+roof (best-effort; UNVERIFIED)' in O else [o for o in O if o.name.startswith('MO Health Drop-In')][0]
c=np.array([b.matrix_world@Vector(q) for q in b.bound_box]); print('HEALTH',b.name,c.min(0).round(2),c.max(0).round(2),flush=True)
