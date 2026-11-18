import bpy, numpy as np, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; S=bpy.data.objects['Context_skirt_3DEP_ortho_4km']
print('TMODS',[(m.name,m.type,m.show_viewport,m.show_render) for m in T.modifiers])
print('SMODS',[(m.name,m.type,m.show_viewport,m.show_render) for m in S.modifiers])
bt=BVHTree.FromObject(T,dg); bs=BVHTree.FromObject(S,dg)
xs=np.arange(200.25,252,0.5); ys=np.arange(150.25,252,0.5)
zt=np.full((len(ys),len(xs)),np.nan); zs=zt.copy()
for j,y in enumerate(ys):
  for i,x in enumerate(xs):
    h=bt.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))
    if h[0] is not None: zt[j,i]=h[0].z
    h=bs.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))
    if h[0] is not None: zs[j,i]=h[0].z
np.savez('data/qj/probe.npz',xs=xs,ys=ys,zt=zt,zs=zs)
hole=np.isnan(zt)&np.isnan(zs); print('HOLES05',int(hole.sum()))
# terrain extent per row
for j in range(0,len(ys),8):
  r=~np.isnan(zt[j]); 
  print('y%.1f'%ys[j],'tx max',xs[r].max() if r.any() else None,'holes',[float(x) for x in xs[hole[j]]][:6], 'zt@edge',np.round(zt[j][r][-3:],2) if r.any() else None,'zs next', np.round(zs[j][~r][:3],2) if (~r).any() else None)
