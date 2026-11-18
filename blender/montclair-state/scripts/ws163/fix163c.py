# ws163c: lawn lip ribbons behind the new Normal Ave walks (walk back edge -> +1.4 m onto the LiDAR ground) to cover the saw-tooth where the
# 1 m WS110 ground patch was pushed under the walk (eye view from the E walk showed dark shards at the walk back edge).
import bpy, bmesh, os, math, numpy as np
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws163/main163.py').read().split("for o in [o for o in OB if o.name.startswith('WS163_')]")[0])
SL=0.236; dv=np.array([-1.0,SL]); dv/=np.linalg.norm(dv); nv=np.array([SL,1.0]); nv/=np.linalg.norm(nv); A0=np.array([-268.8,-262.9]); WROAD=11.3
def npt(x): t=(A0[0]-x)/(-dv[0]); return A0+dv*t
col=bpy.data.collections['WS163_NormalAve_W_LotS']
for n in [o.name for o in col.objects if o.name.startswith('WS163_walk_back_lawn_lip')]: OB.remove(OB[n])
walks={1:OB['WS163_NormalAve_W_N_sidewalk_3p2m_LiDAR2023_int_UNVERIFIED'],-1:OB['WS163_NormalAve_W_S_sidewalk_1p6m_UNVERIFIED']}
from mathutils.bvhtree import BVHTree
from mathutils import Vector
lawn=bpy.data.materials.get('COLE_lawn_post2020_bs')
for side,w in ((1,3.2),(-1,1.6)):
    wo=walks[side]; T=BVHTree.FromPolygons([wo.matrix_world@v.co for v in wo.data.vertices],[p.vertices for p in wo.data.polygons])
    bm=bmesh.new(); rows=[]
    for x in np.arange(-269.6,-346.01,-0.75):
        if side>0 and -316.0<=x<=-304.8: rows.append(None); continue    # drive mouth
        base=(npt(x) if side>0 else npt(x)-nv*WROAD)+nv*side*(0.18+w)
        h=T.ray_cast(Vector((base[0]-nv[0]*side*0.05,base[1]-nv[1]*side*0.05,300)),Vector((0,0,-1)))
        ze=h[0].z if h[0] is not None else dz(*base)+0.04
        r=[]
        for s_,fr in ((0.0,0),(0.5,0.45),(1.4,1.0)):
            q=base+nv*side*s_; zg=dz(*q)+0.03; z=ze-0.005 if s_==0 else ze+(max(zg,ze-0.25)-ze)*fr
            if s_==1.4: z=max(zg,ze-0.25)
            r.append(bm.verts.new((q[0],q[1],z)))
        rows.append(r)
    for i in range(len(rows)-1):
        if rows[i] is None or rows[i+1] is None: continue
        for j in range(2): bm.faces.new((rows[i][j],rows[i][j+1],rows[i+1][j+1],rows[i+1][j]))
    for f in bm.faces:
        f.normal_update()
        if f.normal.z<0: f.normal_flip()
    nm='WS163_walk_back_lawn_lip_%s_UNVERIFIED'%('N' if side>0 else 'S')
    me=bpy.data.meshes.new(nm); bm.to_mesh(me); bm.free(); me.materials.append(lawn)
    uv=me.uv_layers.new(name='UVMap')
    for lp in me.loops:
        p=me.vertices[lp.vertex_index].co; uv.data[lp.index].uv=(p.x*0.25,p.y*0.25)
    col.objects.link(OB.new(nm,me)); print('LIP',nm,len(me.polygons))
if OUT: bpy.ops.wm.save_as_mainfile(filepath=OUT,copy=True); print('SAVED',OUT)
