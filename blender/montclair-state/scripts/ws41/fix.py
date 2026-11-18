import bpy,bmesh,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def repair(name,box,R=2.5,tol=0.05,it=3):
    o=bpy.data.objects[name]; mw=o.matrix_world; mi=mw.inverted()
    W=np.array([tuple(mw@v.co) for v in o.data.vertices]); x0,x1,y0,y1=box
    sel=np.where((W[:,0]>x0)&(W[:,0]<x1)&(W[:,1]>y0)&(W[:,1]<y1))[0]; tot=0
    for k in range(it):
        ch=0; Z=W[:,2].copy()
        for i in sel:
            d=np.hypot(W[:,0]-W[i,0],W[:,1]-W[i,1]); nb=np.where((d<R)&(d>0.05))[0]
            if len(nb)<6: continue
            A=np.c_[np.ones(len(nb)),W[nb,0]-W[i,0],W[nb,1]-W[i,1]]
            wts=1/(0.3+d[nb]); 
            # robust: drop worst 25% residuals of initial fit
            c,*_=np.linalg.lstsq(A*wts[:,None],Z[nb]*wts,rcond=None); r=np.abs(A@c-Z[nb]); keep=r<=np.percentile(r,75)
            c,*_=np.linalg.lstsq(A[keep]*wts[keep,None],Z[nb][keep]*wts[keep],rcond=None)
            if abs(Z[i]-c[0])>tol: W[i,2]=c[0]; ch+=1
        tot+=ch; print('F41',name,'iter',k,'changed',ch)
        if ch==0: break
    for i in sel: o.data.vertices[i].co=mi@Vector(W[i])
    o.data.update(); return tot
BOX=(-206,-186,-108,-76)
repair('WS27_CollegeAve_carriageway_2020ortho',BOX)
pass
dg=bpy.context.evaluated_depsgraph_get()
def tree(n):
    o=bpy.data.objects[n]; bm=bmesh.new(); bm.from_mesh(o.evaluated_get(dg).to_mesh()); bm.transform(o.matrix_world); return BVHTree.FromBMesh(bm)
TT=[(tree('WS27_CollegeAve_carriageway_2020ortho'),0.08),(tree('WS27_CollegeAve_curb_right_UNVERIFIED'),0.10),(tree('WS27_CollegeAve_curb_left_UNVERIFIED'),0.10)]
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; mw=t.matrix_world; mi=mw.inverted(); n=0
for v in t.data.vertices:
    w=mw@v.co
    if not (BOX[0]-3<w.x<BOX[1]+3 and BOX[2]-3<w.y<BOX[3]+3): continue
    best=None
    for T,off in TT:
        for dx,dy in ((0,0),(0.5,0),(-0.5,0),(0,0.5),(0,-0.5)):
            r=T.ray_cast(Vector((w.x+dx,w.y+dy,w.z+5)),Vector((0,0,-1)),20)
            if r[0]: z=r[0].z-off; best=z if best is None else min(best,z)
    if best is not None and w.z>best: w.z=best; v.co=mi@w; n+=1
t.data.update(); print('F41 terrain seated',n)
tr=bpy.data.objects['T_RedMaple_L1_0235']
tr.hide_render=True; tr.hide_viewport=True; tr.name='T_RedMaple_L1_0235_HIDDEN_ws41_on_sidewalk_conflicts_Joe_1018'
print('F41 tree hidden')
bpy.ops.wm.save_mainfile()
