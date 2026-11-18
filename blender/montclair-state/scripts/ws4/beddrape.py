import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; print('TMODS',[m.type for m in T.modifiers])
mw=T.matrix_world; vs=[mw@v.co for v in T.data.vertices]
ps=[list(p.vertices) for p in T.data.polygons if -85<(mw@p.center).x<-70 and -58<(mw@p.center).y<-46]
B=BVHTree.FromPolygons(vs,ps)
o=bpy.data.objects['WS4_Planting_bed_mulch_at_Cole_sign_UNVERIFIED']; om=o.matrix_world; inv=om.inverted()
zs=[]
for v in o.data.vertices:
  w=om@v.co; h=B.ray_cast(Vector((w.x,w.y,200)),Vector((0,0,-1)))
  if h[0]: 
    w.z=h[0].z+0.035; v.co=inv@w; zs.append(round(h[0].z,3))
print('TZ',min(zs),max(zs),'old bed z',round((om@o.data.vertices[0].co).z,3))
o.modifiers['skirt'].thickness=0.15
bpy.ops.wm.save_mainfile(); print('SAVED')
