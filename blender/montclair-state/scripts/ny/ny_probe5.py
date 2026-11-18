import bpy, mathutils
for o in bpy.data.objects:
    if o.type=='MESH' and ('N classroom' in o.name) and ('ceiling' in o.name.lower() or 'room shell' in o.name or 'light' in o.name.lower() or 'troffer' in o.name.lower()):
        cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]
        zs=sorted(set(round((o.matrix_world@v.co).z,4) for v in o.data.vertices))[:6]
        print('P5',o.name,o.hide_render,[round(min(c[i] for c in cs),3) for i in range(3)],[round(max(c[i] for c in cs),3) for i in range(3)],len(o.data.polygons),zs,[s.material.name for s in o.material_slots if s.material])
