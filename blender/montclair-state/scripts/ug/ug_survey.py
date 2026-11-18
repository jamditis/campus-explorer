import bpy, json
from mathutils import Vector
out=[]
for o in bpy.data.objects:
    if o.type!='MESH' and o.type!='CAMERA': continue
    if not (o.get('ty_obj') or o.get('tx_obj') or o.get('ud_obj') or o.name.startswith(('TY_','TX_','UD_'))): continue
    if o.type=='MESH':
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        mn=[round(min(v[i] for v in bb),2) for i in range(3)]; mx=[round(max(v[i] for v in bb),2) for i in range(3)]
        out.append((o.name,'M',len(o.data.vertices),mn,mx,o.hide_render,[s.material.name if s.material else '-' for s in o.material_slots][:2]))
    else:
        out.append((o.name,'C',tuple(round(x,2) for x in o.location),tuple(round(x,3) for x in o.rotation_euler),o.data.lens))
for r in out: print('UGS',r)
