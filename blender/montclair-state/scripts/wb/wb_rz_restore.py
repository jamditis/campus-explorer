"""wb: undo wb changes on WT verts that are off-slab and have RZ2 within 1.5 m (west side of walk 435, already flush with RZ2) - the raise opened black crack lines at the WT/RZ2 seam."""
import bpy,numpy as np,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R='/workspace/nj-scenes/montclair-state'; O=bpy.data.objects; dg=bpy.context.evaluated_depsgraph_get()
def bvh(o):
    e=o.evaluated_get(dg); m=e.to_mesh(); b=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return b
def top(B,x,y):
    z=[h[0].z for b in B for h in [b.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))] if h[0] is not None]; return max(z) if z else None
RZ=[bvh(O['RZ2_SC_LiDAR_ground_patch_UNVERIFIED'])]
SL=[bvh(O[n]) for n in O.keys() if O[n].type=='MESH' and n.startswith(('QS_footway_','QW_footway_','QS_service_','TR_footway','SG_'))]
WT=O['WT_richardson_west_LiDAR_patch_UNVERIFIED']; pre=np.load(f'{R}/data/wb/WT_richardso_pre_wb.npy'); mw=WT.matrix_world; k=0; L=[]
for v in WT.data.vertices:
    if abs(v.co.z-pre[v.index][2])<1e-5: continue
    c=mw@v.co
    if top(SL,c.x,c.y) is not None: continue
    near=any(top(RZ,c.x+dx,c.y+dy) is not None for dx in (-1.5,-0.75,0,0.75,1.5) for dy in (-1.5,-0.75,0,0.75,1.5))
    if near: L.append((round(c.x,1),round(c.y,1),round(v.co.z-pre[v.index][2],3))); v.co=Vector(pre[v.index]); k+=1
WT.data.update(); print('RESTORED',k,L[:20])
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED',len(O))
