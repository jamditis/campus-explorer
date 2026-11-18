# UNIFY #51 candidate fix (ws147; NOT run on main — memory-blocked). Run in a loaded test copy of main.
# Evidence (2023 LiDAR class-2 intensity, ws142/dtm142.npy layer 2, 0.5 m; grid in LOG ws147):
#   forecourt concrete 11-13k at x <= -69.5, y -175..-178; the walk E of it = 6.5-8k strip x -69.2..-67.2 (2.0 m) running N-S,
#   ending SQUARE at y ~ -178.2 on the same E-W line as Lot 9's N edge (-178.6); asphalt 2-3k S of -178.5 and E of x -66.5.
# Design: walk ends square on a straight E-W line (no skew slab, no asphalt wedge); its W edge butts the forecourt curb at x -69.2.
import bpy, bmesh, numpy as np
from mathutils import Vector
D=np.load('/workspace/nj-scenes/montclair-state/scripts/ws142/dtm142.npy'); X0,Y1,R=-95.0,-162.0,0.5
def dz(x,y):
    fx=(x-X0)/R; fy=(Y1-y)/R; j=int(fx); i=int(fy); tx=fx-j; ty=fy-i; Z=D[1]
    return (Z[i,j]*(1-tx)+Z[i,j+1]*tx)*(1-ty)+(Z[i+1,j]*(1-tx)+Z[i+1,j+1]*tx)*ty
XW,XE,YS,YN=-69.2,-67.0,-178.4,-175.0
fp=bpy.data.objects['Footpaths_OSM']; mw=fp.matrix_world
bm=bmesh.new(); bm.from_mesh(fp.data)
dl=[f for f in bm.faces if (lambda c:(-70.2<c.x<-66.2 and -181.5<c.y<-174.6))(mw@f.calc_center_median())]
print("FIX51_FP_FACES_DEL",len(dl)); bmesh.ops.delete(bm,geom=dl,context='FACES'); bm.to_mesh(fp.data); bm.free(); fp.data.update()
# new slab: 0.5 m grid, top = LiDAR smoothed + 0.03 (walk sits ~3 cm over asphalt at the end line), 2 % fall to E
me=bpy.data.meshes.new('WS147_walk_E_of_forecourt_square_end_UNIFY51'); bm=bmesh.new()
nx,ny=5,8; xs=np.linspace(XW,XE,nx); ys=np.linspace(YS,YN,ny); V={}
for i,x in enumerate(xs):
    for j,y in enumerate(ys): V[i,j]=bm.verts.new((x,y,dz(x,y)+0.03))
for i in range(nx-1):
    for j in range(ny-1): bm.faces.new((V[i,j],V[i+1,j],V[i+1,j+1],V[i,j+1]))
# 0.12 m edge skirt down so no slot shows over lawn/asphalt
ed=[e for e in bm.edges if e.is_boundary]
r=bmesh.ops.extrude_edge_only(bm,edges=ed)
for v in [g for g in r['geom'] if isinstance(g,bmesh.types.BMVert)]: v.co.z-=0.12
bm.to_mesh(me); bm.free()
ob=bpy.data.objects.new(me.name,me); bpy.context.scene.collection.objects.link(ob)
mat=bpy.data.materials.get('WS4_Concrete_walk_broom_nogrid'); me.materials.append(mat)
print("FIX51_SLAB",len(me.polygons),"end z",round(dz((XW+XE)/2,YS)+0.03,3))
# probe: lot asphalt top at the end line should be <= slab end top
asp=bpy.data.objects.get([o.name for o in bpy.data.objects if o.name.startswith('WS142_Lot9_asphalt')][0])
from mathutils.bvhtree import BVHTree
b2=bmesh.new(); b2.from_mesh(asp.data); b2.transform(asp.matrix_world); T=BVHTree.FromBMesh(b2); b2.free()
for x in (-69.0,-68.1,-67.2):
    h=T.ray_cast(Vector((x,YS-0.15,200)),Vector((0,0,-1)))
    print("FIX51_PROBE x",x,"asphalt",None if h[0] is None else round(h[0].z,3),"slab",round(dz(x,YS)+0.03,3))
