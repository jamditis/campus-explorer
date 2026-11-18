import bpy, bmesh, os, sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
O=bpy.data.objects
T=O['Terrain_LiDAR_DTM_1m']; W75=O['WS75_sprague_lot_asphalt_ortho2020_UNVERIFIED_edges']
b75=BVHTree.FromObject(W75,dg)
assert W75.matrix_world==T.matrix_world
def covered(b,c):
    h=b.ray_cast(Vector((c.x,c.y,c.z+30)),Vector((0,0,-1)),60); return h[0] is not None
exp={'WS80_sprague_lot_fill_asphalt_ortho2020_UNVERIFIED_edges':32,'WS81_lot_seam_underlay_asphalt':8,'WS94_lot_slit_filler_asphalt_UNVERIFIED':13}
tot=0
for n,e in exp.items():
    o=O[n]; mw=o.matrix_world
    assert o.data.users==1, n
    idx=[f.index for f in o.data.polygons if (lambda c: c.x>-217.6 and -97.5<c.y<-89.2 and not covered(b75,c))(mw@f.center)]
    print('A99',n,len(idx),'expected',e)
    assert len(idx)==e
    bm=bmesh.new(); bm.from_mesh(o.data); bm.faces.ensure_lookup_table()
    bmesh.ops.delete(bm,geom=[bm.faces[i] for i in idx],context='FACES'); bm.to_mesh(o.data); bm.free(); o.data.update()
    o['ws99_note']='ws99: %d faces outside the lot E edge (island E tip / bank toe, x>-217.6, y -97.5..-89.2) removed; backup montclair_state_pre_20261112ws99.blend'%len(idx)
    tot+=len(idx)
print('A99 total',tot)
if os.environ.get('SAVE')=='1':
    bpy.ops.wm.save_mainfile(); print('A99 SAVED')
