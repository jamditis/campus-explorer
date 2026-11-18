"""wx fix2: remaining ground-through-footway pokes near Stone west (faces rising between hidden verts). For each poke
sample (0.1 m grid, outside the building, under a slab) lower the hit face's verts that are themselves under a slab or
inside the Stone footprint, by the poke + 1 cm (cap 10 cm per vert), 3 passes. Lawn verts outside slabs never moved."""
import bpy, json, numpy as np, sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R='/workspace/nj-scenes/montclair-state'; O=bpy.data.objects
exec(open(f'{R}/scripts/wx/wx_common.py').read())
pre={n:np.array([v.co[:] for v in O[n].data.vertices]) for n in G}
rep={}
for it in range(3):
    GBs={n:bv(n) for n in G}; GB=dict(GBs); GB['WF']=bv('WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED')
    want={n:{} for n in G}; c=0; mx=0
    for x in np.arange(126,150,0.1):
      for y in np.arange(250,322,0.1):
        if inside(x,y): continue
        s=top(SB,x,y)
        if s is None: continue
        best=None
        for n in G:
            r=GBs[n].ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
            if r[0] is not None and (best is None or r[0].z>best[1]): best=(n,r[0].z,r[2])
        if best is None or best[1]<=s-0.005: continue
        c+=1; mx=max(mx,best[1]-s); n,gz,fi=best; dz=best[1]-s+0.01
        for vi in O[n].data.polygons[fi].vertices:
            w=O[n].matrix_world@O[n].data.vertices[vi].co
            if inside(w.x,w.y) or top(SB,w.x,w.y) is not None:
                want[n][vi]=max(want[n].get(vi,0),dz)
    print('PASS',it,'pokes',c,round(mx,3),flush=True); rep[f'pass{it}']=[c,round(mx,3)]
    if c==0: break
    for n in G:
        me=O[n].data
        for vi,dz in want[n].items():
            cur=me.vertices[vi].co.z; lim=pre[n][vi][2]-0.10
            me.vertices[vi].co.z=max(cur-dz,lim)
        me.update()
    bpy.context.view_layer.update()
GBs={n:bv(n) for n in G}
c=0;mx=0
for x in np.arange(126,150,0.1):
  for y in np.arange(250,322,0.1):
    if inside(x,y): continue
    s=top(SB,x,y)
    if s is None: continue
    g=top(GBs,x,y)
    if g is not None and g>s-0.005: c+=1;mx=max(mx,g-s)
rep['final']=[c,round(mx,3)]; print('FINAL',c,round(mx,3),flush=True)
mv={n:int((np.abs(np.array([v.co[:] for v in O[n].data.vertices])-pre[n]).max(axis=1)>1e-4).sum()) for n in G}; rep['moved']=mv; print('MOVED',mv)
json.dump(rep,open(f'{R}/data/wx/fix2_report.json','w'),indent=1)
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED',len(O),flush=True)
