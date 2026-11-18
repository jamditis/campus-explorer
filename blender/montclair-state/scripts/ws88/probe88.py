import bpy
from mathutils import Vector
for o in bpy.data.objects:
    if o.type not in ('MESH','CURVE') or o.hide_render: continue
    bb=[o.matrix_world @ Vector(c) for c in o.bound_box]
    xs=[v.x for v in bb]; ys=[v.y for v in bb]; zs=[v.z for v in bb]
    if max(xs)>-184 and min(xs)<-172 and max(ys)>-97 and min(ys)<-72 and (max(xs)-min(xs))<60 and max(zs)>130.5:
        print('P88',o.name[:80],f'x{min(xs):.1f}..{max(xs):.1f} y{min(ys):.1f}..{max(ys):.1f} z{min(zs):.1f}..{max(zs):.1f}',len(o.data.polygons) if o.type=='MESH' else 'curve',o.parent.name if o.parent else '')
