import bpy
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=T.data
bb=[v.co for v in me.vertices]; print('TI bbox',min(v.x for v in bb),max(v.x for v in bb),min(v.y for v in bb),max(v.y for v in bb))
from mathutils import Vector
ok,loc,n,i=T.ray_cast(Vector((128,172,400)),Vector((0,0,-1)))
p=me.polygons[i]; print('TI face',i,[tuple(round(c,2) for c in me.vertices[k].co) for k in p.vertices], tuple(round(c,3) for c in p.normal), p.use_smooth)
print('TI mats',[m.name for m in me.materials])
for o in bpy.context.scene.objects:
    if 'grass' in o.name.lower() or 'lawn' in o.name.lower():
        bbw=[o.matrix_world@Vector(c) for c in o.bound_box]
        if min(v.x for v in bbw)<135 and max(v.x for v in bbw)>122 and min(v.y for v in bbw)<185 and max(v.y for v in bbw)>160: print('TI grassobj',o.name,o.type,[m.name for m in o.modifiers])
