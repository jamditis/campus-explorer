# ws199 W16c (after fix199b): (1) blue-square paint spike at ISA3 NW corner (-238.4,-80.1) +43 mm -> paint re-seated at asphalt+15 mm (flush rule)
# (2) dip/gap E of ISA3 (x -236.8..-235.8, y -81.6..-80.8): AS verts 0.5-5 cm under the fitted plane lifted to it (raise-only);
#     remaining slit covered by a thin flat asphalt patch 3 mm under the plane (WS76 material) so no underlay/terrain shows.
import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
AS=['WS75_sprague_lot_asphalt_ortho2020_UNVERIFIED_edges','WS76_accessible_lot_asphalt_ortho2020_UNVERIFIED_edges','WS94_lot_slit_filler_asphalt_UNVERIFIED']
k2=0
for n in AS:
    o=bpy.data.objects[n]; mw=o.matrix_world; mi=mw.inverted()
    for v in o.data.vertices:
        w=mw@v.co
        if wt(w.x,w.y)>=1:
            t=pl(w.x,w.y)
            if t-0.05<w.z<t-0.005: w.z=t; v.co=mi@w; k2+=1
    o.data.update()
print('F199c AS dip verts lifted',k2,flush=True)
V=[];F=[]
for n in AS:
    o=bpy.data.objects[n]; mw=o.matrix_world; b=len(V)
    V+=[mw@v.co for v in o.data.vertices]; F+=[tuple(b+i for i in p.vertices) for p in o.data.polygons]
NT=BVHTree.FromPolygons(V,F)
def zt2(x,y):
    h=NT.ray_cast(Vector((x,y,300)),Vector((0,0,-1))); return h[0].z if h[0] else None
kp=0
for nm in ('WS76_lot_stall_paint_blue_accessible_ortho2020_UNVERIFIED','WS196_lot_accessible_ISA_symbol_paint_UNVERIFIED'):
    o=bpy.data.objects[nm]; mw=o.matrix_world; mi=mw.inverted(); want=0.015 if 'blue' in nm else 0.0225
    for v in o.data.vertices:
        w=mw@v.co
        if wt(w.x,w.y)<=0: continue
        za=zt2(w.x,w.y)
        if za is None: continue
        d=w.z-za
        if d>want+0.006 and d<0.15: w.z=za+want; v.co=mi@w; kp+=1
        elif d<want-0.006 and d>-0.06: w.z=za+want; v.co=mi@w; kp+=1
    o.data.update()
print('F199c paint verts re-seated',kp,flush=True)
x0,x1,y0,y1=-236.9,-235.7,-81.7,-80.7
me=bpy.data.meshes.new('WS199_lot_gap_patch_asphalt')
nx,ny=7,6; vs=[]
for j in range(ny):
    for i in range(nx):
        x=x0+(x1-x0)*i/(nx-1); y=y0+(y1-y0)*j/(ny-1); vs.append((x,y,pl(x,y)-0.003))
fs=[(j*nx+i,j*nx+i+1,(j+1)*nx+i+1,(j+1)*nx+i) for j in range(ny-1) for i in range(nx-1)]
me.from_pydata(vs,[],fs); me.update()
src=bpy.data.objects['WS76_accessible_lot_asphalt_ortho2020_UNVERIFIED_edges']
for m in src.data.materials: me.materials.append(m)
ob=bpy.data.objects.new('WS199_lot_gap_patch_asphalt_UNVERIFIED',me)
for c in src.users_collection: c.objects.link(ob)
print('F199c gap patch added',len(vs),flush=True)
