# UNIFY #54: old Footpaths_OSM drape slabs between Lot 9 and Skyline Way. 2023 LiDAR class-2 intensity (ws142/dtm142.npy)
# x -71..-63, y -180..-204 is 2.0-3.1k everywhere (= asphalt; concrete reads 6-13k), no height step (smooth 2.4% fall S):
# the lot's stalls open straight onto Skyline Way with no walk or curb on the E side. Remove the Footpaths faces there and
# fill any 0.5 m cell not covered by Roads_OSM / Lot 9 / WS145 asphalt with lot asphalt at the lot's own LiDAR offset.
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
D=np.load('/workspace/nj-scenes/montclair-state/scripts/ws142/dtm142.npy'); X0,Y1,R=-95.0,-162.0,0.5
def dz(x,y):
    fx=(x-X0)/R; fy=(Y1-y)/R; j=int(fx); i=int(fy); tx=fx-j; ty=fy-i; Z=D[1]
    return (Z[i,j]*(1-tx)+Z[i,j+1]*tx)*(1-ty)+(Z[i+1,j]*(1-tx)+Z[i+1,j+1]*tx)*ty
BX=(-70.5,-63.0,-203.5,-178.7)
fp=bpy.data.objects['Footpaths_OSM']; mw=fp.matrix_world
bm=bmesh.new(); bm.from_mesh(fp.data)
dl=[f for f in bm.faces if (lambda c:(BX[0]<c.x<BX[1] and BX[2]<c.y<BX[3]))(mw@f.calc_center_median())]
cs=[tuple(round(v,1) for v in (mw@f.calc_center_median())) for f in dl]
print("FIX54_FP_DEL",len(dl),cs[:12]); bmesh.ops.delete(bm,geom=dl,context='FACES'); bm.to_mesh(fp.data); bm.free(); fp.data.update()
def flat(names):
    b=bmesh.new()
    for n in names:
        o=bpy.data.objects.get(n)
        if not o: continue
        t=bmesh.new(); t.from_mesh(o.data); t.transform(o.matrix_world)
        for v in t.verts: v.co.z=0
        m=bpy.data.meshes.new('tmp'); t.to_mesh(m); t.free(); b.from_mesh(m); bpy.data.meshes.remove(m)
    T=BVHTree.FromBMesh(b); b.free(); return T
asp=[o.name for o in bpy.data.objects if o.name.startswith(('WS142_Lot9_asphalt','WS145_walk_nose_lot_asphalt','WS135a_Skyline_Way_asphalt'))]
Tc=flat(['Roads_OSM']+asp)
a=bpy.data.objects[[n for n in asp if n.startswith('WS142')][0]]
b2=bmesh.new(); b2.from_mesh(a.data); b2.transform(a.matrix_world); Ta=BVHTree.FromBMesh(b2); b2.free()
offs=[]
for xx in (-72.0,-70.0,-69.0):
  for y in np.arange(-180,-203,-1.0):
    h=Ta.ray_cast(Vector((xx,y,300)),Vector((0,0,-1)))
    if h[0] is not None: offs.append(h[0].z-dz(xx,y))
off=float(np.median(offs)) if offs else 0.02
print("FIX54_LOT_OFFSET",round(off,3),len(offs))
cells=[]
for x in np.arange(-68.5,-63.0,0.5):
    for y in np.arange(-203.3,-178.7,0.5):
        c=Vector((x+0.25,y+0.25,10)); h=Tc.ray_cast(c,Vector((0,0,-1)))
        if h[0] is None and y>-190.6 and x<-66.4: cells.append((x,y))
print("FIX54_UNCOVERED_CELLS",len(cells),min(cells) if cells else '',max(cells) if cells else '')
if cells:
    me=bpy.data.meshes.new('WS148_Lot9_E_apron_asphalt_to_Skyline_LiDAR2023int_UNIFY54'); bm=bmesh.new(); V={}
    def gv(x,y):
        k=(round(x,2),round(y,2))
        if k not in V: V[k]=bm.verts.new((x,y,dz(x,y)+off-0.005))
        return V[k]
    for x,y in cells: bm.faces.new((gv(x,y),gv(x+0.5,y),gv(x+0.5,y+0.5),gv(x,y+0.5)))
    ed=[e for e in bm.edges if e.is_boundary]; r=bmesh.ops.extrude_edge_only(bm,edges=ed)
    for v in [g for g in r['geom'] if isinstance(g,bmesh.types.BMVert)]: v.co.z-=0.10
    bm.to_mesh(me); bm.free(); ob=bpy.data.objects.new(me.name,me); SCN.collection.objects.link(ob)
    me.materials.append(a.data.materials[0])
    print("FIX54_PATCH",len(me.polygons))
# terrain base verts poking above the paving in the box -> push under (top - 0.05)
tr=bpy.data.objects['Terrain_LiDAR_DTM_1m']; tm=tr.matrix_world; tmi=tm.inverted(); n=0
for v in tr.data.vertices:
    w=tm@v.co
    if BX[0]<w.x<BX[1] and BX[2]<w.y<BX[3]:
        lim=dz(w.x,w.y)+off-0.05
        if w.z>lim: w.z=lim; v.co=tmi@w; n+=1
tr.data.update(); print("FIX54_TERRAIN_LOWERED",n)
