import bpy
from mathutils import Vector
P='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(P) as (df,dt):
    dt.objects=[n for n in df.objects if not n.startswith(('T_','Tree','ShrubLeaf','Leaf','Grass')) and 'CAM' not in n]
for o in dt.objects:
    if o is None or o.type not in ('MESH','CURVE','EMPTY'): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    xs=[v.x for v in bb]; ys=[v.y for v in bb]; zs=[v.z for v in bb]
    if max(xs)<-182 or min(xs)>-150 or max(ys)<-268 or min(ys)>-222: continue
    if max(xs)-min(xs)>150: continue
    print('OB',o.name[:60],o.type,'x %.1f %.1f y %.1f %.1f z %.1f %.1f'%(min(xs),max(xs),min(ys),max(ys),min(zs),max(zs)),'hide_render',o.hide_render,[c.name[:25] for c in o.users_collection][:2])
