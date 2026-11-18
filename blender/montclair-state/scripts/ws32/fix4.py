# ws32 fix4 (run on the ws32-saved main): Footpaths_OSM is re-draped onto the terrain by its GN modifiers (OO_redrape_LiDAR),
# so seating terrain under the lowered apron pulled the walk back down flush with the apron (blotches + a dark wedge).
# Terrain is left alone; apron verts under/near the walk are set 2.5 cm under the evaluated walk (walk rides ~4.5 cm over terrain).
import bpy,bmesh,collections
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get(); dg.update(); D=Vector((0,0,-1))
def bvh(n):
    o=bpy.data.objects[n]; e=o.evaluated_get(dg); m=e.to_mesh(); b=bmesh.new(); b.from_mesh(m); b.transform(o.matrix_world); e.to_mesh_clear(); t=BVHTree.FromBMesh(b); b.free(); return t
FP=bvh('Footpaths_OSM'); TB=bvh('Terrain_LiDAR_DTM_1m')
OFF=[(0,0),(0.3,0),(-0.3,0),(0,0.3),(0,-0.3),(0.21,0.21),(-0.21,0.21),(0.21,-0.21),(-0.21,-0.21)]
ap=bpy.data.objects['CCOM_dock_apron_20261014jf3']; mw=ap.matrix_world; mi=mw.inverted(); n=0; lo=[]
for v in ap.data.vertices:
    p=mw@v.co
    zs=[h[0].z for h in (FP.ray_cast(Vector((p.x+dx,p.y+dy,p.z+3)),D,6) for dx,dy in OFF) if h[0] is not None]
    if not zs: continue
    t=min(zs)-0.025
    tz=TB.ray_cast(Vector((p.x,p.y,p.z+3)),D,8); tz=tz[0].z if tz[0] is not None else t-1
    t=max(t,tz+0.008)
    if abs(p.z-t)>0.002: lo.append(round(t-p.z,3)); p.z=t; v.co=mi@p; n+=1
ap.data.update(); print('apron verts set under walk',n,'dz range',min(lo) if lo else 0,max(lo) if lo else 0)
dg.update(); AP=bvh('CCOM_dock_apron_20261014jf3'); h=collections.Counter()
for x10 in range(-10,90,3):
    for y10 in range(-390,-235,3):
        a=AP.ray_cast(Vector((x10/10,y10/10,150)),D,30); f=FP.ray_cast(Vector((x10/10,y10/10,150)),D,30); t=TB.ray_cast(Vector((x10/10,y10/10,150)),D,30)
        if a[0] and f[0]:
            d=f[0].z-a[0].z; h['ok>=1.5cm' if d>=0.015 else ('thin0-1.5' if d>=0 else 'apron_above')]+=1
        if a[0] and t[0] and t[0].z>a[0].z-0.003: h['terrain_pokes_apron']+=1
print('OVERLAP after',dict(h))
