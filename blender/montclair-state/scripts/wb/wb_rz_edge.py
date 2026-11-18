"""wb: RZ2 boundary verts in x44-64,y310-320 sit 2-7 cm above the WT lawn below them (dark slot in the 435 close-up). Lower-only: drop each boundary vert to WT top +0.5 cm (cap 12 cm). Grass re-snap."""
import bpy,numpy as np,sys
from collections import Counter
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R='/workspace/nj-scenes/montclair-state'; O=bpy.data.objects; dg=bpy.context.evaluated_depsgraph_get()
def bvh(o):
    e=o.evaluated_get(dg); m=e.to_mesh(); b=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return b
rz=O['RZ2_SC_LiDAR_ground_patch_UNVERIFIED']; me=rz.data; mw=rz.matrix_world; mi=mw.inverted()
print('mods',[m.type for m in rz.modifiers],len(me.vertices))
W=bvh(O['WT_richardson_west_LiDAR_patch_UNVERIFIED'])
ec=Counter()
for p in me.polygons:
    for a,b in p.edge_keys: ec[(a,b)]+=1
bd=set(v for e,c in ec.items() if c==1 for v in e)
np.save(f'{R}/data/wb/RZ2_pre_wb.npy',np.array([v.co[:] for v in me.vertices]))
k=0;L=[]
for vi in bd:
    v=me.vertices[vi]; c=mw@v.co
    if not (44<=c.x<=64 and 310<=c.y<=320): continue
    h=W.ray_cast(Vector((c.x,c.y,c.z+0.5)),Vector((0,0,-1)))
    if h[0] is None: continue
    t=h[0].z+0.005
    if c.z>t+0.003 and c.z-t<=0.12:
        L.append((round(c.x,2),round(c.y,2),round(c.z-t,3))); c.z=t; v.co=mi@c; k+=1
me.update(); print('LOWERED',k,L)
if k and '--save' in sys.argv:
    bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
    G=[bvh(O[n]) for n in O.keys() if O[n].type=='MESH' and n.startswith(('WT_richardson_west_LiDAR','RZ2_','WF_east_dorm_LiDAR','WU_richardson_reid','QW_DTM'))]
    SL=[bvh(O[n]) for n in O.keys() if O[n].type=='MESH' and n.startswith(('QS_footway_','QW_footway_','QS_service_','TR_footway','SG_'))]
    def top(B,x,y):
        z=[h[0].z for b in B for h in [b.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))] if h[0] is not None]; return max(z) if z else None
    for name in [n for n in O.keys() if 'grass_points' in n]:
        g=O[name]; m=g.matrix_world; m2=m.inverted(); n=0
        if g.type!='MESH': continue
        for v in g.data.vertices:
            c=m@v.co
            if not (43<=c.x<=65 and 309<=c.y<=321): continue
            z=top(G,c.x,c.y)
            if z is None or top(SL,c.x,c.y) is not None: continue
            if abs(c.z-z)>0.005: c.z=z; v.co=m2@c; n+=1
        g.data.update()
        if n: print('GRASS',name,n)
    bpy.ops.wm.save_mainfile(); print('SAVED',len(O))
