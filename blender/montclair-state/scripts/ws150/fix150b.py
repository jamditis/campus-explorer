# UNIFY #54 part 2 (ws150 review): ws148's fill stopped at y -190.6 but the terrain push-down covered the whole box to y -203.5,
# leaving a lawn pit between Lot 9's E curb and Skyline Way (close-up). LiDAR 2023 class-2 intensity is 2.0-3.1k (asphalt) for
# x -71..-62.5, y -180..-204, so fill every uncovered 0.5 m cell S of -190.6 with plain asphalt at the lot's LiDAR offset.
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
D=np.load('/workspace/nj-scenes/montclair-state/scripts/ws142/dtm142.npy'); X0,Y1,R=-95.0,-162.0,0.5
def dz(x,y):
    fx=(x-X0)/R; fy=(Y1-y)/R; j=int(fx); i=int(fy); tx=fx-j; ty=fy-i; Z=D[1]
    return (Z[i,j]*(1-tx)+Z[i,j+1]*tx)*(1-ty)+(Z[i+1,j]*(1-tx)+Z[i+1,j+1]*tx)*ty
names=['Roads_OSM','Curbs_granite_OSM','Footpaths_OSM']+[o.name for o in bpy.data.objects if o.name.startswith(('WS142_Lot9_asphalt','WS145_','WS135a_Skyline_Way_asphalt','WS148_Lot9_E_apron','WS136','WS135'))]
b=bmesh.new()
for n in names:
    o=bpy.data.objects.get(n)
    if not o or o.type!='MESH': continue
    t=bmesh.new(); t.from_mesh(o.data); t.transform(o.matrix_world)
    for v in t.verts: v.co.z=0
    m=bpy.data.meshes.new('tmp'); t.to_mesh(m); t.free(); b.from_mesh(m); bpy.data.meshes.remove(m)
T=BVHTree.FromBMesh(b); b.free()
off=0.04; cells=[]
for x in np.arange(-70.0,-62.5,0.5):
    for y in np.arange(-203.5,-190.5,0.5):
        h=T.ray_cast(Vector((x+0.25,y+0.25,10)),Vector((0,0,-1)))
        if h[0] is None: cells.append((x,y))
print("FIX150B_CELLS",len(cells),min(cells) if cells else '',max(cells) if cells else '')
if cells:
    me=bpy.data.meshes.new('WS150_Lot9_E_apron_S_asphalt_LiDAR2023int_UNIFY54b'); bm=bmesh.new(); V={}
    def gv(x,y):
        k=(round(x,2),round(y,2))
        if k not in V: V[k]=bm.verts.new((x,y,dz(x,y)+off-0.005))
        return V[k]
    for x,y in cells: bm.faces.new((gv(x,y),gv(x+0.5,y),gv(x+0.5,y+0.5),gv(x,y+0.5)))
    ed=[e for e in bm.edges if e.is_boundary]; r=bmesh.ops.extrude_edge_only(bm,edges=ed)
    for v in [g for g in r['geom'] if isinstance(g,bmesh.types.BMVert)]: v.co.z-=0.10
    bm.to_mesh(me); bm.free(); ob=bpy.data.objects.new(me.name,me)
    ref=[o for o in bpy.data.objects if o.name.startswith('WS148_Lot9_E_apron')][0]
    for c in ref.users_collection: c.objects.link(ob)
    me.materials.append(bpy.data.materials['Asphalt'])
    print("FIX150B_PATCH",len(me.polygons))
bpy.ops.wm.save_as_mainfile(filepath='/workspace/nj-scenes/montclair-state/montclair_state_ws150c.blend',copy=True)
print("SAVED_WS150C")
