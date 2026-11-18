# ws152 review fixes: (C) E-W seam at y ~ -203.2 where WS142 Lot 9 asphalt meets the WS145/WS150 S patches -> seam-cover strip
# (asphalt-intensity cells only); (D) pale chip = Footpaths_OSM face (+ its OZ joint overlay) at (-69.0,-170.2) on asphalt-intensity
# cells (2.9-3.1k) -> delete only faces whose bbox lies E of x -71.2 (the real concrete walk N of the forecourt is x < -71.5, 7k).
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
exec(open(M+'scripts/ws152/fix152.py').read().split("apron('WS152_Lot9_N_triangle")[0].split("# Footpaths faces on asphalt cells in box A")[0])
exec("def _dummy(): pass")
src=open(M+'scripts/ws152/fix152.py').read()
exec(src[src.index('def apron('):src.index("apron('WS152_Lot9_N_triangle")])
fp=bpy.data.objects['Footpaths_OSM']; mw=fp.matrix_world; me=fp.data
bm=bmesh.new(); bm.from_mesh(me); bm.transform(mw); T=BVHTree.FromBMesh(bm); bm.faces.ensure_lookup_table(); kill=set()
for (x,y) in [(-69.0,-170.2),(-68.8,-170.5),(-69.2,-169.9),(-69.4,-170.0)]:
    h=T.ray_cast(Vector((x,y,140)),Vector((0,0,-1)))
    if h[0] is not None:
        f=bm.faces[h[2]]; xs=[v.co.x for v in f.verts]
        print("FIX152B_FP_FACE",h[2],round(min(xs),2),round(max(xs),2),round(min(v.co.y for v in f.verts),2),round(max(v.co.y for v in f.verts),2),"int",inten(x,y))
        if min(xs)>-71.2 and inten(x,y)<4000: kill.add(h[2])
bm.free()
bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
bmesh.ops.delete(bm,geom=[bm.faces[i] for i in kill],context='FACES'); bm.to_mesh(me); bm.free(); me.update(); print("FIX152B_FP_DELETED",len(kill))
apron('WS152_Lot9_S_patch_seam_cover_y-203_LiDAR2023_UNIFY58',-73.5,lambda y:min(-66.6,xe(y)),-204.2,-202.3,0.5,True)
