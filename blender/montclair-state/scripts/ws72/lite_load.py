# append only objects whose bbox hits CULL box (chunked), from main; shared by ws72 probes / lite renders
import bpy,os
from mathutils import Vector
src=os.environ.get('SRC','/workspace/nj-scenes/montclair-state/montclair_state.blend')
X0,X1,Y0,Y1=map(float,os.environ['CULL'].split(','))
ALWAYS=set(os.environ.get('ALWAYS','Terrain_LiDAR_DTM_1m').split(','))
SKIP=('tuft','clover','flower','annual','newsroom')+tuple(k for k in os.environ.get('SKIP','').split(',') if k)
with bpy.data.libraries.load(src) as (fr,to): names=[n for n in fr.objects if not any(k in n.lower() for k in SKIP)]
sc=bpy.context.scene
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
C=500; kept=0
for k in range(0,len(names),C):
    with bpy.data.libraries.load(src,link=False) as (fr,to): to.objects=names[k:k+C]
    rm=[]
    for o in to.objects:
        if not o: continue
        ok=False
        if o.name in ALWAYS: ok=True
        elif (o.type in ('MESH','CURVE') or (o.type=='EMPTY' and o.instance_type=='COLLECTION')) and not o.hide_render:
            bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[p.x for p in bb]; ys=[p.y for p in bb]
            ok=min(xs)<X1 and max(xs)>X0 and min(ys)<Y1 and max(ys)>Y0 and max(xs)-min(xs)<float(os.environ.get('MAXSPAN','1200'))
        if ok and not o.hide_render: sc.collection.objects.link(o); kept+=1
        else: rm.append(o)
    bpy.data.batch_remove([o for o in rm if o.name not in sc.objects]); bpy.data.orphans_purge(do_recursive=True)
print('LR kept',kept,flush=True)
