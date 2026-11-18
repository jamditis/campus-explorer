import bpy, bmesh, math, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OB=bpy.data.objects
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws164/fix164a.py').read().split('def ramp')[0].split('OB=bpy.data.objects',1)[1])
SL=0.236; dv=np.array([-1.0,SL]); dv/=np.linalg.norm(dv); nv=np.array([SL,1.0]); nv/=np.linalg.norm(nv); A0=np.array([-268.8,-262.9])
def npt(x): t=(A0[0]-x)/(-dv[0]); return A0+dv*t
def wb(x): return (npt(x)+nv*(0.18+3.2))[1]
def fdist(x,y): return float(np.dot(np.array([x,y])-(npt(x)+nv*(0.18+3.2)),nv))
def bvh(objs):
    V=[];F=[]
    for o in objs:
        b=len(V); V+=[o.matrix_world@v.co for v in o.data.vertices]; F+=[[b+i for i in p.vertices] for p in o.data.polygons]
    return BVHTree.FromPolygons(V,F)
def hz(T,x,y):
    h=T.ray_cast(Vector((x,y,300)),Vector((0,0,-1))); return h[0].z if h[0] is not None else None
walk=OB['WS163_NormalAve_W_N_sidewalk_3p2m_LiDAR2023_int_UNVERIFIED']; TW=bvh([walk])
def wz(x): return hz(TW,min(max(x,-305.3),-300.2),wb(min(max(x,-305.3),-300.2))-0.15)
XW,XE,YN,RC,CW=-305.45,-300.0,-248.8,1.0,0.15
xi0=XW+CW; yi1=YN-CW; cx,cy=XW+RC,YN-RC; ri=RC-CW
def inside(x,y):
    if x<xi0 or x>XE or y>yi1 or fdist(x,y)<0: return False
    if x<cx and y>cy and math.hypot(x-cx,y-cy)>ri: return False
    return True
