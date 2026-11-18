# ws204 W22 follow-up: close-up ray map (r204_cu.json) shows a 2-4 px band of the WS68 ground drape (1 m grid) poking up between the
# new WS204 fill and the WS70 berm base edge (fill line verts sit at berm-5 mm, the drape is higher there) -> jagged tan band.
# The drape is ground UNDER paving here: lower every WS68 vertex in the entrance box that is covered by another surface to 2 cm under
# the lowest covering surface at that point (only lowers, only covered verts; nothing visible moves except the hidden band).
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
def bvh(o):
    me=o.evaluated_get(dg).to_mesh(); mw=o.matrix_world
    return BVHTree.FromPolygons([mw@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons])
def ob(p): return [o for o in bpy.data.objects if o.name.startswith(p)][0]
G=ob('WS68_RHD_ground_northDTM'); mw=G.matrix_world; mi=mw.inverted()
COV=[ob(p) for p in ['WS204_CollegeAve_lot_entrance_asphalt_fill','WS70_gap_strip_grass_berms','KY_college_ave_carriageway_asphalt','WS74_cogen_lot_asphalt','WS76_accessible_lot_asphalt','WS67_CollegeAve_gap_asphalt','WS69_CollegeAve_gap_strip_curbs']]
TS=[bvh(o) for o in COV]; n=0
for v in G.data.vertices:
    p=mw@v.co
    if not (-264.5<p.x<-248.5 and -67.5<p.y<-55.5): continue
    tops=[]
    for t in TS:
        for dx,dy in ((0,0),(0.3,0),(-0.3,0),(0,0.3),(0,-0.3)):
            h=t.ray_cast(Vector((p.x+dx,p.y+dy,p.z+3)),Vector((0,0,-1)),6)
            if h[0] is not None: tops.append(h[0].z)
    if not tops: continue
    tz=min(tops)-0.02
    if p.z>tz: p.z=tz; v.co=mi@p; n+=1
G.data.update(); print('F204b WS68 verts lowered',n,flush=True)
