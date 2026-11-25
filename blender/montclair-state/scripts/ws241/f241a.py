# W58 (ws241): NJ Transit deck vs M3a ground. probe241a: inside the deck footprint M3a is a flat 106.71 pad (LiDAR DTM
# no-data fill under the building) 1.4-3.3 m under the deck's lowest slabs (108.7 / 110.0-110.3), seen as a black pit at the
# deck's W corner; along the S/W faces the DTM stands 110.4-111.4, i.e. 0.1-1.1 m over the 110.0 slab edge (ground climbing
# over the lowest level). Design read: the lowest level is (near) at grade on the S/W side (the DTM 1-3 m from the wall is
# smoothed); grade the ground to the slab at the wall. Changes M3a base verts only (no paving, deck untouched):
#  - inside the footprint: z = lowest deck hit above - 0.05 (raises the pad; lowers any ground poking through the slab)
#  - outside, within 1.5 m of the footprint: lowered to slab TOP - 0.15 (0.15 m slab-edge reveal) where higher; feathered back to LiDAR over 1.5-6 m.
# Max lowering capped at 1.5 m. Level-to-grade relation UNVERIFIED (no public photo of the S face found).
import bpy, math
import numpy as np
from mathutils import Vector, kdtree
from mathutils.bvhtree import BVHTree
dk=bpy.data.objects['NJ Transit Deck']; M=dk.matrix_world
DB=BVHTree.FromPolygons([M@v.co for v in dk.data.vertices],[p.vertices[:] for p in dk.data.polygons])
w=[M@Vector(c) for c in dk.bound_box]
X0,X1=min(v.x for v in w)-8,max(v.x for v in w)+8; Y0,Y1=min(v.y for v in w)-8,max(v.y for v in w)+8
def up2(x,y):
    h=DB.ray_cast(Vector((x,y,100.0)),Vector((0,0,1)),30.0)
    if h[0] is None or h[0].z>=112.0: return None
    h2=DB.ray_cast(h[0]+Vector((0,0,0.01)),Vector((0,0,1)),0.8)
    return (h[0].z, h2[0].z if h2[0] is not None else h[0].z)
def up(x,y):
    r=up2(x,y); return r[0] if r else None
cells=[]
for i in range(int(X1-X0)+1):
    for j in range(int(Y1-Y0)+1):
        x=X0+i+0.5; y=Y0+j+0.5; r=up2(x,y)
        if r is not None: cells.append((x,y,r[1]))
kd=kdtree.KDTree(len(cells))
for k,(x,y,z) in enumerate(cells): kd.insert((x,y,0),k)
kd.balance()
print('F241A footprint cells',len(cells),'slab top z range',round(min(c[2] for c in cells),2),round(max(c[2] for c in cells),2),flush=True)
g=bpy.data.objects['M3a_north_LiDAR_DTM_1m_ext_y515_UNVERIFIED_seam']; G=g.matrix_world; Gi=G.inverted()
me=g.data; n=len(me.vertices); co=np.empty(n*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
st={'pad_raised':0,'inside_lowered':0,'band_lowered':0,'maxup':0.0,'maxdn':0.0}
for k in range(n):
    p=G@Vector(co[k])
    if not (X0<=p.x<=X1 and Y0<=p.y<=Y1): continue
    s=up(p.x,p.y)
    if s is not None:
        t=s-0.05
        if p.z<t-0.01: st['pad_raised']+=1; st['maxup']=max(st['maxup'],t-p.z); p.z=t
        elif p.z>t+0.01 and p.z-t<=1.5: st['inside_lowered']+=1; st['maxdn']=max(st['maxdn'],p.z-t); p.z=t
        else: continue
    else:
        (c,idx,d)=kd.find((p.x,p.y,0))
        d=max(0.0,d-0.5)
        if d>6.0: continue
        t=cells[idx][2]-0.15
        if p.z<=t+0.01 or p.z-t>1.5: continue
        wgt=0.0 if d<=1.5 else min(1.0,(d-1.5)/4.5); wgt=wgt*wgt*(3-2*wgt)
        nz=t+(p.z-t)*wgt
        if p.z-nz<0.01: continue
        st['band_lowered']+=1; st['maxdn']=max(st['maxdn'],p.z-nz); p.z=nz
    co[k]=tuple(Gi@p)
me.vertices.foreach_set('co',co.ravel()); me.update()
print('F241A',{k:(round(v,2) if isinstance(v,float) else v) for k,v in st.items()},flush=True)
