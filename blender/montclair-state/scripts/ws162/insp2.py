import bpy, numpy as np
o=bpy.data.objects['Context_skirt_3DEP_ortho_4km']
for m in o.modifiers: print('MOD',m.name,getattr(m,'node_group',None) and m.node_group.name,m.show_viewport,m.show_render)
dg=bpy.context.evaluated_depsgraph_get(); e=o.evaluated_get(dg); me=e.to_mesh(); n=len(me.vertices); co=np.empty(n*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
m=(co[:,0]>-309)&(co[:,0]<-285)&(co[:,1]>-238)&(co[:,1]<-170); print('EVAL verts in box',m.sum(),'z',co[m,2].min() if m.any() else None,co[m,2].max() if m.any() else None)
from mathutils.bvhtree import BVHTree
from mathutils import Vector
lot=[x for x in bpy.data.objects if x.name.startswith('WS162_Lot3_asphalt')][0]
T=BVHTree.FromPolygons([v.co for v in lot.data.vertices],[p.vertices for p in lot.data.polygons])
bt=BVHTree.FromPolygons([Vector(c) for c in co],[p.vertices for p in me.polygons])
worst=[]
for x in np.arange(-307,-286,2.0):
  for y in np.arange(-234,-172,3.0):
    a=T.ray_cast(Vector((x,y,200)),Vector((0,0,-1))); b=bt.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))
    if a[0] is not None: worst.append((round(b[0].z-a[0].z,2) if b[0] else None,round(x,1),round(y,1)))
print('DIFF terrain-lot',[w for w in worst if w[0] is None or w[0]>-0.03][:30],len(worst))
print('mods all',[ (x.name) for x in bpy.data.objects if x.type=='MESH' and x.name.startswith(('Terrain','WS110','WS113','WS114'))][:20])
