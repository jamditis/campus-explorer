# lite render: append only objects inside CULL box (chunked) + terrain/skirt/apron + golden world/sun, then render CAMS via render59 camera helpers
import bpy,os
from mathutils import Vector
src='/workspace/nj-scenes/montclair-state/montclair_state.blend'
X0,X1,Y0,Y1=map(float,os.environ['CULL'].split(','))
ALWAYS={'Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km','WS60_terrain_edge_apron_LiDAR_to_skirt','WP2_Sun_GOLDEN'}
with bpy.data.libraries.load(src) as (fr,to): names=[n for n in fr.objects if not any(k in n.lower() for k in ('tuft','clover','flower','annual','newsroom'))]; worlds=list(fr.worlds)
with bpy.data.libraries.load(src,link=False) as (fr,to): to.worlds=['WP2_World_GOLDEN']
sc=bpy.context.scene; sc.world=bpy.data.worlds['WP2_World_GOLDEN']
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
C=300; kept=0
for k in range(0,len(names),C):
    with bpy.data.libraries.load(src,link=False) as (fr,to): to.objects=names[k:k+C]
    rm=[]
    for o in to.objects:
        if not o: continue
        ok=False
        if any(o.name.startswith(a) for a in ALWAYS): ok=True
        elif (o.type in ('MESH','CURVE') or (o.type=='EMPTY' and o.instance_type=='COLLECTION')) and not o.hide_render:
            bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[p.x for p in bb]; ys=[p.y for p in bb]
            ok=min(xs)<X1 and max(xs)>X0 and min(ys)<Y1 and max(ys)>Y0 and max(xs)-min(xs)<1200
        if ok and not o.hide_render: sc.collection.objects.link(o); kept+=1
        elif o.users==0 or not ok: rm.append(o)
    bpy.data.batch_remove([o for o in rm if o.users<=1 and o.name not in sc.objects]); bpy.data.orphans_purge(do_recursive=True)
print('LR kept',kept,flush=True)
sv=open('/workspace/nj-scenes/montclair-state/scripts/ws67/render67.py').read()
exec(compile(sv,'r67','exec'))
