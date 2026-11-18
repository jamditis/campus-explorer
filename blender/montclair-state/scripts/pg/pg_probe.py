import bpy, bmesh
from mathutils import Vector
for o in bpy.data.objects:
    if 'Feliciano' in o.name or 'PF_' in o.name[:3]:
        if o.type=='MESH':
            bb=[o.matrix_world@Vector(c) for c in o.bound_box]
            mn=[min(v[i] for v in bb) for i in range(3)]; mx=[max(v[i] for v in bb) for i in range(3)]
            print('OBJ',o.name,len(o.data.polygons),[round(x,1) for x in mn],[round(x,1) for x in mx],[m.name for m in o.modifiers],[s.material.name if s.material else None for s in o.material_slots][:6], o.hide_render)
c=bpy.data.objects.get('PF_CAM_closeup_feliciano_entrance')
if c: print('CAM',c.location, c.rotation_euler)
r=[o for o in bpy.data.objects if o.name.startswith('Feliciano') and o.name.endswith('roof (LiDAR)')][0]
me=r.data; mw=r.matrix_world
zs=sorted((mw@v.co).z for v in me.vertices); print('ROOFZ',zs[0],zs[len(zs)//10],zs[len(zs)//2],zs[-1], len(zs))
