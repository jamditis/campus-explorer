# ws197 W14 follow-up: ISA symbols in row B (south row, entered from the shared drive aisle to its NORTH) rotated 180 deg in
# place (about each glyph's bbox centre in the stall frame) so they read upright to a driver entering from the aisle; row A
# (north row, entered from the aisle to its south) already upright. Re-draped: each vertex keeps its ws196 offset above the
# top-most asphalt (+2.2 cm + layer step).
import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
lots=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_render and any(o.name.startswith(p) for p in ('WS74_cogen_lot_asphalt','WS75_sprague_lot_asphalt','WS76_accessible_lot_asphalt','WS80_sprague_lot_fill','WS79_lot_E_patch'))]
TR=[BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(f.vertices) for f in o.data.polygons]) for o in lots]
def zat(x,y):
    b=None
    for T in TR:
        h=T.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))
        if h[0] and (b is None or h[0].z>b): b=h[0].z
    return b
I=bpy.data.objects['WS196_lot_accessible_ISA_symbol_paint_UNVERIFIED']; mw=I.matrix_world; mi=mw.inverted()
V=I.data.vertices; n=len(V)//18; assert len(V)==18*n
W=np.array([tuple(mw@v.co) for v in V])
cen=W[:,:2].reshape(18,n,2).mean(1)
t=cen[8]-cen[0]; t/=np.linalg.norm(t); up=np.array((-t[1],t[0]))
dzs=[];miss=0
for s in range(9,18):
    SB=W[s*n:(s+1)*n]; Q=SB[:,:2]
    a=Q@t; b=Q@up; c=t*(a.min()+a.max())/2+up*(b.min()+b.max())/2
    for k in range(n):
        i=s*n+k; x,y,z=W[i]; z0=zat(x,y); off=(z-z0) if z0 is not None else 0.022
        nx,ny=2*c-np.array((x,y)); z1=zat(nx,ny)
        if z1 is None: miss+=1; z1=z0 if z0 is not None else z-0.022
        V[i].co=mi@Vector((nx,ny,z1+off)); dzs.append(off)
I.data.update()
print('F197 rotated row B symbols 9..17, verts',9*n,'miss',miss,'offset min %.4f max %.4f'%(min(dzs),max(dzs)),flush=True)
