# Fix floating W door landing/walk after LiDAR patch — re-drape more aggressively onto patch
import bpy, json, numpy as np, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
os.chdir('/workspace/nj-scenes/montclair-state')
dg=bpy.context.evaluated_depsgraph_get()
P=bpy.data.objects['WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED']
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']
Pe=P.evaluated_get(dg); pme=Pe.to_mesh()
bp=BVHTree.FromPolygons([P.matrix_world@v.co for v in pme.vertices],[tuple(p.vertices) for p in pme.polygons]); Pe.to_mesh_clear()
ske=sk.evaluated_get(dg); sme=ske.to_mesh()
bs=BVHTree.FromPolygons([sk.matrix_world@v.co for v in sme.vertices],[tuple(p.vertices) for p in sme.polygons]); ske.to_mesh_clear()
def gz(x,y):
    h=bp.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
    if h[0] is not None: return h[0].z,'patch'
    h=bs.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
    return (h[0].z,'skirt') if h[0] is not None else (None,None)

names=['WD_walk_1132693523_UNVERIFIED','TK_Bohn_landing_W_walk_UNVERIFIED','WD_walk_600258640_UNVERIFIED']
# also door-related thresholds
for nm in names:
    o=bpy.data.objects[nm]
    mw=o.matrix_world; V=[mw@v.co for v in o.data.vertices]
    dzs=[]
    for p in V:
        g,s=gz(p.x,p.y)
        if g is not None: dzs.append(g+0.05-p.z)
    print(nm,'n',len(V),'dz min/med/max',round(min(dzs),3),round(float(np.median(dzs)),3),round(max(dzs),3) if dzs else None)

# Re-drape: set every vert to ground+0.05 (walks) or ground+0.02 (landing), keep XY
bak={}
for nm, lift in [('WD_walk_1132693523_UNVERIFIED',0.05),('TK_Bohn_landing_W_walk_UNVERIFIED',0.02),('WD_walk_600258640_UNVERIFIED',0.05)]:
    o=bpy.data.objects[nm]
    n=len(o.data.vertices); co=np.zeros(n*3,np.float32); o.data.vertices.foreach_get('co',co); co=co.reshape(n,3)
    if nm not in bak and o.get('wf_drape') and os.path.exists('data/wf/drape_bak.npz'):
        # keep original bak from first pass
        pass
    M=np.array(o.matrix_world); W=co@M[:3,:3].T+M[:3,3]
    # save current as bak if not already from first session bak
    if not os.path.exists('data/wf/drape_bak.npz') or nm not in np.load('data/wf/drape_bak.npz').files:
        bak[nm]=co.copy()
    ok=0
    for i in range(n):
        g,s=gz(W[i,0],W[i,1])
        if g is None: continue
        W[i,2]=g+lift; ok+=1
    invR=np.linalg.inv(M[:3,:3]).T
    co2=(W-M[:3,3])@invR
    o.data.vertices.foreach_set('co',co2.astype(np.float32).ravel()); o.data.update(); o['wf_drape']=1
    print('REDAPE',nm,ok)

# Verify
for nm in names:
    o=bpy.data.objects[nm]
    mw=o.matrix_world; V=[mw@v.co for v in o.data.vertices]
    dzs=[(gz(p.x,p.y)[0]+0.05-p.z) for p in V if gz(p.x,p.y)[0] is not None]
    print('AFTER',nm,round(min(dzs),3),round(float(np.median(dzs)),3),round(max(dzs),3))

# Door sill vs landing
G=bpy.data.objects['TK_Bohn_door_glass_W_walk_UNVERIFIED']
gv=[G.matrix_world@v.co for v in G.data.vertices]
print('door glass z',round(min(p.z for p in gv),3),round(max(p.z for p in gv),3))
L=bpy.data.objects['TK_Bohn_landing_W_walk_UNVERIFIED']
lv=[L.matrix_world@v.co for v in L.data.vertices]
print('landing z',round(min(p.z for p in lv),3),round(max(p.z for p in lv),3))
# if landing top below door sill by >0.3, raise landing to meet sill-0.02
door_sill=min(p.z for p in gv)
land_top=max(p.z for p in lv)
print('door_sill',door_sill,'land_top',land_top,'gap',door_sill-land_top)
if door_sill-land_top > 0.15:
    # raise entire landing to meet door (keep relative)
    d=door_sill-0.02-land_top
    for v in L.data.vertices:
        # local z bump via world
        pass
    # simpler: location.z
    L.location.z += d; L['wf_dz']=round(float(L.get('wf_dz',0))+d,3)
    print('RAISED landing by',round(d,3))
    # also raise walk end near door
    w=bpy.data.objects['WD_walk_1132693523_UNVERIFIED']
    mw=w.matrix_world; inv=mw.inverted()
    for v in w.data.vertices:
        p=mw@v.co
        if p.x > 214:  # near door
            v.co=inv@Vector((p.x,p.y,p.z+d))
    w.data.update()
    print('raised walk end verts')

bpy.context.view_layer.update()
bpy.ops.wm.save_mainfile(); print('SAVED',len(bpy.data.objects))
json.dump({'door_sill':door_sill,'land_top':land_top},open('data/wf/walk_fix.json','w'))
