# ws273 probe C (NO SAVE): evaluated top surface (BVH per mesh, render-visible only) over the Sprague lot S edge / grandstand lawn N end.
import bpy, os, collections, numpy as np, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
TAG='P273E'; BX=(-262.0,-230.0,-110.0,-88.0)
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
    dl=[f for f in bm.faces if not any(BX[0]-1<v.co.x<BX[1]+1 and BX[2]-1<v.co.y<BX[3]+1 for v in f.verts)]
    bmesh.ops.delete(bm,geom=dl,context='FACES')
    if len(bm.faces): MAT=[ (me.materials[f.material_index].name if f.material_index<len(me.materials) and me.materials[f.material_index] else None) for f in bm.faces]; T.append((o.name[:30]+'|',BVHTree.FromBMesh(bm),MAT))
    bm.free(); oe.to_mesh_clear()
print(TAG,'trees',[n for n,_,_ in T],flush=True)
K={}; S=1.0
for y in np.arange(BX[3]-0.5,BX[2],-S):
    a='';b='';c=''
    for x in np.arange(BX[0]+0.5,BX[1],S):
        best=None
        for n,t,MT in T:
            r=t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))
            if r[0] is not None and (best is None or r[0].z>best[0].z): best=(r[0],r[1],n+str(MT[r[2]])[:28])
        if best is None: a+='.';b+='.';c+='  ';continue
        if best[2] not in K: K[best[2]]=chr(65+len(K))
        a+=K[best[2]]
        nz=best[1].z; ny=best[1].y
        b+= 'N' if ny>0.05 else ('S' if ny<-0.05 else '-')
        c+=f'{int(round((best[0].z-120)*10))%100:02d}'
    print(TAG,f'{y:7.1f} {a}  {b}',flush=True)
    print(TAG,'   z   ',c,flush=True)
for k,v in K.items(): print(TAG,'KEY',v,k,flush=True)
sun=[o for o in bpy.data.objects if o.type=='LIGHT' and o.data.type=='SUN']
for s in sun: print(TAG,'SUN',s.name,tuple(round(v,3) for v in (s.matrix_world.to_quaternion()@Vector((0,0,-1)))),s.hide_render,flush=True)
os._exit(0)
