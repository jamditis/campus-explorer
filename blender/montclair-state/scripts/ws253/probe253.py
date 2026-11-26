# ws253 read-only probe (CHAIN via merge208, exits before save): objects + Footpaths_OSM faces in the W63d box
import bpy, os
from mathutils import Vector
B=(-193,-176,162,185)
for o in bpy.data.objects:
    if o.type not in ('MESH','CURVE','EMPTY'): continue
    try: bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    except Exception: continue
    xs=[v.x for v in bb]; ys=[v.y for v in bb]; zs=[v.z for v in bb]
    if max(xs)<B[0] or min(xs)>B[1] or max(ys)<B[2] or min(ys)>B[3]: continue
    if (max(xs)-min(xs))>120: continue
    print('PR253',o.name,o.type,'x %.1f..%.1f y %.1f..%.1f z %.2f..%.2f'%(min(xs),max(xs),min(ys),max(ys),min(zs),max(zs)),'hide_r',o.hide_render,o.library.name if o.library else '',[m.name for m in o.modifiers][:3],flush=True)
for n in ('Footpaths_OSM','Roads_OSM'):
    o=bpy.data.objects.get(n)
    if not o: continue
    M=o.matrix_world; me=o.data; k=0
    for p in me.polygons:
        c=M@p.center
        if B[0]<c.x<B[1] and B[2]<c.y<B[3]:
            k+=1
            if k<=60: print('PF253',n,p.index,'c %.1f %.1f %.2f'%(c.x,c.y,c.z),'area %.1f'%p.area,flush=True)
    print('PF253',n,'faces in box',k,'mods',[m.name for m in o.modifiers],flush=True)
os._exit(0)
