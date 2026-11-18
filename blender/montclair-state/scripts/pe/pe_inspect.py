import bpy, sys, mathutils, json
names=sys.argv[sys.argv.index('--')+1:]
out=[]
for o in bpy.data.objects:
    n=o.name.lower()
    if any(k in n for k in names) or any(k in (c.name.lower()) for c in o.users_collection for k in names):
        bb=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box] if o.type in('MESH','CURVE','FONT') else [o.matrix_world.translation]
        mn=[round(min(v[i] for v in bb),2) for i in range(3)]; mx=[round(max(v[i] for v in bb),2) for i in range(3)]
        out.append((o.name,o.type,[c.name for c in o.users_collection][:2],mn,mx,[s.material.name if s.material else None for s in o.material_slots][:3], o.library.filepath if o.library else (o.data.library.filepath if o.data and getattr(o.data,'library',None) else '')))
for r in out: print('OBJ',r)
print('COUNT',len(out))
