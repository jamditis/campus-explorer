# ws255b: (1) rebuild the W63f wall-foot strip with denser rows (0.25 m) and clearance over the ground max in a +-0.2 m x / +-0.3 m y
# neighbourhood + 3 cm (ws255a test: terrain crease rows at y 182.0 / 190.0 poked through as dark spots at the stair top);
# (2) base terrain verts along Feliciano's E wall foot N of the strip (y 190.6..199.5, from 4 m inside the wall line to 0.4 m out)
# lifted to the ground 0.9 m east of the wall minus 3 cm (ws255a eye-from-N test: dark notches every ~2 m at the wall foot; probe255d
# pits 0.4-1.1 m deep at offsets -0.05..0.3 m).
# (3) ground verts (terrain + W63 patches) under the strip box (x wall-1.2..-192.0, y 179.3..190.4) lowered to <= walk level - 6 cm:
# there are no LiDAR ground returns under the eave, so that ground was interpolated and stood 0.2-0.4 m above the walk at the wall;
# a 1st ws255b build draped on it put a 26 cm step at the walk's W edge (y 181.2). Neighbouring triangles fall under the walk (E) or
# inside the building (W).
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
TAG='F255B'
def inner(y): return -194.69+0.0615*(y-172.0)
def bvo(n):
    o=bpy.data.objects.get(n)
    if not o: print(TAG,'MISSING',n,flush=True); return None
    M=o.matrix_world; me=o.data; vs=[M@v.co for v in me.vertices]
    ps=[p.vertices[:] for p in me.polygons if any(-200<vs[i].x<-186 and 165<vs[i].y<202 for i in p.vertices)]
    return BVHTree.FromPolygons(vs,ps) if ps else None
def zmax(bl,x,y):
    z=-1e9
    for b in bl:
        h=b.ray_cast(Vector((x,y,300)),Vector((0,0,-1)),400)
        if h[0]: z=max(z,h[0].z)
    return z
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']
# (2) terrain lift first
TB=bvo('Terrain_LiDAR_DTM_1m'); M=T.matrix_world; Mi=M.inverted(); me=T.data; n=0; mx=0
for v in me.vertices:
    w=M@v.co
    if 190.6<w.y<199.5 and inner(w.y)-4.0<w.x<inner(w.y)+0.4:
        ref=zmax([TB],inner(w.y)+0.9,w.y)-0.03
        if ref>-1e8 and w.z<ref:
            mx=max(mx,ref-w.z); w2=Vector((w.x,w.y,ref)); v.co=Mi@w2; n+=1
me.update(); print(TAG,'terrain verts lifted',n,'max %.2f'%mx,flush=True)
WK0=[b for b in map(bvo,['WS253_W63d_Feliciano_E_walk_slabs','WS253_W63d_Feliciano_E_walk_and_stairs_UNVERIFIED','WS254_W63e_Feliciano_E_walk_N_extension_to_OSM_walk_UNVERIFIED']) if b]
for gnm in ('Terrain_LiDAR_DTM_1m','WS250_W63_lawn_LiDAR2023_ground_patch_1m','WS251_W63b_passage_LiDAR2023_ground_patch_1m'):
    go=bpy.data.objects.get(gnm)
    if not go: continue
    Mg=go.matrix_world; Mgi=Mg.inverted(); k=0; dm=0
    for v in go.data.vertices:
        w=Mg@v.co
        if 179.3<=w.y<=190.4 and inner(w.y)-1.2<=w.x<=-192.0:
            lim=zmax(WK0,-191.5,w.y)-0.06
            if lim>-1e8 and w.z>lim: dm=max(dm,w.z-lim); v.co=Mgi@Vector((w.x,w.y,lim)); k+=1
    go.data.update(); print(TAG,'lowered',gnm,k,'max %.2f'%dm,flush=True)
GR=[b for b in map(bvo,['Terrain_LiDAR_DTM_1m','WS250_W63_lawn_LiDAR2023_ground_patch_1m','WS251_W63b_passage_LiDAR2023_ground_patch_1m']) if b]
WK=[b for b in map(bvo,['WS253_W63d_Feliciano_E_walk_slabs','WS253_W63d_Feliciano_E_walk_and_stairs_UNVERIFIED','WS254_W63e_recess_stairs_landing_to_wall_UNVERIFIED','WS254_W63e_Feliciano_E_walk_N_extension_to_OSM_walk_UNVERIFIED']) if b]
SN='WS255_W63f_Feliciano_E_wall_foot_paving_to_wall_UNVERIFIED'
old=bpy.data.objects[SN]; COL=old.users_collection[0]; mats=list(old.data.materials); bpy.data.objects.remove(old,do_unlink=True)
y0=179.2; y1=190.9; ys=list(np.arange(y0,y1,0.25))+[y1]; XE=-191.95; NC=9
def wtop(y): return zmax(WK,-191.5,max(y,y0+0.02))
def gn(x,y): return max(zmax(GR,x+dx,y+dy) for dx in (-0.15,0,0.15) for dy in (-0.12,0,0.12))
bm=bmesh.new(); G=[]
for y in ys:
    row=[]; wt=wtop(y); xw=inner(y)-0.10
    for k,x in enumerate(np.linspace(xw,XE,NC+1)):
        z=max(wt-0.004, gn(x,y)+0.03) if k<NC else wt-0.004
        row.append(bm.verts.new((x,y,z)))
    G.append(row)
for i in range(len(ys)-1):
    for k in range(NC): bm.faces.new([G[i][k],G[i][k+1],G[i+1][k+1],G[i+1][k]])
for row,rev in ((G[0],False),(G[-1],True)):
    L=[bm.verts.new((v.co.x,v.co.y,v.co.z-0.35)) for v in row]
    for k in range(NC):
        q=[row[k],L[k],L[k+1],row[k+1]]; bm.faces.new(q[::-1] if rev else q)
bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:])
top=set(sum(G,[]))
if sum(1 for f in bm.faces if all(v in top for v in f.verts) and f.normal.z<0)>len(ys): 
    for f in bm.faces: f.normal_flip()
for i in range(0,len(ys),8): print(TAG,'strip y%.2f'%ys[i],' '.join('%.2f'%v.co.z for v in G[i]),flush=True)
me2=bpy.data.meshes.new(SN); bm.to_mesh(me2); bm.free()
for m in mats: me2.materials.append(m)
uv=me2.uv_layers.new(name='UVMap')
for p in me2.polygons:
    for li in p.loop_indices:
        co=me2.vertices[me2.loops[li].vertex_index].co; uv.data[li].uv=(co.x,co.y) if abs(p.normal.z)>0.5 else (co.x,co.z)
so=bpy.data.objects.new(SN,me2); COL.objects.link(so)
print(TAG,'obj',SN,len(me2.vertices),len(me2.polygons),'up',sum(1 for p in me2.polygons if p.normal.z>0.5),flush=True)
