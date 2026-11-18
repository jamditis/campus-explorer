# UNIFY #54 part 3 (ws150 review, close-up): lawn showing at x -66.4..-63, y -190.6..-189 = Terrain_LiDAR_DTM_1m poking 3 cm above
# the Skyline Way N-end asphalt (127.35) in the strip ws148's fill skipped (its coverage test counted buried Roads_OSM faces).
# Fill the strip with plain asphalt at the lot's LiDAR offset and push terrain verts there under the paving.
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
D=np.load('/workspace/nj-scenes/montclair-state/scripts/ws142/dtm142.npy'); X0,Y1,R=-95.0,-162.0,0.5
def dz(x,y):
    fx=(x-X0)/R; fy=(Y1-y)/R; j=int(fx); i=int(fy); tx=fx-j; ty=fy-i; Z=D[1]
    return (Z[i,j]*(1-tx)+Z[i,j+1]*tx)*(1-ty)+(Z[i+1,j]*(1-tx)+Z[i+1,j+1]*tx)*ty
pav=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('WS142_Lot9_asphalt','WS135a_Skyline_Way_asphalt','WS148_Lot9_E_apron','WS150_Lot9_E_apron','WS145_walk_nose'))]
def bvh(objs,flat):
    b=bmesh.new()
    for o in objs:
        t=bmesh.new(); t.from_mesh(o.data); t.transform(o.matrix_world)
        if flat:
            for v in t.verts: v.co.z=0
        m=bpy.data.meshes.new('tmp'); t.to_mesh(m); t.free(); b.from_mesh(m); bpy.data.meshes.remove(m)
    T=BVHTree.FromBMesh(b); b.free(); return T
Tf=bvh(pav,True); T3=bvh(pav,False)
cells=[]
for x in np.arange(-67.0,-62.5,0.5):
    for y in np.arange(-191.0,-188.0,0.5):
        if Tf.ray_cast(Vector((x+0.25,y+0.25,10)),Vector((0,0,-1)))[0] is None: cells.append((x,y))
print("FIX150C_CELLS",len(cells),cells[:20])
if cells:
    me=bpy.data.meshes.new('WS150_Lot9_E_apron_Skyline_N_end_strip_asphalt_UNIFY54c'); bm=bmesh.new(); V={}
    def gv(x,y):
        k=(round(x,2),round(y,2))
        if k not in V: V[k]=bm.verts.new((x,y,dz(x,y)+0.035))
        return V[k]
    for x,y in cells: bm.faces.new((gv(x,y),gv(x+0.5,y),gv(x+0.5,y+0.5),gv(x,y+0.5)))
    ed=[e for e in bm.edges if e.is_boundary]; r=bmesh.ops.extrude_edge_only(bm,edges=ed)
    for v in [g for g in r['geom'] if isinstance(g,bmesh.types.BMVert)]: v.co.z-=0.10
    bm.to_mesh(me); bm.free(); ob=bpy.data.objects.new(me.name,me)
    ref=[o for o in bpy.data.objects if o.name.startswith('WS148_Lot9_E_apron')][0]
    for c in ref.users_collection: c.objects.link(ob)
    me.materials.append(bpy.data.materials['Asphalt']); pav.append(ob); T3=bvh(pav,False)
tr=bpy.data.objects['Terrain_LiDAR_DTM_1m']; tm=tr.matrix_world; tmi=tm.inverted(); n=0
for v in tr.data.vertices:
    w=tm@v.co
    if -68.0<w.x<-62.0 and -193.0<w.y<-187.5:
        h=T3.ray_cast(Vector((w.x,w.y,w.z+5)),Vector((0,0,-1)))
        lim=min(dz(w.x,w.y)-0.02, (h[0].z-0.06) if h[0] is not None else 1e9)
        if w.z>lim: w.z=lim; v.co=tmi@w; n+=1
tr.data.update(); print("FIX150C_TERRAIN_LOWERED",n)
bpy.ops.wm.save_as_mainfile(filepath='/workspace/nj-scenes/montclair-state/montclair_state_ws150d.blend',copy=True)
print("SAVED_WS150D")
