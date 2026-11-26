# ws252 read-only probe (CHAIN via merge208, exits before save): objects in the W63c box
import bpy, os
from mathutils import Vector
B=(-206,-178,150,180)
for o in bpy.data.objects:
    if o.type not in ('MESH','CURVE','EMPTY') : continue
    try: bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    except Exception: continue
    xs=[v.x for v in bb]; ys=[v.y for v in bb]; zs=[v.z for v in bb]
    if max(xs)<B[0] or min(xs)>B[1] or max(ys)<B[2] or min(ys)>B[3]: continue
    if (max(xs)-min(xs))>300: continue
    mats=[m.name for m in getattr(o.data,'materials',[]) if m][:3] if o.type=='MESH' else []
    print('PR252',o.name,o.type,'x %.1f..%.1f y %.1f..%.1f z %.2f..%.2f'%(min(xs),max(xs),min(ys),max(ys),min(zs),max(zs)),'hide_r',o.hide_render,mats,[m.name for m in o.modifiers][:4],flush=True)
os._exit(0)
