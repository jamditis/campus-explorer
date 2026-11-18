# ws68c: skirt verts under the deck's east end (x -258..-238, y -45..30) pushed 0.5 m under the deck ground slab
import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def bvh(o):
    bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); return t
S=bvh(bpy.data.objects['eu_rhd_ground_slab']); SK=bpy.data.objects['Context_skirt_3DEP_ortho_4km']; mw=SK.matrix_world; mi=mw.inverted(); n=0
for v in SK.data.vertices:
    c=mw@v.co
    if -258<=c.x<=-238 and -45<=c.y<=30:
        hs=[S.ray_cast(Vector((c.x+dx,c.y+dy,200)),Vector((0,0,-1)))[0] for dx in (-3,0,3) for dy in (-3,0,3)]; hs=[h.z for h in hs if h]
        if hs and c.z>min(hs)-0.5: v.co=mi@Vector((c.x,c.y,min(hs)-0.5)); n+=1
SK.data.update(); print('C68 lowered',n); bpy.ops.wm.save_mainfile(); print('C68 saved')
