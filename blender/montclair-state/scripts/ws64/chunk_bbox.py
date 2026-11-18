# list objects whose world bbox overlaps a box, loading the main file in chunks to stay light
import bpy,os,json
from mathutils import Vector
src='/workspace/nj-scenes/montclair-state/montclair_state.blend'
X0,X1,Y0,Y1=map(float,os.environ['BOX'].split(','))
with bpy.data.libraries.load(src) as (fr,to): names=[n for n in fr.objects if (n.startswith('T_') if os.environ.get('TONLY') else (not n.startswith('T_') and not any(k in n.lower() for k in ('tuft','clover','leaf','flower','annual','newsroom'))))]
print('CB total',len(names)); hits=[]
C=int(os.environ.get('CH','600'))
for k in range(0,len(names),C):
    with bpy.data.libraries.load(src,link=False) as (fr,to): to.objects=names[k:k+C]
    for o in to.objects:
        if not o: continue
        try: bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        except Exception: continue
        xs=[p.x for p in bb]; ys=[p.y for p in bb]; zs=[p.z for p in bb]
        if min(xs)<X1 and max(xs)>X0 and min(ys)<Y1 and max(ys)>Y0 and max(xs)-min(xs)<400: hits.append((o.name,o.type,round(min(xs)),round(max(xs)),round(min(ys)),round(max(ys)),round(min(zs),1),round(max(zs),1)))
    bpy.data.batch_remove([o for o in to.objects if o]); bpy.data.orphans_purge(do_recursive=True)
json.dump(hits,open(os.environ['OUT'],'w')); print('CB hits',len(hits))
for h in hits: print('CBH',h)
