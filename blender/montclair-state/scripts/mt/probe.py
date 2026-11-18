import bpy
for o in bpy.data.objects:
    n=o.name.lower()
    if 'tower' in n or 'belfry' in n or 'bell' in n or ('sign' in n and 'ccom' in n) or 'letter' in n:
        bb=[o.matrix_world @ __import__('mathutils').Vector(c) for c in o.bound_box] if o.type=='MESH' else []
        if bb:
            mn=[min(v[i] for v in bb) for i in range(3)]; mx=[max(v[i] for v in bb) for i in range(3)]
            print('OBJ',o.name,o.type,[round(x,2) for x in mn],[round(x,2) for x in mx], [c.name for c in o.users_collection])
        else: print('OBJ',o.name,o.type,[c.name for c in o.users_collection])
print('COUNT',len(bpy.data.objects))
print('FONTS',[f.name for f in bpy.data.fonts])
