import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
def bvh(n):
    o=bpy.data.objects.get(n); e=o.evaluated_get(dg); m=e.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world)
    t=BVHTree.FromBMesh(bm); bm.free(); e.to_mesh_clear(); return t
names=['WS27_CollegeAve_carriageway_2020ortho','Roads_OSM','WS27_CollegeAve_curb_left_UNVERIFIED','WS27_CollegeAve_curb_right_UNVERIFIED','Footpaths_OSM','COLE_plaza_deck_bs','WS35_Kasser_terrace_steps_concrete_5risers_UNVERIFIED']
T={n:bvh(n) for n in names}
for n in names:
    o=bpy.data.objects[n]; print('P39b',n,len(o.data.vertices),[m.type+':'+m.name for m in o.modifiers], [s.material.name for s in o.material_slots if s.material][:4])
def iv(t,y):
    out=[];cur=None
    for i in range(-480,-340):
        x=i*0.5; h=t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))[0] is not None
        if h and cur is None: cur=x
        if not h and cur is not None: out.append((cur,x-0.5)); cur=None
    if cur is not None: out.append((cur,-170.5))
    return out
for y in range(-136,-66,4):
    print('P39b y',y,' | '.join('%s:%s'%(n[:12] if n[:4]!='WS27' else n[17:27],iv(T[n],y)) for n in names))
