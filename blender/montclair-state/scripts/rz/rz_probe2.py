import bpy
from mathutils import Vector
exec(open('scripts/rz/rz_sc.py').read())
par=bpy.data.collections['RZ_StudentCenter_hero_from_north_UNVERIFIED']
for o in par.all_objects:
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    print('OB',o.name,o.type,len(o.data.polygons) if o.type=='MESH' else '',[round(min(getattr(v,a) for v in bb),1) for a in 'xyz'],[round(max(getattr(v,a) for v in bb),1) for a in 'xyz'],[m.name for m in o.data.materials][:3] if o.type=='MESH' else '', [md.type for md in o.modifiers])
for l in bpy.data.libraries: 
    if 'north' in l.filepath: print('LIB',l.filepath,[i.name for i in bpy.data.images if i.library==l],[x.name for x in bpy.data.objects if x.library==l][:5],[x.name for x in bpy.data.node_groups if x.library==l][:5],[x.name for x in bpy.data.materials if x.library==l][:5])
for i in bpy.data.images:
    if i.name in json.load(open(J))['images']: print('IMG',i.name,i.filepath,i.packed_file is not None)
