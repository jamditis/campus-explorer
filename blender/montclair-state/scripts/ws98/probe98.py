import bpy,math
from mathutils import Vector
X0,X1,Y0,Y1=-228,-198,-104,-66
sc=bpy.context.scene
for cn in ['WS79_CAM_closeup_island_E_end_patch','WS79_CAM_oblique_lots_E','WS78_CAM_eye_lot_from_E','WS78_CAM_eye_lot_from_W']:
    c=bpy.data.objects.get(cn)
    if c: print("CAM",cn,tuple(round(a,2) for a in c.matrix_world.translation),tuple(round(math.degrees(a),1) for a in c.matrix_world.to_euler()), c.data.lens)
hits=[]
for o in sc.objects:
    if o.type not in ('MESH','CURVE') : continue
    if o.hide_render: continue
    bb=[o.matrix_world@Vector(b) for b in o.bound_box]
    xs=[b.x for b in bb]; ys=[b.y for b in bb]
    if max(xs)<X0 or min(xs)>X1 or max(ys)<Y0 or min(ys)>Y1: continue
    area=(max(xs)-min(xs))*(max(ys)-min(ys))
    if area>40000: continue
    hits.append(o.name); print("OBJ",o.name,o.type,round(min(xs),1),round(max(xs),1),round(min(ys),1),round(max(ys),1),round(min(b.z for b in bb),2),round(max(b.z for b in bb),2),[m.name for m in o.data.materials][:2] if hasattr(o.data,'materials') else '')
