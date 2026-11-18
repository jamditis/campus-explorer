import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
src='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(src,link=False) as (fr,to):
    to.objects=[n for n in fr.objects if not n.startswith('T_') and not any(k in n.lower() for k in ('tuft','clover','leaf','flower','annual','newsroom'))]
cand=[]
for o in to.objects:
    if not o or o.type!='MESH': continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if min(p.x for p in bb)<-180 and max(p.x for p in bb)>-248 and min(p.y for p in bb)<44 and max(p.y for p in bb)>-4 and (max(p.x for p in bb)-min(p.x for p in bb))<3000: cand.append(o)
print('BW cands',len(cand),[o.name[:40] for o in cand][:80])
for o in cand: bpy.context.scene.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get(); dg.update()
pts=[(-230,6),(-222,10),(-218,10),(-234,6),(-226,2),(-214,14),(-242,26),(-234,30),(-222,26),(-238,18),(-206,6),(-200,0)]
res={p:[] for p in pts}
for o in cand:
    try: me=o.evaluated_get(dg).to_mesh()
    except Exception: continue
    if not me or len(me.polygons)==0: continue
    bm=bmesh.new(); bm.from_mesh(me); bm.transform(o.matrix_world); T=BVHTree.FromBMesh(bm)
    for x,y in pts:
        h=T.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),1000)[0]
        if h: res[(x,y)].append((round(h.z,2),o.name[:50]))
for p,v in res.items(): print('BH',p,sorted(v,reverse=True)[:6])
