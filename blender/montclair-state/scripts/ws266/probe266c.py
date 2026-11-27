# ws266 probe C (merge208 CHAIN, NO SAVE): W68 slit, BVH version. Only meshes whose bbox meets the box (no farfield/skirt) get
# their modifiers on; each is evaluated once into a BVHTree; 5 cm downward ray grid -> top two hits per cell. eval266c.json.
import bpy, json, collections, os, numpy as np, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
TAG='P266C'; BX=(-224.0,-212.0,-208.0,-196.0)
def meets(o,m=0.5):
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    return not (max(v.x for v in bb)<BX[0]-m or min(v.x for v in bb)>BX[1]+m or max(v.y for v in bb)<BX[2]-m or min(v.y for v in bb)>BX[3]+m)
obs=[o for o in bpy.context.scene.objects if o.type=='MESH' and not o.hide_render and meets(o) and not o.name.startswith(('BD_farfield','Context_skirt','T_','TREE','MID_canopy','gd_grass'))]
for o in obs:
    for m in o.modifiers:
        if not m.show_viewport: m.show_viewport=True
dg=bpy.context.evaluated_depsgraph_get(); T=[]
for o in obs:
    oe=o.evaluated_get(dg)
    try: me=oe.to_mesh()
    except Exception: continue
    if not me or len(me.polygons)==0: oe.to_mesh_clear(); continue
    bm=bmesh.new(); bm.from_mesh(me); bm.transform(o.matrix_world)
    # crop to the box (+1 m) to keep the tree small
    dl=[f for f in bm.faces if not any(BX[0]-1<v.co.x<BX[1]+1 and BX[2]-1<v.co.y<BX[3]+1 for v in f.verts)]
    bmesh.ops.delete(bm,geom=dl,context='FACES')
    if len(bm.faces): T.append((o.name[:60],BVHTree.FromBMesh(bm)))
    bm.free(); oe.to_mesh_clear()
print(TAG,'objs',len(obs),'trees',len(T),[n for n,_ in T][:40],flush=True)
res=[]; S=0.05
for y in np.arange(BX[2],BX[3],S):
    for x in np.arange(BX[0],BX[1],S):
        h=[]
        for n,t in T:
            r=t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))
            if r[0] is not None: h.append((round(r[0].z,3),n,round(r[1].z,3)))
        h.sort(reverse=True); res.append((round(float(x),3),round(float(y),3),h[:3]))
json.dump(res,open('/workspace/nj-scenes/montclair-state/scripts/ws266/eval266c.json','w'))
print(TAG,'n',len(res),'tops',collections.Counter(r[2][0][1] if r[2] else None for r in res).most_common(25),flush=True)
os._exit(0)
