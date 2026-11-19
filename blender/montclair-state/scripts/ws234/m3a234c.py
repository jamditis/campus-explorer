# ws234 M3a step 2: delete Context_skirt faces that lie fully inside the M3a extension footprint (every corner AND the centroid
# over extension ground) so the coarse 3DEP skirt can't stand up between its lowered vertices (rail cut, station). Faces that
# straddle the extension edge stay (their inside corners were already lowered 0.35 m under the extension in m3a234.py).
import bpy, bmesh, mathutils
from mathutils.bvhtree import BVHTree
import os
V2=os.environ.get('M3A_RULE')=='v2'
e=bpy.data.objects['M3a_north_LiDAR_DTM_1m_ext_UNVERIFIED_seam' if V2 else 'M3a_north_LiDAR_DTM_1m_ext_y515_UNVERIFIED_seam']; mw=e.matrix_world
bvh=BVHTree.FromPolygons([(mw@v.co)[:] for v in e.data.vertices],[p.vertices[:] for p in e.data.polygons])
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']; smw=sk.matrix_world
def over(w): return bvh.ray_cast(mathutils.Vector((w.x,w.y,400)),mathutils.Vector((0,0,-1)))[0] is not None
bm=bmesh.new(); bm.from_mesh(sk.data)
cand=[]
for f in bm.faces:
    c=smw@f.calc_center_median()
    if c.y<(38 if V2 else 510) or c.x<-460 or c.x>150: continue
    if over(c) and all(over(smw@v.co) for v in f.verts): cand.append(f)
el=[ (smw@f.calc_center_median()) for f in cand]
print('F234C skirt faces deleted',len(cand),'edge len sample',round(cand[0].edges[0].calc_length(),2) if cand else None,flush=True)
bmesh.ops.delete(bm,geom=cand,context='FACES_ONLY')
bm.to_mesh(sk.data); bm.free(); sk.data.update()
