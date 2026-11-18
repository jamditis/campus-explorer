import bpy, bmesh, numpy as np
from mathutils import Vector
from collections import defaultdict
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; e=t.evaluated_get(dg); me=e.to_mesh()
bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
long=[f for f in bm.faces if max(e_.calc_length() for e_ in f.edges)>6]
print('FE eval long faces',len(long),'area %.0f'%sum(f.calc_area() for f in long))
rng=np.random.default_rng(0); vis=defaultdict(float); tot=defaultdict(float); ex=defaultdict(list)
for f in long:
    vs=[v.co.copy() for v in f.verts]; A=f.calc_area(); n=max(3,min(40,int(A/20)))
    hub=max(f.verts,key=lambda v: sum(1 for g in v.link_faces if max(x.calc_length() for x in g.edges)>6)).index
    hits=0
    for _ in range(n):
        a=rng.random(len(vs)); a/=a.sum(); q=sum((v*w for v,w in zip(vs,a)),Vector())
        h=sc.ray_cast(dg,q+Vector((0,0,80)),Vector((0,0,-1)),distance=80.3)
        if h[0] and h[4].name==t.name and abs(h[1].z-q.z)<0.05: hits+=1
    vis[hub]+=A*hits/n; tot[hub]+=A
    if hits: ex[hub].append(tuple(round(c,1) for c in f.calc_center_median()))
for hb in sorted(tot,key=lambda k:-vis[k])[:15]:
    print('FE hub',hb,'(%.1f,%.1f)'%tuple(bm.verts[hb].co.xy),'area %.0f visible %.0f'%(tot[hb],vis[hb]),'ex',ex[hb][:4])
