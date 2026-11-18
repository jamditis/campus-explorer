"""wb clamp: WT verts changed in wb must stay >=1 cm below RZ2 where RZ2 overlies them, and faces must not poke any walk slab (clamp verts to slab-top -1.5 cm when a slab is within 0.6 m). Reports pokes."""
import bpy,numpy as np,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R='/workspace/nj-scenes/montclair-state'; O=bpy.data.objects; dg=bpy.context.evaluated_depsgraph_get()
def bvh(o):
    e=o.evaluated_get(dg); m=e.to_mesh(); b=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return b
def top(B,x,y):
    z=[h[0].z for b in B for h in [b.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))] if h[0] is not None]; return max(z) if z else None
rz=[n for n in O.keys() if n.startswith('RZ2_')]; print('RZ2',rz,[ (O[n].active_material.name if O[n].active_material else None) for n in rz])
RZ=[bvh(O[n]) for n in rz]
SLn=[n for n in O.keys() if O[n].type=='MESH' and n.startswith(('QS_footway_','QW_footway_','QS_service_','TR_footway','SG_'))]
SL={n:bvh(O[n]) for n in SLn}
WT=O['WT_richardson_west_LiDAR_patch_UNVERIFIED']
def pokes():
    G=[bvh(O[n]) for n in O.keys() if O[n].type=='MESH' and n.startswith(('WT_richardson_west_LiDAR','RZ2_','WF_east_dorm_LiDAR','WU_richardson_reid','QW_DTM'))]
    W=bvh(WT); out=[]; rzp=0
    for x in np.arange(38,78,0.25):
        for y in np.arange(310,319,0.25):
            s=top(SL.values(),x,y); w=top([W],x,y)
            if s is not None and w is not None and w>s-0.005: out.append((round(x,2),round(y,2),round(w-s,3),[n[11:20] for n,b in SL.items() if top([b],x,y) is not None]))
            r=top(RZ,x,y)
            if r is not None and w is not None and w>r+0.002 and s is None: rzp+=1
    return out,rzp
p,r=pokes(); print('BEFORE slabpokes',len(p),p[:12],'rzpokes',r)
pre=np.load(f'{R}/data/wb/WT_richardso_pre_wb.npy'); mw=WT.matrix_world; mi=mw.inverted(); k=0
for v in WT.data.vertices:
    if abs(v.co.z-pre[v.index][2])<1e-5: continue
    c=mw@v.co; lim=[]
    r=top(RZ,c.x,c.y)
    if r is not None: lim.append(r-0.01)
    for dx in (-0.6,-0.3,0,0.3,0.6):
        for dy in (-0.6,-0.3,0,0.3,0.6):
            s=top(SL.values(),c.x+dx,c.y+dy)
            if s is not None: lim.append(s-0.015)
    if lim:
        L=max(min(lim),pre[v.index][2]+0) if False else min(lim)
        if c.z>L:
            c.z=max(L,(mi.inverted()@Vector(pre[v.index])).z); v.co=mi@c; k+=1
WT.data.update(); bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
p,r=pokes(); print('CLAMPED',k,'AFTER slabpokes',len(p),p[:12],'rzpokes',r)
for it in range(3):
    if not p: break
    Wb=bvh(WT); ids={}
    for x,y,d,_ in p:
        h=Wb.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))
        if h[2] is None: continue
        for vi in WT.data.polygons[h[2]].vertices: ids[vi]=max(ids.get(vi,0),d+0.012)
    for vi,d in ids.items(): WT.data.vertices[vi].co.z-=d
    WT.data.update(); bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
    p,r=pokes(); print('POKEFIX',it,len(ids),len(p),'rz',r)
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED',len(O))
