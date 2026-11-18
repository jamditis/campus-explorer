import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sc=bpy.context.scene
cam=bpy.data.objects['WA1_CAM_eye_stone_footway_from_S']
print('CAM',tuple(round(c,2) for c in cam.matrix_world.translation))
res=[]
for o in bpy.data.objects:
    if o.type!='MESH' or not o.visible_get(): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    pts=[world_to_camera_view(sc,cam,p) for p in bb]
    if all(p.z<0 for p in pts): continue
    xs=[p.x for p in pts if p.z>0]; ys=[p.y for p in pts if p.z>0]
    if not xs: continue
    if max(xs)<0.3 or min(xs)>1 or max(ys)<0 or min(ys)>1: continue
    d=(o.matrix_world.translation-cam.matrix_world.translation).length
    mn=Vector((min(p.x for p in bb),min(p.y for p in bb),min(p.z for p in bb)));mx=Vector((max(p.x for p in bb),max(p.y for p in bb),max(p.z for p in bb)))
    if mn.x>170 or mx.x<130 or mn.y>300 or mx.y<250: continue
    res.append((o.name,len(o.data.vertices),[round(c,1) for c in mn],[round(c,1) for c in mx],[m.name for m in o.data.materials][:3]))
for r in sorted(res,key=lambda r:r[0]): print(r)
