# ws236 self-review: a thin dark line stays along the PK/M3b seam in the close-up. Test: the 4 cm lip of M3b's free edge over the
# f236c strip. Lift the strip's outer (extruded) verts to M3b z - 0.005 (still under the LiDAR surface, 5 mm lip).
import bpy, bmesh, mathutils
from mathutils.bvhtree import BVHTree
M=bpy.data.objects['M3b_north_LiDAR_DTM_1m_west_rail_corridor_UNVERIFIED_seam']
mb=bmesh.new(); mb.from_mesh(M.data); mb.transform(M.matrix_world); MT=BVHTree.FromBMesh(mb)
NF={'PK_Feliciano_west_DTM_fill_UNVERIFIED':290,'WS60_terrain_edge_apron_LiDAR_to_skirt':26}
names=list(NF)+[o.name for o in bpy.data.objects if o.name.startswith('WS68_RHD_ground_northDTM')]
for n in names:
    o=bpy.data.objects[n]; mw=o.matrix_world; mi=mw.inverted()
    bm=bmesh.new(); bm.from_mesh(o.data); bm.faces.ensure_lookup_table()
    strip=set(list(bm.faces)[-NF.get(n,135):])
    outer=[v for f in strip for v in f.verts if all(g in strip for g in v.link_faces)]
    c=0
    for v in set(outer):
        w=mw@v.co; h=MT.ray_cast(mathutils.Vector((w.x,w.y,w.z+60)),mathutils.Vector((0,0,-1)),200)
        if h[0] is None: continue
        v.co=mi@mathutils.Vector((w.x,w.y,h[0].z-0.005)); c+=1
    bm.to_mesh(o.data); o.data.update(); print('F236E',n[:30],'outer verts',c,flush=True)
