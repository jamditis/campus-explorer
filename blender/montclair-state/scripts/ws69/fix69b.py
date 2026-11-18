# ws69: skirt verts inside the Red Hawk Deck east end / under main terrain pushed 0.5 m under every covering surface
import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=bpy.data.objects
def bvh(o):
    dg=bpy.context.evaluated_depsgraph_get(); oe=o.evaluated_get(dg); m=oe.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); oe.to_mesh_clear(); return t
gn=[o.name for o in O if o.name.startswith('WS68_RHD_ground')]; print('S69 ground',gn)
cov=[bvh(O[n]) for n in ['Terrain_LiDAR_DTM_1m','eu_rhd_ground_slab']+gn]
SK=O['Context_skirt_3DEP_ortho_4km']; mw=SK.matrix_world; mi=mw.inverted(); n=0; mx=0
bm=bmesh.new(); bm.from_mesh(SK.data)
fs=[f for f in bm.faces if any((-264<=(mw@v.co).x<=-222 and -50<=(mw@v.co).y<=32) for v in f.verts)]
es=list({e for f in fs for e in f.edges}); print('S69 subdiv faces',len(fs),'edges',len(es))
bmesh.ops.subdivide_edges(bm,edges=es,cuts=10,use_grid_fill=True)
bm.to_mesh(SK.data); bm.free(); SK.data.update()
def low(x,y):
    hs=[]
    for t in cov:
        for dx in (-2.5,0,2.5):
            for dy in (-2.5,0,2.5):
                h=t.ray_cast(Vector((x+dx,y+dy,400)),Vector((0,0,-1)))[0]
                if h: hs.append(h.z)
    return min(hs) if hs else None
for v in SK.data.vertices:
    c=mw@v.co
    if -264<=c.x<=-222 and -50<=c.y<=32:
        m=low(c.x,c.y)
        if m is not None and c.z>m-0.5:
            mx=max(mx,c.z-(m-0.5)); v.co=mi@Vector((c.x,c.y,m-0.5)); n+=1
SK.data.update(); print('S69 lowered',n,'max',round(mx,2))
# re-survey
S=bvh(SK); bad=0; tot=0
for x in range(-262,-234,1):
  for y in range(-30,14,1):
    sk=S.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0]
    hs=[t.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0] for t in cov]; hs=[h.z for h in hs if h]
    if sk and hs:
        tot+=1
        if sk.z>min(hs)-0.05: bad+=1
print('S69 after skirt-over',bad,'of',tot)
bpy.ops.wm.save_mainfile(); print('S69 saved')
