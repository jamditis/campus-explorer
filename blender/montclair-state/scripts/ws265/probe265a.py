# ws265 probe (merge208 CHAIN, NO SAVE): police flat lawn S/W of the merged grass. Dump the existing grass points, then ray-cast
# a jittered candidate grid over the W263 mask box on main's EVALUATED ground (modifiers re-enabled only on meshes meeting the box),
# record the top object, z, normal z and the ortho colour at the hit (UV of the hit face -> the material's ortho image).
import bpy, json, collections, os, numpy as np
from mathutils import Vector
from mathutils.interpolate import poly_3d_calc
TAG='P265A'; BX=(-354.68,-323.43,-7.61,35.64)
G=bpy.data.objects['gd_grass_police_lawn_points']; W=G.matrix_world
E=np.array([tuple(W@v.co) for v in G.data.vertices]); np.save('/workspace/nj-scenes/montclair-state/scripts/ws265/grass_exist265.npy',E)
def meets(o,m=2):
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    return not (max(v.x for v in bb)<BX[0]-m or min(v.x for v in bb)>BX[1]+m or max(v.y for v in bb)<BX[2]-m or min(v.y for v in bb)>BX[3]+m)
on=[]
for o in bpy.data.objects:
    if o.type=='MESH' and meets(o) and o!=G:
        for m in o.modifiers:
            if not m.show_viewport: m.show_viewport=True; on.append((o,m))
print(TAG,'existing',len(E),'mods on',len(on),flush=True)
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
IMG={}
def ortho_of(ob):
    if ob.name in IMG: return IMG[ob.name]
    r=None
    for ms in ob.material_slots:
        if ms.material and ms.material.node_tree:
            for n in ms.material.node_tree.nodes:
                if n.type=='TEX_IMAGE' and n.image and 'ortho' in n.image.name.lower():
                    im=n.image; w,h=im.size; px=np.array(im.pixels[:],np.float32).reshape(h,w,4); r=(im.name,px); break
        if r: break
    IMG[ob.name]=r; print(TAG,'ORTHO',ob.name[:50],r and r[0],flush=True); return r
rng=np.random.default_rng(265); S=0.35
xs=np.arange(BX[0],BX[1],S); ys=np.arange(BX[2],BX[3],S)
C=np.array([(x,y) for y in ys for x in xs])+rng.uniform(-S/2,S/2,(len(xs)*len(ys),2))
res=[]
for x,y in C:
    o0=Vector((x,y,200)); hit=None
    for k in range(40):
        r=sc.ray_cast(dg,o0,Vector((0,0,-1)))
        if not r[0]: break
        ob=r[4]
        if not (ob.name.startswith(('T_','TREE','MID_canopy','gd_grass')) or ob.hide_render): hit=r; break
        o0=r[1]+Vector((0,0,-0.0005))
    if not hit: res.append((x,y,None,None,None,None)); continue
    ok,loc,nrm,fi,ob,mx=hit; col=None
    oi=ortho_of(ob)
    if oi:
        me=ob.evaluated_get(dg).data; uvl=me.uv_layers.active
        if uvl and fi<len(me.polygons):
            p=me.polygons[fi]; lp=mx.inverted()@loc
            wts=poly_3d_calc([me.vertices[i].co for i in p.vertices],lp)
            uv=sum((uvl.data[li].uv*w for li,w in zip(p.loop_indices,wts)),Vector((0,0)))
            h,w_=oi[1].shape[:2]; c=oi[1][min(h-1,max(0,int(uv.y*h))),min(w_-1,max(0,int(uv.x*w_)))]; col=[round(float(c[0]),3),round(float(c[1]),3),round(float(c[2]),3)]
    res.append((round(x,3),round(y,3),ob.name[:60],round(loc.z,3),round(nrm.z,3),col))
json.dump(res,open('/workspace/nj-scenes/montclair-state/scripts/ws265/eval265a.json','w'))
print(TAG,'cands',len(res),'tops',collections.Counter(r[2] for r in res).most_common(20),flush=True)
for o,m in on: m.show_viewport=False
os._exit(0)
