import bpy
def col_of(o): return [c.name for c in o.users_collection]
for c in bpy.data.collections:
    if any(k in c.name.lower() for k in ('felic','fsb','business')):
        print('COLL',c.name,len(c.all_objects),'parents',[p.name for p in bpy.data.collections if c.name in p.children])
for o in bpy.data.objects:
    if any(k in o.name.lower() for k in ('felic','fsb','business')):
        print('OBJ',o.type,o.name,'|',col_of(o),'|',[s.material.name for s in o.material_slots if s.material][:3], [m.type+':'+m.name for m in o.modifiers][:3])
