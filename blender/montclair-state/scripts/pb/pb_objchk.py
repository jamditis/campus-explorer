# list static objects whose origin is in the box and the evaluated terrain dz under them (ray-cast evaluated vs original)
import bpy, numpy as np
from mathutils import Vector
X0,X1,Y0,Y1=80,205,120,262
dg=bpy.context.evaluated_depsgraph_get(); T=bpy.data.objects['Terrain_LiDAR_DTM_1m']
te=T.evaluated_get(dg); me=te.to_mesh()
a=me.attributes['pb_dz']; dz=np.zeros(len(me.vertices)); a.data.foreach_get('value',dz)
co=np.zeros(len(me.vertices)*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
m=np.abs(dz)>1e-4; mc=co[m]; md=dz[m]
print('PBO moved bbox',mc.min(0).round(1),mc.max(0).round(1),'n',m.sum(),'|dz|>0.1:',(np.abs(md)>0.1).sum())
skip=('Terrain','Footpaths_OSM','Roads_OSM','Context_skirt')
for o in bpy.data.objects:
    if o.type not in ('MESH','EMPTY','CURVES') or o.name.startswith(skip): continue
    p=o.matrix_world.translation
    if X0<p.x<X1 and Y0<p.y<Y1 and len(mc):
        d=np.hypot(mc[:,0]-p.x,mc[:,1]-p.y); i=d.argmin()
        if d[i]<3 and abs(md[i])>0.02: print('PBO',o.name[:50],tuple(round(v,1) for v in p),'near dz %.3f'%md[i])
te.to_mesh_clear()
