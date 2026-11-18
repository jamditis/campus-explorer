import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
src='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(src,link=False) as (fr,to):
    to.objects=[n for n in fr.objects if not n.startswith('T_') and not any(k in n.lower() for k in ('grass','tuft','clover','leaf','scatter','shrub','flower','annual','newsroom'))]
cand=[]
for o in to.objects:
    if not o or o.type!='MESH': continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if min(p.x for p in bb)<125 and max(p.x for p in bb)>95 and min(p.y for p in bb)<-60 and max(p.y for p in bb)>-76: cand.append(o)
print('PB cands',len(cand))
for o in cand: bpy.context.scene.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get()
pts=[(x,y) for x in (100,108,115,122) for y in (-62,-66,-70,-74)]
for o in cand:
    try:
        me=o.evaluated_get(dg).to_mesh()
    except Exception: continue
    bm=bmesh.new(); bm.from_mesh(me); bm.transform(o.matrix_world); T=BVHTree.FromBMesh(bm)
    hits=[]
    for x,y in pts:
        r=T.ray_cast(Vector((x,y,300)),Vector((0,0,-1)),600)
        if r[0]: hits.append(f'({x},{y}){r[0].z:.1f}')
    if hits: print('PB',o.name[:60],' '.join(hits))
