import bpy
from mathutils import Vector
o=bpy.data.objects['PZ_Dickson_wing_coping_joints_corners_UNVERIFIED']; me=o.data
for p in me.polygons:
    c=p.center
    if (c.xy-Vector((-176.64,159.78))).length<0.7: print('F %d c %.3f %.3f %.3f n %.2f %.2f %.2f area %.4f'%(p.index,c.x,c.y,c.z,p.normal.x,p.normal.y,p.normal.z,p.area))
for on in ('PY_Dickson_wing_parapet_coping_UNVERIFIED','PY_Dickson_wing_parapet_back_roofstrip_UNVERIFIED','PZ_Dickson_wing_coping_drip_stain_UNVERIFIED'):
    o=bpy.data.objects[on]
    for p in o.data.polygons:
        c=p.center
        if (c.xy-Vector((-176.5,159.6))).length<0.5 and p.normal.z>0.5: print(on[:12],'F c %.3f %.3f %.3f n %.2f'%(c.x,c.y,c.z,p.normal.z))
