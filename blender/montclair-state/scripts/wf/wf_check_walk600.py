import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import os; os.chdir('/workspace/nj-scenes/montclair-state')
dg=bpy.context.evaluated_depsgraph_get()
P=bpy.data.objects['WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED']
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']
Pe=P.evaluated_get(dg); pme=Pe.to_mesh()
bp=BVHTree.FromPolygons([P.matrix_world@v.co for v in pme.vertices],[tuple(p.vertices) for p in pme.polygons]); Pe.to_mesh_clear()
# restore walk600 from bak if available
bak=np.load('data/wf/drape_bak.npz')
print('bak files',bak.files)
w=bpy.data.objects['WD_walk_600258640_UNVERIFIED']
V=[w.matrix_world@v.co for v in w.data.vertices]
zs=sorted(p.z for p in V)
print('walk600 z min/p10/med/max',round(zs[0],3),round(zs[len(zs)//10],3),round(zs[len(zs)//2],3),round(zs[-1],3))
# how many below 130?
print('n z<130',sum(1 for z in zs if z<130),'n z<132',sum(1 for z in zs if z<132))
# restore from bak (pre-wf first drape original)
if 'WD_walk_600258640_UNVERIFIED' in bak.files:
    # bak is ORIGINAL pre-any-wf — then re-apply careful drape skipping hole
    co=bak['WD_walk_600258640_UNVERIFIED']
    w.data.vertices.foreach_set('co',co.ravel()); w.data.update()
    print('restored from bak')
M=np.array(w.matrix_world); n=len(w.data.vertices)
co=np.zeros(n*3,np.float32); w.data.vertices.foreach_get('co',co); co=co.reshape(n,3)
W=co@M[:3,:3].T+M[:3,3]
ok=0; skipped=0
for i in range(n):
    h=bp.ray_cast(Vector((W[i,0],W[i,1],400)),Vector((0,0,-1)))
    if h[0] is None: skipped+=1; continue
    g=h[0].z
    if g < 125: skipped+=1; continue  # hole / bad
    W[i,2]=g+0.05; ok+=1
invR=np.linalg.inv(M[:3,:3]).T
co2=(W-M[:3,3])@invR
w.data.vertices.foreach_set('co',co2.astype(np.float32).ravel()); w.data.update()
print('careful drape ok',ok,'skipped',skipped)
V=[w.matrix_world@v.co for v in w.data.vertices]
zs=sorted(p.z for p in V)
print('after z min/med/max',round(zs[0],3),round(zs[len(zs)//2],3),round(zs[-1],3))

# W walk + landing from bak too then careful
for nm,lift in [('WD_walk_1132693523_UNVERIFIED',0.05),('TK_Bohn_landing_W_walk_UNVERIFIED',0.02)]:
    if nm not in bak.files: print('no bak',nm); continue
    o=bpy.data.objects[nm]
    o.data.vertices.foreach_set('co',bak[nm].ravel()); o.data.update()
    M=np.array(o.matrix_world); n=len(o.data.vertices)
    co=np.zeros(n*3,np.float32); o.data.vertices.foreach_get('co',co); co=co.reshape(n,3)
    W=co@M[:3,:3].T+M[:3,3]
    ok=0
    for i in range(n):
        h=bp.ray_cast(Vector((W[i,0],W[i,1],400)),Vector((0,0,-1)))
        if h[0] is None: continue
        g=h[0].z
        if g<125: continue
        W[i,2]=g+lift; ok+=1
    invR=np.linalg.inv(M[:3,:3]).T
    co2=(W-M[:3,3])@invR
    o.data.vertices.foreach_set('co',co2.astype(np.float32).ravel()); o.data.update(); o['wf_drape']=1
    print('careful',nm,ok)

bpy.ops.wm.save_mainfile(); print('SAVED',len(bpy.data.objects))
