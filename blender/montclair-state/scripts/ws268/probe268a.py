# ws267 probe A (ortho colour sampled later outside Blender from UV; pixels[:] blew memory) (EVAL=0 default: base meshes, modifiers off -- the evaluated version was watchdog-killed at 1.15 GB)
# ws267 probe A (merge208 CHAIN, NO SAVE): police south-walk strip S of the W263 box. BVH per evaluated mesh meeting the box
# (probe266c pattern; no scene.ray_cast), jittered 0.35 m samples: top object, z, normal z, ortho RGB at the hit (face UV).
import bpy, json, collections, os, numpy as np, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.interpolate import poly_3d_calc
TAG='P268A'; BX=tuple(float(v) for v in os.environ.get('BX','-358,-320,-24,-5').split(','))
def meets(o,m=0.5):
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    return not (max(v.x for v in bb)<BX[0]-m or min(v.x for v in bb)>BX[1]+m or max(v.y for v in bb)<BX[2]-m or min(v.y for v in bb)>BX[3]+m)
obs=[o for o in bpy.context.scene.objects if o.type=='MESH' and not o.hide_render and meets(o) and not o.name.startswith(('BD_farfield','Context_skirt','T_','TREE','MID_canopy','gd_grass'))]
EVAL=os.environ.get('EVAL','0')=='1'
print(TAG,'EVAL',EVAL,flush=True)
for o in (obs if EVAL else []):
    for m in o.modifiers:
        if not m.show_viewport: m.show_viewport=True
G=bpy.data.objects['gd_grass_police_lawn_points']; GW=G.matrix_world
E=np.array([tuple(GW@v.co) for v in G.data.vertices]); sel=(E[:,0]>BX[0])&(E[:,0]<BX[1])&(E[:,1]>BX[2])&(E[:,1]<BX[3])
print(TAG,'grass pts in box',int(sel.sum()),flush=True)
def ortho_of(ob):
    for ms in ob.material_slots:
        if ms.material and ms.material.node_tree:
            for n in ms.material.node_tree.nodes:
                if n.type=='TEX_IMAGE' and n.image and 'ortho' in n.image.name.lower():
                    im=n.image; return (im.name,bpy.path.abspath(im.filepath,library=im.library))
    return None
T=[]
dg=bpy.context.evaluated_depsgraph_get() if EVAL else None
for o in obs:
    oe=o.evaluated_get(dg) if EVAL else o
    try: me=oe.to_mesh() if EVAL else o.data
    except Exception: continue
    if not me or len(me.polygons)==0: continue
    bm=bmesh.new(); bm.from_mesh(me); bm.transform(o.matrix_world)
    dl=[f for f in bm.faces if not any(BX[0]-1<v.co.x<BX[1]+1 and BX[2]-1<v.co.y<BX[3]+1 for v in f.verts)]
    bmesh.ops.delete(bm,geom=dl,context='FACES')
    if len(bm.faces):
        bm.faces.ensure_lookup_table(); oi=ortho_of(o)
        T.append((o.name[:60],BVHTree.FromBMesh(bm),bm if oi else None,oi))
        if not oi: bm.free()
    else: bm.free()
    if EVAL: oe.to_mesh_clear()
print(TAG,'objs',len(obs),'trees',len(T),[(n,oi and oi[0]) for n,_,_,oi in T],flush=True)
IMGS={oi[0]:oi[1] for _,_,_,oi in T if oi}
rng=np.random.default_rng(268); S=0.5
xs=np.arange(BX[0],BX[1],S); ys=np.arange(BX[2],BX[3],S)
C=np.array([(x,y) for y in ys for x in xs])+rng.uniform(-S/2,S/2,(len(xs)*len(ys),2)); res=[]
for x,y in C:
    best=None
    for n,t,bm,oi in T:
        r=t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))
        if r[0] is not None and (best is None or r[0].z>best[1][0].z): best=(n,r,bm,oi)
    if not best: res.append((round(x,3),round(y,3),None,None,None,None)); continue
    n,(loc,nrm,fi,_),bm,oi=best; col=None
    if bm is not None:
        uvl=bm.loops.layers.uv.active; f=bm.faces[fi]
        if uvl:
            wts=poly_3d_calc([l.vert.co for l in f.loops],loc); uv=sum((l[uvl].uv*w for l,w in zip(f.loops,wts)),Vector((0,0)))
            col=[oi[0],round(uv.x,6),round(uv.y,6)]
    res.append((round(x,3),round(y,3),n,round(loc.z,3),round(abs(nrm.z),3),col))
json.dump({'imgs':IMGS,'box':BX,'res':res,'grass':E[sel].round(3).tolist()},open('/workspace/nj-scenes/montclair-state/scripts/ws268/eval268a.json','w'))
print(TAG,'n',len(res),'tops',collections.Counter(r[2] for r in res).most_common(30),flush=True)
os._exit(0)
