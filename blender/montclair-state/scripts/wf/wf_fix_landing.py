import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import os; os.chdir('/workspace/nj-scenes/montclair-state')
dg=bpy.context.evaluated_depsgraph_get()
P=bpy.data.objects['WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED']
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']
Pe=P.evaluated_get(dg); pme=Pe.to_mesh()
bp=BVHTree.FromPolygons([P.matrix_world@v.co for v in pme.vertices],[tuple(p.vertices) for p in pme.polygons]); Pe.to_mesh_clear()
ske=sk.evaluated_get(dg); sme=ske.to_mesh()
bs=BVHTree.FromPolygons([sk.matrix_world@v.co for v in sme.vertices],[tuple(p.vertices) for p in sme.polygons]); ske.to_mesh_clear()
def gz(x,y):
    h=bp.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
    if h[0] is not None and h[0].z>125: return h[0].z
    h=bs.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
    if h[0] is not None and h[0].z>125: return h[0].z
    return None
L=bpy.data.objects['TK_Bohn_landing_W_walk_UNVERIFIED']
# restore bak then full drape
bak=np.load('data/wf/drape_bak.npz')
L.data.vertices.foreach_set('co',bak['TK_Bohn_landing_W_walk_UNVERIFIED'].ravel()); L.data.update()
M=np.array(L.matrix_world); n=8
co=np.zeros(n*3,np.float32); L.data.vertices.foreach_get('co',co); co=co.reshape(n,3)
W=co@M[:3,:3].T+M[:3,3]
for i in range(n):
    g=gz(W[i,0],W[i,1]); print('vert',i,tuple(np.round(W[i],3)),'g',g)
    if g is not None: W[i,2]=g+0.03
invR=np.linalg.inv(M[:3,:3]).T
co2=(W-M[:3,3])@invR
L.data.vertices.foreach_set('co',co2.astype(np.float32).ravel()); L.data.update(); L['wf_drape']=1
# match door sill: landing top should be ~door sill
G=bpy.data.objects['TK_Bohn_door_glass_W_walk_UNVERIFIED']
sill=min((G.matrix_world@v.co).z for v in G.data.vertices)
ltop=max((L.matrix_world@v.co).z for v in L.data.vertices)
print('sill',sill,'land_top',ltop)
# if landing much below sill, lift whole object
if sill-ltop>0.05:
    d=sill-0.01-ltop; L.location.z+=d; L['wf_dz']=round(float(L.get('wf_dz',0))+d,3); print('lift',d)
bpy.ops.wm.save_mainfile(); print('SAVED')
