# ws271 probe (no save): dump paving mesh + evaluated ground grid in the two W72 leftover windows + nearby objects.
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OB=bpy.data.objects; NAME='WS268_W72_CollegeAve_Lot33_paving_UNVERIFIED'
pav=OB[NAME]; mw=pav.matrix_world; me=pav.data
V=np.array([tuple(mw@v.co) for v in me.vertices]); F=[list(p.vertices) for p in me.polygons]
FM=np.array([p.material_index for p in me.polygons]); FN=np.array([tuple(p.normal) for p in me.polygons])
mats=[m.name if m else '' for m in me.materials]
GN=('WS68_RHD_ground_northDTM','M3b_north_LiDAR_DTM_1m_west_rail_corridor_UNVERIFIED_seam')
gobs=[o for o in OB if o.type=='MESH' and o.name.startswith(GN)]
for o in gobs:
    for m in o.modifiers: m.show_viewport=True
dg=bpy.context.evaluated_depsgraph_get(); GT=[]
for o in gobs:
    oe=o.evaluated_get(dg); m2=oe.to_mesh(); bm=bmesh.new(); bm.from_mesh(m2); bm.transform(o.matrix_world)
    bmesh.ops.delete(bm,geom=[f for f in bm.faces if not any(-400<v.co.x<-340 and -50<v.co.y<-12 for v in f.verts)],context='FACES')
    GT.append(BVHTree.FromBMesh(bm)); bm.free(); oe.to_mesh_clear()
def gz(x,y):
    b=np.nan
    for t in GT:
        r=t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))
        if r[0] is not None and (np.isnan(b) or r[0].z>b): b=r[0].z
    return b
xs=np.arange(-398,-340,0.25); ys=np.arange(-48,-12,0.25)
G=np.array([[gz(x,y) for x in xs] for y in ys])
near=[]
for o in OB:
    if o.type!='MESH' or not o.visible_get(): pass
    try:
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    except Exception: continue
    x0=min(b.x for b in bb);x1=max(b.x for b in bb);y0=min(b.y for b in bb);y1=max(b.y for b in bb)
    if x1>-375 and x0<-350 and y1>-26 and y0<-15 and (x1-x0)<200: near.append((o.name,o.hide_render,round(x0,1),round(x1,1),round(y0,1),round(y1,1)))
for n in near: print('P271NEAR',n)
np.savez_compressed('/workspace/nj-scenes/montclair-state/scripts/ws271/probe271a.npz',V=V,FM=FM,FN=FN,G=G,xs=xs,ys=ys,F=np.array([f+[-1]*(8-len(f)) for f in F]))
print('P271 mats',mats,'nv',len(V),'nf',len(F),flush=True)
