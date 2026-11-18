# ws205 W22 follow-up: thin dark slit where the ws204 lot-entrance fill meets KY carriageway at the top of the ladder.
# Cause: the fill was tucked 4 mm UNDER KY, so KY's stair-stepped S boundary (0.1-0.4 m teeth, x -260..-256, y -57..-59.3)
# still drew a dark line over the fill. Fix: lift fill verts lying under KY to KY+3 mm (same asphalt material) with a smooth
# 0.6 m cone taper outside, capped 4 mm under every other surface (berm, paint, lots), so the visible seam becomes the
# fill's own straight N/W edges; ws204 paint bars re-seated 7 mm over the lifted fill.
import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def ob(p): return [o for o in bpy.data.objects if o.name.startswith(p)][0]
def bvh(o):
    mw=o.matrix_world; return BVHTree.FromPolygons([mw@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
def hz(t,x,y):
    h=t.ray_cast(Vector((x,y,150)),Vector((0,0,-1)),60); return h[0].z if h[0] is not None else None
F=ob('WS204_CollegeAve_lot_entrance_asphalt_fill'); KY=ob('KY_college_ave_carriageway_asphalt'); PB=ob('WS204_lot_entrance_crosswalk_paint')
TK=bvh(KY)
OTHN=['WS74_cogen_lot_asphalt','WS76_accessible_lot_asphalt','WS70_gap_strip_grass_berms','WS67_CollegeAve_gap_asphalt','ey_rhd_se_crosswalks','WS76_lot_zebra_walkway_paint','WS76_lot_stall_paint_white','WS69_CollegeAve_gap_strip_curbs','KX_drive_apron','LH_college_ave_gutter_asphalt_fill']
OT=[bvh(ob(n)) for n in OTHN]
mw=F.matrix_world; mi=mw.inverted(); P=np.array([tuple(mw@v.co) for v in F.data.vertices])
req=np.zeros(len(P))
for k,p in enumerate(P):
    zk=hz(TK,p[0],p[1])
    if zk is not None and zk+0.003>p[2] and zk+0.003-p[2]<0.02: req[k]=zk+0.003-p[2]
idx=np.where(req>0)[0]; print('F205b verts under KY',len(idx),'max lift %.4f'%(req.max() if len(idx) else 0),flush=True)
new=P[:,2].copy(); nl=0
for k,p in enumerate(P):
    if len(idx)==0: break
    d=np.sqrt(((P[idx,:2]-p[:2])**2).sum(1)); f=np.clip(1-d/0.6,0,1); lift=float((req[idx]*f).max())
    if lift<=0: continue
    z=p[2]+lift
    zk=hz(TK,p[0],p[1])
    for t in OT:
        zo=hz(t,p[0],p[1])
        if zo is not None and zo<z+0.004: z=max(p[2],zo-0.004)
    if zk is not None: z=max(z,zk+0.003) if all((hz(t,p[0],p[1]) is None) or hz(t,p[0],p[1])>zk+0.008 for t in OT) else z
    new[k]=z; nl+=1
for k,v in enumerate(F.data.vertices):
    g=mw@v.co; g.z=new[k]; v.co=mi@g
F.data.update(); print('F205b fill verts lifted',nl,flush=True)
TF=bvh(F); pm=PB.matrix_world; pi=pm.inverted(); np_=0
for v in PB.data.vertices:
    g=pm@v.co; zf=hz(TF,g.x,g.y)
    if zf is not None and g.z<zf+0.007: g.z=zf+0.007; v.co=pi@g; np_+=1
PB.data.update(); print('F205b paint verts reseated',np_,flush=True)
