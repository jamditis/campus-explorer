import bpy
from mathutils import Vector
for cn in ('North_CELS_20261014p','CELS_windows_ground_arch_20261015au','CELS_windows_modelled_20261015at'):
    c=bpy.data.collections.get(cn); print('C',cn,len(c.all_objects),[ch.name for ch in c.children], c.library)
    ic=set()
    for o in c.all_objects:
        if o.instance_collection: ic.add((o.instance_collection.name, str(o.instance_collection.library)))
        if o.type=='MESH':
            bb=[o.matrix_world@Vector(q) for q in o.bound_box]; print('  M',o.name[:60],round(min(p.z for p in bb),2),round(max(p.z for p in bb),2),[m.name for m in o.data.materials][:4])
    print('  IC',ic)
print('LIBS',[(l.name,l.filepath) for l in bpy.data.libraries])
