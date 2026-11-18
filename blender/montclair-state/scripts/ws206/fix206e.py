# ws206 item 5: tiny dark mark at the WS70 gap-strip berm W tip (-256.3,-58.3) by the ws204 lot-entrance fill. map206 (0.2 m):
# the berm tip vertices sit ~2 cm BELOW the adjoining KY carriageway / WS204 fill, so the grass tip forms a small dark pit.
# Raise-only: WS70 verts within 1.0 m of the tip that are below the highest asphalt within 0.3 m are lifted to asphalt + 3 mm
# (smooth 1.0 m falloff of the lift); nothing else moves.
import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def ob(p): return [o for o in bpy.data.objects if o.name.startswith(p)][0]
def bvh(o):
    mw=o.matrix_world; return BVHTree.FromPolygons([mw@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
def hz(t,x,y):
    h=t.ray_cast(Vector((x,y,160)),Vector((0,0,-1)),80); return h[0].z if h[0] is not None else None
B=ob('WS70_gap_strip_grass_berms'); AT=[bvh(ob('KY_college_ave_carriageway_asphalt')),bvh(ob('WS204_CollegeAve_lot_entrance_asphalt_fill'))]
TX,TY=-256.3,-58.3; mw=B.matrix_world; mi=mw.inverted(); n=0; mx=0
for v in B.data.vertices:
    g=mw@v.co; d=((g.x-TX)**2+(g.y-TY)**2)**0.5
    if d>1.0: continue
    zs=[hz(t,g.x+dx,g.y+dy) for t in AT for dx,dy in ((0,0),(0.3,0),(-0.3,0),(0,0.3),(0,-0.3))]; zs=[z for z in zs if z is not None and abs(z-g.z)<0.1]
    if not zs: continue
    req=max(zs)+0.003-g.z
    if req>0:
        f=1-(d/1.0)**2; g.z+=req*max(f,0.35); mx=max(mx,req); v.co=mi@g; n+=1
B.data.update(); print('F206e berm tip verts raised',n,'max %.3f'%mx,flush=True)
