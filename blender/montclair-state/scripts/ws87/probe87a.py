import bpy,re
pat=re.compile(r'median|island|cole|arcade|loggia|statue|terrace|gazebo|WS77|mulch|ramp|rail',re.I)
for o in bpy.data.objects:
    if pat.search(o.name):
        mats=[m.name for m in o.data.materials] if o.type=='MESH' and o.data else []
        bb=[o.matrix_world @ __import__('mathutils').Vector(c) for c in o.bound_box]
        xs=[v.x for v in bb]; ys=[v.y for v in bb]; zs=[v.z for v in bb]
        print('P87',o.name,o.type,'hid' if o.hide_render else 'vis',f'x{min(xs):.1f}..{max(xs):.1f} y{min(ys):.1f}..{max(ys):.1f} z{min(zs):.1f}..{max(zs):.1f}',mats[:4])
