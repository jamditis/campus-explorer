# m2c241 follow-up 2 (ws241): after f241g, M3a 1 m faces that straddle the Lot 28S / Ice Arena paving edge still poke
# through it where the ground rises beyond the edge (bank at the lot's W side, up to 0.38 m). M3a verts within 1.2 m
# OUTSIDE a paving edge: z = min(z, nearest paving z - 0.06) (narrow shoulder, then the LiDAR bank resumes). Paving untouched.
import bpy, math
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
PV=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('KP IceArena SSW drive-aisle','KP IceArena SSW walk','KQ Lot 28S asphalt'))]
g=bpy.data.objects['M3a_north_LiDAR_DTM_1m_ext_y515_UNVERIFIED_seam']; G=g.matrix_world; Gi=G.inverted()
me=g.data; n=len(me.vertices); co=np.empty(n*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
DIRS=[(math.cos(a*math.pi/8),math.sin(a*math.pi/8)) for a in range(16)]
tot=0; mx=0
for o in PV:
    M=o.matrix_world; T=BVHTree.FromPolygons([M@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons])
    cs=[M@Vector(c) for c in o.bound_box]; x0=min(c.x for c in cs)-1.3; x1=max(c.x for c in cs)+1.3; y0=min(c.y for c in cs)-1.3; y1=max(c.y for c in cs)+1.3
    k=0
    for i in range(n):
        p=G@Vector(co[i])
        if not (x0<=p.x<=x1 and y0<=p.y<=y1): continue
        if T.ray_cast(Vector((p.x,p.y,p.z+3)),Vector((0,0,-1)),6)[0] is not None: continue
        best=None
        for r in (0.4,0.8,1.2):
            for dx,dy in DIRS:
                h=T.ray_cast(Vector((p.x+dx*r,p.y+dy*r,p.z+3)),Vector((0,0,-1)),6)
                if h[0] is not None and (best is None or h[0].z<best): best=h[0].z
            if best is not None: break
        if best is None: continue
        t=best-0.06
        if p.z>t and p.z-t<0.8:
            mx=max(mx,p.z-t); p.z=t; co[i]=tuple(Gi@p); k+=1
    tot+=k; print('F241H shoulder verts',o.name[:30],k,flush=True)
me.vertices.foreach_set('co',co.ravel()); me.update()
print('F241H total',tot,'max',round(mx,2),flush=True)
