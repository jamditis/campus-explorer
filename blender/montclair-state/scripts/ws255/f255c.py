# ws255c: re-run the W63f base-course rebuild (f255a part 2) against the ws255b surfaces (strip rebuilt on lowered ground), so the
# band's bottom stays buried and its top stays 0.85 m over the final paving.
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
TAG='F255C'
def bvo(n):
    o=bpy.data.objects.get(n)
    if not o: print(TAG,'MISSING',n,flush=True); return None
    M=o.matrix_world; me=o.data; vs=[M@v.co for v in me.vertices]
    ps=[p.vertices[:] for p in me.polygons if any(-200<vs[i].x<-186 and 165<vs[i].y<196 for i in p.vertices)]
    return BVHTree.FromPolygons(vs,ps) if ps else None
GR=[b for b in map(bvo,['Terrain_LiDAR_DTM_1m','WS250_W63_lawn_LiDAR2023_ground_patch_1m','WS251_W63b_passage_LiDAR2023_ground_patch_1m']) if b]
WK=[b for b in map(bvo,['WS253_W63d_Feliciano_E_walk_slabs','WS253_W63d_Feliciano_E_walk_and_stairs_UNVERIFIED','WS254_W63e_recess_stairs_landing_to_wall_UNVERIFIED','WS254_W63e_Feliciano_E_walk_N_extension_to_OSM_walk_UNVERIFIED']) if b]
def zmax(bl,x,y):
    z=-1e9
    for b in bl:
        h=b.ray_cast(Vector((x,y,300)),Vector((0,0,-1)),400)
        if h[0]: z=max(z,h[0].z)
    return z
def inner(y): return -194.69+0.0615*(y-172.0)   # wall line fitted to the PI band (y173 -194.62, y199 -193.03)
SN='WS255_W63f_Feliciano_E_wall_foot_paving_to_wall_UNVERIFIED'; so=bpy.data.objects[SN]
SB=BVHTree.FromObject(so,bpy.context.evaluated_depsgraph_get())
# base course
pi=bpy.data.objects['PI_Feliciano_east_base_course_UNVERIFIED']; Mp=pi.matrix_world; Mi=Mp.inverted()
bm=bmesh.new(); bm.from_mesh(pi.data)
fv=[(Mp@v.co) for v in bm.verts]
brk=sorted(set(round(p.y,2) for p in fv if p.x>-196 and 171.0<p.y<193.0))
# merge near-duplicate breaks
B=[]
for y in brk:
    if not B or y-B[-1]>0.3: B.append(y)
ya=min(y for y in B if y>=172.0); yb=max(y for y in B if y<=191.6)
df=[f for f in bm.faces if all((Mp@v.co).x>-196 and ya-0.02<=(Mp@v.co).y<=yb+0.02 for v in f.verts)]
n0=len(bm.faces); bmesh.ops.delete(bm,geom=df,context='FACES_ONLY')
lv=[v for v in bm.verts if not v.link_faces]; bmesh.ops.delete(bm,geom=lv,context='VERTS')
seg=[y for y in B if ya<=y<=yb]
print(TAG,'PI faces',n0,'deleted',len(df),'segments',len(seg)-1,'ya %.2f yb %.2f'%(ya,yb),flush=True)
def surf(x,y):
    z=max(zmax(GR,x,y),zmax(WK,x,y))
    h=SB.ray_cast(Vector((x,y,300)),Vector((0,0,-1)),400)
    return max(z,h[0].z) if h[0] else z
for a,b in zip(seg[:-1],seg[1:]):
    smp=[surf(inner(y)+0.12,y) for y in np.linspace(a,b,7)]
    top=max(smp)+0.85; za=surf(inner(a)+0.12,a)-0.08; zb=surf(inner(b)+0.12,b)-0.08
    def V(x,y,z): return bm.verts.new(Mi@Vector((x,y,z)))
    fa0,fb0=V(inner(a)+0.07,a,za),V(inner(b)+0.07,b,zb); fa1,fb1=V(inner(a)+0.07,a,top),V(inner(b)+0.07,b,top)
    ia1,ib1=V(inner(a)-0.01,a,top),V(inner(b)-0.01,b,top); ia0,ib0=V(inner(a)-0.01,a,za),V(inner(b)-0.01,b,zb)
    bm.faces.new([fa0,fb0,fb1,fa1]); bm.faces.new([fa1,fb1,ib1,ia1]); bm.faces.new([ia0,fa0,fa1,ia1]); bm.faces.new([fb0,ib0,ib1,fb1])
    print(TAG,'seg y%.2f-%.2f bot %.2f/%.2f top %.2f (surf %.2f..%.2f)'%(a,b,za,zb,top,min(smp),max(smp)),flush=True)
bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:])
bm.to_mesh(pi.data); bm.free(); pi.data.update()
print(TAG,'PI now',len(pi.data.polygons),flush=True)
