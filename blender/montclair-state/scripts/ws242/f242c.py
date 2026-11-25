# W59b (ws242): the dark band W of the police building in the W57 eye view = a 15 x 31 m gap in M3b (x -395..-380,
# y -52..-21) between M3b's diagonal E edge and its small island to the east; the skirt shows 0.4-1.5 m lower in it.
# Nothing covers the gap now (cov242: no ground object, base or evaluated, over 5 test points), and M3b's own source
# (North_terrain_LiDAR_1m) has NO DATA there (x -389..-380), so the real DTM can't be re-sampled. Fill: 1 m lattice cells
# whose centre is not on an M3b face, welded to M3b's existing integer-grid verts; new verts get z linearly interpolated
# along the row between the nearest M3b verts W and E (one-sided rows take the nearer side). Lawn/ground material of the
# nearest M3b face. Ground only; no paving touched. Surface between the two LiDAR edges = UNVERIFIED (DTM no-data).
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
o=next(x for x in bpy.data.objects if x.name.startswith('M3b_north_LiDAR_DTM_1m'))
X0,X1,Y0,Y1=-396,-380,-52,-21
M=o.matrix_world; Mi=M.inverted()
bm=bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
VM={}
for v in bm.verts:
    p=M@v.co
    if X0-25<=p.x<=X1+25 and Y0-2<=p.y<=Y1+2 and abs(p.x-round(p.x))<1e-3 and abs(p.y-round(p.y))<1e-3: VM[(round(p.x),round(p.y))]=v
T=BVHTree.FromBMesh(bm)
def covered(x,y): return T.ray_cast(Mi@Vector((x,y,600)),Vector((0,0,-1)))[0] is not None
def zrow(x,y):
    w=[k for k in VM if k[1]==y and k[0]<x and x-k[0]<=20]; e=[k for k in VM if k[1]==y and k[0]>x and k[0]-x<=20]
    kw=max(w) if w else None; ke=min(e) if e else None
    if kw and ke:
        zw=(M@VM[kw].co).z; ze=(M@VM[ke].co).z; t=(x-kw[0])/(ke[0]-kw[0]); return zw+(ze-zw)*t
    k=kw or ke; return (M@VM[k].co).z if k else None
NEW={}; dz=[]
def vert(x,y):
    v=VM.get((x,y)) or NEW.get((x,y))
    if v: return v
    z=zrow(x,y)
    if z is None: return None
    v=bm.verts.new(Mi@Vector((x,y,z))); NEW[(x,y)]=v; return v
add=0
for y in range(Y0,Y1):
    for x in range(X0,X1):
        if covered(x+0.5,y+0.5): continue
        vs=[vert(x,y),vert(x+1,y),vert(x+1,y+1),vert(x,y+1)]
        if None in vs: continue
        try: f=bm.faces.new(vs)
        except ValueError: continue
        nb=[g for v in vs for g in v.link_faces if g is not f]; f.material_index=nb[0].material_index if nb else 0; add+=1
bm.normal_update()
dn=sum(1 for f in bm.faces if f.normal.z<0)
zs=[(M@v.co).z for v in NEW.values()]
bm.to_mesh(o.data); o.data.update(); bm.free()
print('F242C M3b gap fill faces',add,'new verts',len(NEW),'z range',round(min(zs or [0]),2),round(max(zs or [0]),2),'down-facing faces',dn,flush=True)
