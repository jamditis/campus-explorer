import bpy
from mathutils import Vector
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world @ Vector(c) for c in o.bound_box]
    xs=[v.x for v in bb]; ys=[v.y for v in bb]; zs=[v.z for v in bb]
    cx=(min(xs)+max(xs))/2; cy=(min(ys)+max(ys))/2
    if -200<cx<-150 and -110<cy<-55 and (max(xs)-min(xs))<80:
        print('P87',o.name[:70],f'x{min(xs):.1f}..{max(xs):.1f} y{min(ys):.1f}..{max(ys):.1f} z{min(zs):.1f}..{max(zs):.1f}',len(o.data.polygons),[m.name for m in o.data.materials][:3])
# terrain heights sample
T=bpy.data.objects.get('Terrain_LiDAR_DTM_1m')
