import bpy, bmesh, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
F='/workspace/nj-scenes/montclair-state/montclair_state.blend'
W=['MID_streets_far_20261015ag','MID_street_tree_proto_20261015ag','MID_canopy_carpet_SW_far_crowns_wq2','MID_canopy_carpet_far_crowns_ai','MID_canopy_carpet_far2_crowns_ai','Context_skirt_3DEP_ortho_4km','Terrain_LiDAR_DTM_1m']
with bpy.data.libraries.load(F,link=False) as (s,d): d.objects=W
sc=bpy.context.scene
for o in d.objects: sc.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get()
for o in d.objects:
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    print('M48',o.name,o.type,'hide_r',o.hide_render,'mods',[m.type+':'+m.name for m in o.modifiers][:4],'x',round(min(v.x for v in bb)),round(max(v.x for v in bb)),'y',round(min(v.y for v in bb)),round(max(v.y for v in bb)),'z',round(min(v.z for v in bb)),round(max(v.z for v in bb)), 'verts',len(o.data.vertices) if o.type=='MESH' else '')
# instances from MID objects
import collections
c=collections.Counter(); pts=[]
for inst in dg.object_instances:
    if inst.is_instance and inst.parent and inst.parent.original.name.startswith('MID_'):
        c[inst.parent.original.name]+=1
        if 'street' in inst.parent.original.name: pts.append(inst.matrix_world.translation.copy())
print('M48 inst',dict(c))
T=json.load(open('/workspace/nj-scenes/montclair-state/data/ws47/band_trees.json'))['trees']
def bvh(o):
    e=o.evaluated_get(dg); m=e.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); return t
B=[bvh(bpy.data.objects[n]) for n in ('Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km')]
hit=[0,0,0]; near=0
from mathutils.kdtree import KDTree
kd=KDTree(max(1,len(pts)))
for i,p in enumerate(pts): kd.insert(p,i)
kd.balance()
for t in T:
    h0=B[0].ray_cast(Vector((t['x'],t['y'],400)),Vector((0,0,-1)))[0]; h1=B[1].ray_cast(Vector((t['x'],t['y'],400)),Vector((0,0,-1)))[0]
    if h0 and h0.z>50: hit[0]+=1
    elif h1 and h1.z>30: hit[1]+=1
    else: hit[2]+=1
    if pts:
        co,i,dd=kd.find(Vector((t['x'],t['y'],h1.z if h1 else 100)))
        if dd is not None and ((co.x-t['x'])**2+(co.y-t['y'])**2)**.5<12: near+=1
print('M48 band pts on DTM/skirt/none',hit,'within 12 m of existing MID street tree',near,'of',len(T),'MID street pts',len(pts))
