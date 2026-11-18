# ws133b: 1 m 2023-DTM lawn ground patch S/E of Russ where the evaluated Terrain has holes and only the coarse
# Context_skirt_3DEP_ortho_4km (smeared ortho) showed: x -133..-116.5 (stops W of the unmodelled dining-link roof), y -272..-249.5.
import bpy, bmesh, math, os, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SAVE=os.environ.get('SAVE','0')=='1'
D='/workspace/nj-scenes/montclair-state/scripts/'
P=np.load(D+'ws132/las132.npy'); G2=P[P[:,3]==2]
c=math.hypot(1,0.24); U=np.array([1,-0.24])/c; V=np.array([0.24,1])/c; O=np.array([-150.,-242.])
def ST(x,y): d=np.array([x,y])-O; return float(d@U),float(d@V)
def gzxy(x,y,r=1.5):
    d2=(G2[:,0]-x)**2+(G2[:,1]-y)**2; m=d2<r*r
    if m.sum()<4: m=d2<(2.5*r)**2
    w=1/(0.3+d2[m]); return float((G2[m,2]*w).sum()/w.sum())
R=[(-17,19,-7.25,7.3),(-23.8,-10.3,-11.55,11.8),(12,24.95,-11.65,11.75),(-31,-23,-6.1,6.6),(-23,-11.5,-14.5,-11),(13,24.1,-14.6,-11)]
def inb(x,y):
    s,t=ST(x,y); return any(r[0]-0.3<=s<=r[1]+0.3 and r[2]-0.3<=t<=r[3]+0.3 for r in R)
col=bpy.data.collections['WS133_Russ_E_side']
for o in [o for o in bpy.data.objects if o.name.startswith('WS133b_')]: bpy.data.objects.remove(o)
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']; bm=bmesh.new(); bm.from_mesh(sk.data); bm.transform(sk.matrix_world); TS=BVHTree.FromBMesh(bm); bm.free()
X=np.arange(-133,-116.5+1e-6,1.0); Y=np.arange(-272,-249.5+1e-6,0.5*1)  # 1 x 0.5 m
bm=bmesh.new(); vid={}; dz=[]
def v(i,j):
    if (i,j) not in vid:
        z=gzxy(X[i],Y[j])-0.01; vid[(i,j)]=bm.verts.new((float(X[i]),float(Y[j]),z))
        h=TS.ray_cast(Vector((float(X[i]),float(Y[j]),300)),Vector((0,0,-1)))
        if h[0]: dz.append(h[0].z-z)
    return vid[(i,j)]
for i in range(len(X)-1):
    for j in range(len(Y)-1):
        cx,cy=(X[i]+X[i+1])/2,(Y[j]+Y[j+1])/2
        if inb(cx,cy): continue
        bm.faces.new((v(i,j),v(i+1,j),v(i+1,j+1),v(i,j+1)))
me=bpy.data.meshes.new('WS133b_ground_patch_Russ_S_E_DTM2023_1m_lawn_UNVERIFIED'); bm.to_mesh(me); bm.free()
me.materials.append(bpy.data.materials['COLE_lawn_post2020_bs'])
o=bpy.data.objects.new(me.name,me); col.objects.link(o)
dz=np.array(dz); print('PATCH faces',len(me.polygons),'skirt-minus-patch dz min %.2f med %.2f max %.2f'%(dz.min(),np.median(dz),dz.max()))
# keep the walk above the patch everywhere (smoothing could dip it): lift any walk vert < patch+0.03
w=bpy.data.objects['WS133_Russ_E_walk_concrete_LiDAR2023int_UNVERIFIEDjoints']; n=0
for vv in w.data.vertices:
    p=w.matrix_world@vv.co; zg=gzxy(p.x,p.y)
    if p.z<zg+0.015 and vv.co.z>-1e9:
        # only top verts (skirt verts are 0.25 below their top twin; skip those by checking neighbours is costly) -> top verts are within 0.1 of ground
        if p.z>zg-0.1: vv.co.z+= (zg+0.025-p.z); n+=1
w.data.update(); print('WALK lifted',n)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
