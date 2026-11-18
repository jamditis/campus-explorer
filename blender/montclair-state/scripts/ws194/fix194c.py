# ws194 WOBBLE #W4: Lot 3 S ramp S end -> Normal Ave W N sidewalk joint. probe194e.out: the asphalt S edge sits a steady
# 5 cm (W end 10 cm) BELOW the sidewalk all along the joint = a dark step line. A driveway apron meets the walk flush
# (ADA cross-walk at drive crossings; the 2020 ortho shows no curb line here, the depressed curb is at the carriageway).
# Fix: S-edge verts raised to sidewalk -0.5 cm, delta feathered over 1.5 m up the ramp; same delta applied to the WS193 W curb
# verts (keeps its taper flush) and to the lawn within 0.6 m E of the drive's E edge near the S end (no new lip).
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def _o(p):
    l=[o for o in bpy.data.objects if o.name.startswith(p)]; return l[0] if l else None
D=_o('WS163_Lot3_aisle_S_drive'); M=D.matrix_world; Mi=M.inverted()
SW=_o('WS163_NormalAve_W_N_sidewa'); Ms=SW.matrix_world
SB=BVHTree.FromPolygons([Ms@v.co for v in SW.data.vertices],[p.vertices[:] for p in SW.data.polygons])
W=np.array([tuple(M@v.co) for v in D.data.vertices])
bm=bmesh.new(); bm.from_mesh(D.data)
bidx=sorted({v.index for e in bm.edges if e.is_boundary for v in e.verts}); bm.free()
B=W[bidx]
ybot=lambda x: -248.66+(x+315.2)*(-2.27/9.6)
SE_=B[np.abs(B[:,1]-ybot(B[:,0]))<0.08]; SE_=SE_[np.argsort(SE_[:,0])]
dS=[]
for x,y,z in SE_:
    nx,ny=-0.2275,-0.9738  # outward (S) normal of the joint line
    h=SB.ray_cast(Vector((x+0.12*-nx*0+0.12*nx*-1*0+0.12*nx, y+0.12*ny,200)),Vector((0,0,-1)))
    dS.append(max(0.0,(h[0].z-0.005-z)) if h[0] else 0.0)
dS=np.array(dS); print('FIX194c S pts',len(SE_),'dz',np.round(dS,3).tolist(),flush=True)
def delta(x,y):
    d=ybot(x)-y  # negative inside the ramp (north of the joint)
    dist=-d
    if dist<-0.05 or dist>1.5: return 0.0
    t=max(0.0,dist)/1.5; f=1-t*t*(3-2*t)
    return f*float(np.interp(x,SE_[:,0],dS))
n=0
for v in D.data.vertices:
    p=M@v.co; dz=delta(p.x,p.y)
    if dz>0: p.z+=dz; v.co=Mi@p; n+=1
D.data.update()
C=_o('WS193_Lot3_S_ramp_W_curb'); Mc=C.matrix_world; Mci=Mc.inverted(); nc=0
for v in C.data.vertices:
    p=Mc@v.co; dz=delta(p.x+0.2,p.y)
    if dz>0: p.z+=dz; v.co=Mci@p; nc+=1
C.data.update()
En=lambda y: -305.45+0.0114*(y+236.0)
L=_o('WS163_ground_patch_W_of_WS110'); ML=L.matrix_world; MLi=ML.inverted(); nl=0
for v in L.data.vertices:
    p=ML@v.co
    if -251.2<p.y<-247.0:
        e=p.x-En(p.y)
        if 0<=e<0.6:
            dz=delta(En(p.y)-0.05,p.y)*(1-e/0.6)
            if dz>0: p.z+=dz; v.co=MLi@p; nl+=1
L.data.update()
print('FIX194c drive',n,'curb',nc,'lawn',nl,flush=True)
