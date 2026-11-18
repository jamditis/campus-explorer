import bpy, mathutils, json
cam = bpy.data.objects['UV_CAM_eye_Freeman_N_entrance']
print('CAM', tuple(round(v,2) for v in cam.location), tuple(round(v,3) for v in cam.rotation_euler))
out=[]
for o in bpy.data.objects:
    if 'Freeman' not in o.name and not o.name.startswith(('UV_','UW_','VA_')): continue
    if o.type!='MESH': continue
    bb=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]
    mn=[min(v[i] for v in bb) for i in range(3)]; mx=[max(v[i] for v in bb) for i in range(3)]
    if o.name.startswith(('UV_','UW_','VA_')) or 'entrance' in o.name.lower() or '_N_' in o.name:
        out.append((o.name, o.hide_render, [round(x,2) for x in mn],[round(x,2) for x in mx], len(o.data.polygons), [m.name for m in o.data.materials][:3]))
for r in sorted(out): print(r)
