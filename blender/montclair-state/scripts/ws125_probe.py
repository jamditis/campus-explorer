import bpy
from mathutils import Vector
for o in bpy.data.objects:
    if o.name.startswith(('WS123_Chapin_W_entrance_storefront','WS124_Chapin_W_landing','WS117_Chapin_W')) or 'threshold' in o.name.lower():
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        print('P',o.name,[round(min(v[i] for v in bb),2) for i in range(3)],[round(max(v[i] for v in bb),2) for i in range(3)],o.rotation_euler[2])
s=[o for o in bpy.data.objects if o.name.startswith('WS124_bed_shrub')]
print('P shrubs',len(s),s[0].data.name,[m.type for m in s[0].modifiers],s[0].active_material.name)
for n in ('WS105_bank_shrub_02_ortho2020',):
    o=bpy.data.objects[n]; print('P',n,[m.type for m in o.modifiers])
for n in ('WS116_Chapin_W_bed_E1','WS116_Chapin_W_bed_E2','WS116_Chapin_W_bed_W'):
    o=bpy.data.objects[n]; print('P',n,len(o.data.polygons),sum(p.area for p in o.data.polygons))
