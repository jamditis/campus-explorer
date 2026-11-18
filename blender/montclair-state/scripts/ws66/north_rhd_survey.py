import bpy,json
from mathutils import Vector
src='/workspace/nj-scenes/montclair-state/north/montclair_north.blend'
with bpy.data.libraries.load(src) as (fr,to): names=list(fr.objects); cols=list(fr.collections)
print('NS objs',len(names)); print('NS cols',[c for c in cols if any(k in c.lower() for k in ('hawk','rhd','deck','kasser'))])
sel=[n for n in names if any(k in n.lower() for k in ('red hawk','redhawk','rhd','kasser','deck'))]
with bpy.data.libraries.load(src,link=False) as (fr,to): to.objects=sel
tot=0
for o in to.objects:
    if not o: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[p.x for p in bb]; ys=[p.y for p in bb]; zs=[p.z for p in bb]
    nf=len(o.data.polygons) if o.type=='MESH' else 0; tot+=nf
    print('NSO',o.name[:60],o.type,nf,round(min(xs)),round(max(xs)),round(min(ys)),round(max(ys)),round(min(zs),1),round(max(zs),1),o.library is not None, o.data.library is not None if o.data else '')
print('NS tot faces',tot)
