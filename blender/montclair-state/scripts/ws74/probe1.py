import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
def bvh(n):
    o=bpy.data.objects[n]; oe=o.evaluated_get(dg); m=oe.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); oe.to_mesh_clear(); return t
v=bpy.data.objects['WS73_curb_back_lawn_verge_UNVERIFIED']
print('W74 verge verts',len(v.data.vertices),'faces',len(v.data.polygons),[m.name for m in v.modifiers])
for p in list(v.data.vertices)[:40]: print('W74 vv',tuple(round(c,2) for c in (v.matrix_world@p.co)))
T=bvh('Terrain_LiDAR_DTM_1m'); Vb=bvh(v.name)
others=[o.name for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('WS70','WS60','WS68_RHD_ground'))]
print('W74 others',others)
OB={n:bvh(n) for n in others}
for x in (-205,-203,-201,-199,-197,-195):
  for y in [ -70+0.5*i for i in range(16)]:
    h=lambda t:(t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))[0])
    a=h(T); b=h(Vb); s=' '.join(f"{n[:6]}={h(t).z:.2f}" for n,t in OB.items() if h(t))
    print(f'W74 x{x} y{y:.1f} terr={a.z if a else None:} verge={b.z if b else None} {s}')
