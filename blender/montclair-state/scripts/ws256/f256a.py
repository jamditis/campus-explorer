# ws256a: Feliciano E walk/paving junction with the OSM E-W path (y ~188.4..191).
# probe256b: the OSM path (Footpaths_OSM, evaluated drape) crosses the walk's N end with a smooth 8 % cross-fall
# (139.00 at x -193 -> 138.80 at x -190.5, following the 2023 LiDAR swale), but the ws255 wall-foot paving's N end stood at
# 138.96..138.99 (ground under the eave + 3 cm) while its E edge and the ws254 walk extension stayed at 138.78 -> a 20 cm fold
# over ~0.9 m (the pale wedge / lump seen from the N), and the extension's W edge sat 12 cm under the OSM path edge.
# Fix: blend the N 2.5 m of the paving and the extension (top + skirt verts together) to the OSM path's own profile at
# y 191 (table from probe256b, -5 mm), smoothstep in y; the extension follows too (its E half stood 4 cm over the path's S edge). Ground verts (terrain + W63 patches)
# under the paving's N end that would poke are lowered to the new paving - 5 cm (interpolated under-eave ground, as ws255b).
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
TAG='F256A'
def inner(y): return -194.69+0.0615*(y-172.0)
FPX=[-194.0,-193.0,-192.5,-192.0,-191.5,-191.0,-190.5,-190.0,-189.5,-189.0,-188.5]
FPZ=[138.990,138.990,138.956,138.907,138.850,138.819,138.803,138.803,138.825,138.877,138.935]
def zfp(x): return float(np.interp(x,FPX,FPZ))-0.005
Y0,Y1=188.4,190.95
def t_of(y,y0=Y0,y1=Y1):
    u=min(1.0,max(0.0,(y-y0)/(y1-y0))); return u*u*(3-2*u)
def blend(n,raise_only,y1=Y1,off=0.0):
    o=bpy.data.objects[n]; M=o.matrix_world; Mi=M.inverted(); me=o.data
    W=[M@v.co for v in me.vertices]; grp={}
    for i,w in enumerate(W): grp.setdefault((round(w.x,2),round(w.y,2)),[]).append(i)
    k=0; dmax=0; dmin=0
    for key,ids in grp.items():
        x,y=key; t=t_of(y,Y0,y1)
        if t<=0: continue
        zt=max(W[i].z for i in ids); d=t*(zfp(x)-off-zt)
        if raise_only and d<0: d=0
        if abs(d)<1e-4: continue
        for i in ids: me.vertices[i].co=Mi@Vector((W[i].x,W[i].y,W[i].z+d))
        k+=1; dmax=max(dmax,d); dmin=min(dmin,d)
    me.update(); print(TAG,n[:44],'columns moved',k,'d %.3f..%.3f'%(dmin,dmax),flush=True)
# the extension is a 2-column slab (x -191.98 / -189.5): slice it along x so its top can follow the path's curved swale
eo=bpy.data.objects['WS254_W63e_Feliciano_E_walk_N_extension_to_OSM_walk_UNVERIFIED']; bm=bmesh.new(); bm.from_mesh(eo.data)
Mi=eo.matrix_world.inverted()
for xc in (-191.5,-191.0,-190.5,-190.0):
    co=Mi@Vector((xc,0,0)); no=(Mi.to_3x3()@Vector((1,0,0))).normalized()
    bmesh.ops.bisect_plane(bm,geom=bm.verts[:]+bm.edges[:]+bm.faces[:],plane_co=co,plane_no=no)
bm.to_mesh(eo.data); bm.free(); eo.data.update(); print(TAG,'ext sliced verts',len(eo.data.vertices),flush=True)
blend('WS255_W63f_Feliciano_E_wall_foot_paving_to_wall_UNVERIFIED',False)
blend('WS254_W63e_Feliciano_E_walk_N_extension_to_OSM_walk_UNVERIFIED',False,190.6,0.015)  # reach the path level by y 190.6 (path S edge 190.75..190.85), 1.5 cm under it
def bvo(n):
    o=bpy.data.objects[n]; M=o.matrix_world; vs=[M@v.co for v in o.data.vertices]
    ps=[p.vertices[:] for p in o.data.polygons if p.normal.z>0.3 or True]
    return BVHTree.FromPolygons(vs,ps)
PV=[bvo('WS255_W63f_Feliciano_E_wall_foot_paving_to_wall_UNVERIFIED'),bvo('WS254_W63e_Feliciano_E_walk_N_extension_to_OSM_walk_UNVERIFIED')]
def ptop(x,y):
    z=-1e9
    for b in PV:
        h=b.ray_cast(Vector((x,y,300)),Vector((0,0,-1)),400)
        if h[0]: z=max(z,h[0].z)
    return z
for gnm in ('Terrain_LiDAR_DTM_1m','WS250_W63_lawn_LiDAR2023_ground_patch_1m','WS251_W63b_passage_LiDAR2023_ground_patch_1m'):
    go=bpy.data.objects.get(gnm)
    if not go: continue
    Mg=go.matrix_world; Mgi=Mg.inverted(); k=0; dm=0
    for v in go.data.vertices:
        w=Mg@v.co
        if 188.0<=w.y<=190.95 and inner(w.y)+0.05<=w.x<=-189.2:
            pz=min(ptop(w.x+dx,w.y+dy) for dx in (-0.3,0,0.3) for dy in (-0.3,0,0.3))
            if pz<-1e8: continue
            lim=pz-0.05
            if w.z>lim: dm=max(dm,w.z-lim); v.co=Mgi@Vector((w.x,w.y,lim)); k+=1
    go.data.update(); print(TAG,'ground lowered',gnm,k,'max %.3f'%dm,flush=True)
for y in (188.4,189.4,190.2,190.9):
    print(TAG,'paving/ext top y%.1f'%y,' '.join('%.3f'%ptop(x,y) for x in (-193.4,-193.0,-192.5,-192.0,-191.5,-191.0,-190.5,-190.0)),flush=True)
