import bpy, json
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get()
def rc(name,x,y):
    o=bpy.data.objects[name]; e=o.evaluated_get(dg); iw=o.matrix_world.inverted()
    r=e.ray_cast(iw@Vector((x,y,400)),(iw.to_3x3()@Vector((0,0,-1))).normalized())
    if not r[0]: return None
    n=(o.matrix_world.to_3x3()@r[2]).normalized(); return ((o.matrix_world@r[1]).z,n.z,r[3])
out=[]
for x in range(-80,202,4):
    ye=None
    for y10 in range(2300,2700,2):
        y=y10/10; h=rc('Terrain_LiDAR_DTM_1m',x,y)
        if h and h[1]>0.3: ye=(y,h[0])
    if not ye: out.append([x,None]); continue
    sk=[rc('Context_skirt_3DEP_ortho_4km',x,ye[0]+d) for d in (0.5,5,10,15,25)]
    qj=rc('QJ_NE_seam_fill_UNVERIFIED',x,ye[0]+1) if 'QJ_NE_seam_fill_UNVERIFIED' in bpy.data.objects else None
    qm=rc('QM_terrain_band_underlay_UNVERIFIED',x,ye[0]+1) if 'QM_terrain_band_underlay_UNVERIFIED' in bpy.data.objects else None
    out.append([x,round(ye[0],1),round(ye[1],2),[round(s[0]-ye[1],2) if s else None for s in sk],bool(qj),bool(qm)])
for r in out: print('EDGE',r)
o=bpy.data.objects['Context_skirt_3DEP_ortho_4km']; me=o.data
print('SKIRT uv',[u.name for u in me.uv_layers],'mats',[m.name for m in me.materials],'mods',[m.type+':'+m.name for m in o.modifiers],'verts',len(me.vertices))
import numpy as np
if me.uv_layers:
    for u in me.uv_layers:
        n=len(me.loops); uv=np.zeros(n*2); u.data.foreach_get('uv',uv); uv=uv.reshape(-1,2)
        vi=np.zeros(n,dtype=int); me.loops.foreach_get('vertex_index',vi)
        co=np.zeros(len(me.vertices)*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
        mw=np.array(o.matrix_world); P=co[vi]; P=(mw[:3,:3]@P.T).T+mw[:3,3]
        A=np.c_[P[:,0],P[:,1],np.ones(n)]; sol,res,_,_=np.linalg.lstsq(A,uv,rcond=None)
        err=np.abs(A@sol-uv).max(); print('UVFIT',u.name,sol.T.tolist(),'maxerr',err)
