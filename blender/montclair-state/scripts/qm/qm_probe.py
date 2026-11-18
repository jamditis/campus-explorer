import bpy, bmesh, numpy as np
from mathutils.bvhtree import BVHTree
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get()
R=bpy.data.objects['Center for Computing and Information Science roof (LiDAR)']
print('roof mods',[m.name for m in R.modifiers], 'mat', R.matrix_world.translation)
ccis=[o for o in bpy.data.objects if o.type=='MESH' and ('CCIS' in o.name or 'Computing' in o.name) and not o.hide_render]
for o in ccis: print('OBJ',o.name, len(o.data.polygons), [m.name for m in o.modifiers][:6])
def bvh(o):
    e=o.evaluated_get(dg); me=e.to_mesh(); mw=o.matrix_world
    bm=bmesh.new(); bm.from_mesh(me); bm.transform(mw); t=BVHTree.FromBMesh(bm); e.to_mesh_clear(); return t,bm
rt,rbm=bvh(R)
others=[(o.name,)+bvh(o) for o in ccis if o!=R]
steep=[f for f in rbm.faces if abs(f.normal.z)<0.85]
print('roof faces',len(rbm.faces),'steep',len(steep))
import collections
cnt=collections.Counter(); behind=collections.Counter(); area=collections.Counter()
for f in steep:
    c=f.calc_center_median(); n=f.normal.copy(); n.z=0
    if n.length<1e-6: continue
    n.normalize()
    key=(round(c.x/10)*10,round(c.y/10)*10)
    cnt[key]+=1; area[key]+=f.calc_area()
    hit=None
    for nm,t,bm in others:
        for d in (-n, n):
            r=t.ray_cast(c+d*0.01,d,3.0)
            if r[0] is not None and (hit is None or r[3]<hit[1]): hit=(nm,r[3])
    if hit: behind[(key,hit[0][:40])]+=1
zs=[f.calc_center_median().z for f in steep]
print('steep z range',min(zs),max(zs))
for k in sorted(cnt): print('cell',k,cnt[k],round(area[k],1))
for k,v in sorted(behind.items(),key=lambda x:-x[1])[:40]: print('behind',k,v)
