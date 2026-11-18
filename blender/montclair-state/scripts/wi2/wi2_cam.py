import bpy
from mathutils import Vector
c=bpy.data.objects['WE_CAM_closeup_stone_footway_junction_from_SE']
print('CAM',tuple(round(v,2) for v in c.location),tuple(round(v,3) for v in (c.matrix_world.to_3x3()@Vector((0,0,-1)))),c.data.lens)
f=bpy.data.objects['QS_footway_546643369_UNVERIFIED']; s=bpy.data.objects['QS_service_546643370_UNVERIFIED']
for o in (f,s):
    bb=[o.matrix_world@Vector(v) for v in o.bound_box]; print('BB',o.name,round(min(b.x for b in bb),1),round(max(b.x for b in bb),1),round(min(b.y for b in bb),1),round(max(b.y for b in bb),1))
