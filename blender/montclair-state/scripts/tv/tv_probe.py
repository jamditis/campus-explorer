import bpy
from mathutils import Vector
cam=bpy.data.objects['TU_CAM_eye_Blanton_W_entrances']
print('CAM',tuple(cam.location), tuple(cam.rotation_euler))
for o in bpy.data.objects:
    if 'grass' in o.name.lower() and o.type=='MESH':
        vs=o.data.vertices
        if len(vs)==0: continue
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        x0=min(b.x for b in bb);x1=max(b.x for b in bb);y0=min(b.y for b in bb);y1=max(b.y for b in bb)
        if x1<60 or x0>180 or y1<380 or y0>470: continue
        mods=[m.name for m in o.modifiers]
        print(o.name,len(vs),round(x0),round(x1),round(y0),round(y1),o.hide_render,mods[:3])
