import bpy,numpy as np,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=bpy.data.objects
NS=['QW_DTM_north_edge_ramp_UNVERIFIED','RZ2_SC_LiDAR_ground_patch_UNVERIFIED','SA_ground_lower_patch_UNVERIFIED','WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED','WT_richardson_west_LiDAR_patch_UNVERIFIED']
lib='/workspace/nj-scenes/montclair-state/montclair_state_pre_20261109wh.blend'
mn={n:O[n].data.name for n in NS}
with bpy.data.libraries.load(lib,link=True) as (a,b): b.meshes=list(mn.values())
PM={n:[m for m in b.meshes if m.name==mn[n]][0] for n in NS}
def bv(o,me): mw=o.matrix_world; return BVHTree.FromPolygons([mw@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons])
CUR={n:bv(O[n],O[n].data) for n in NS}; PRE={n:bv(O[n],PM[n]) for n in NS}
def hz(B,x,y):
    h=B.ray_cast(Vector((x,y,500)),Vector((0,0,-1))); return None if h[0] is None else h[0].z
tot=0
for n in NS:
    o=O[n]; mw=o.matrix_world; mi=mw.inverted(); k=0
    for i,v in enumerate(o.data.vertices):
        p0=PM[n].vertices[i].co
        if abs(v.co.z-p0.z)<1e-5: continue
        c=mw@v.co; c0=mw@p0
        for m in NS:
            if m==n: continue
            zc=hz(CUR[m],c.x,c.y)
            if zc is None or abs(zc-c.z)>0.006: continue
            zp=hz(PRE[m],c.x,c.y)
            if zp is not None and zp>c0.z+1e-4:   # other sheet was on top before: tuck under it
                nz=max(c0.z,zc-0.015)
                if nz<c.z: c.z=nz; v.co=mi@c; k+=1
    o.data.update(); tot+=k; print('TUCK',n,k,flush=True)
print('TOTAL',tot)
if '--save' in sys.argv:
    for m in list(b.meshes): pass
    import os
    for L in [l for l in bpy.data.libraries if os.path.basename(l.filepath)=='montclair_state_pre_20261109wh.blend']: bpy.data.libraries.remove(L)
    bpy.ops.wm.save_mainfile(); print('SAVED',len(O),len(bpy.data.libraries),flush=True)
