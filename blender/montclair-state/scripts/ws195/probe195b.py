import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
for n in ('WS98_lotE_raised_concrete_walk_pad_LiDAR15cm_curb_ortho2020_UNV','WS99_lotE_padS_bed_MULCH_ortho2020_LiDARshrubs_UNVERIFIED','WS79_lot_E_patch_asphalt_ortho2020_UNVERIFIED_edges'):
    ob=bpy.data.objects[n]; bb=[ob.matrix_world@Vector(c) for c in ob.bound_box]; print('Q195',n[:30],'x',round(min(p.x for p in bb),1),round(max(p.x for p in bb),1),'y',round(min(p.y for p in bb),1),round(max(p.y for p in bb),1))
lots=[ob for ob in bpy.data.objects if ob.type=='MESH' and not ob.hide_render and any(ob.name.startswith(p) for p in ('WS74_cogen','WS75_sprague_lot_asphalt','WS76_accessible_lot_asphalt','WS80_sprague_lot_fill','WS79_lot_E_patch','WS98_lotE','WS99_lotE'))]
BV=[]
for ob in lots:
    mw=ob.matrix_world; BV.append((ob.name[:6],BVHTree.FromPolygons([mw@v.co for v in ob.data.vertices],[p.vertices[:] for p in ob.data.polygons])))
QX=np.load('/workspace/nj-scenes/montclair-state/scripts/ws195/outline195.npy')
o=bpy.data.objects['WS77_lot_median_island_MULCH_JOEphoto20261112_curb_ortho2020']

import sys; sys.path.insert(0,'/workspace/nj-scenes/montclair-state/scripts/ws91'); from straight91 import loops_of
W=np.array([tuple(o.matrix_world@v.co) for v in o.data.vertices]); F=[list(p.vertices) for p in o.data.polygons]
L=max(loops_of(F),key=len); OLD=W[L][:,:2]
def pip(P,x,y):
    xs,ys=P[:,0],P[:,1]; xj,yj=np.roll(xs,1),np.roll(ys,1)
    c=((ys>y)!=(yj>y))&(x<(xj-xs)*(y-ys)/(yj-ys+1e-12)+xs); return c.sum()%2==1
nin=0;miss=[];both=0
for x in np.arange(-257,-212,0.25):
    for y in np.arange(-96,-80,0.25):
        if pip(OLD,x,y) and not pip(QX,x,y):
            nin+=1; hit=[n for n,B in BV if B.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))[0]]
            if not hit: miss.append((round(x,2),round(y,2)))
        if pip(QX,x,y) and not pip(OLD,x,y): both+=1
print('Q195 old-not-new pts',nin,'no lot under',len(miss),miss[:40]); print('Q195 new-not-old pts',both)
np.save('/workspace/nj-scenes/montclair-state/scripts/ws195/old195.npy',W[L])
