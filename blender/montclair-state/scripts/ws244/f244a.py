# ws244 W62: ground still poked through the turf / east pad / fence feet on the last 1 m LiDAR cell of the east bank
# (probe243b: turf 19 faces <=0.90 m, east pad 72 <=1.11 m, fence posts 30). Cause: the hold-under target ended exactly at
# the turf/pad edge, so ground vertices one cell outside stayed high and their faces rose across the edge.
# Fix: grow the hidden hold-under target 1.2 m outward from every boundary edge, flat at the edge height (a narrow level
# margin outside the field, as built pitches have; width UNVERIFIED). The GN only lowers ground points within 3 m over the
# target (never raises), so ground below the field edge is unchanged and paving never moves.
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
o=bpy.data.objects['WS243_stands_pitch_holdunder_target']
bm=bmesh.new(); bm.from_mesh(o.data); bm.edges.ensure_lookup_table()
W=1.5; k=0
B=[e for e in bm.edges if e.is_boundary and len(e.link_faces)==1]
new=[]
bv=BVHTree.FromBMesh(bm)
def over(p):
    # only a target surface BELOW the strip matters (the GN ray hits the highest surface first; a strip under an existing
    # surface is never reached, a strip over one would hold the ground at the strip's higher level)
    h=bv.ray_cast(p+Vector((0,0,0.01)),Vector((0,0,-1)),40)
    return h[0] is not None
skip=0
for e in B:
    a,b=e.verts[0].co.copy(),e.verts[1].co.copy(); f=e.link_faces[0]; c=f.calc_center_median()
    d=(b-a); d.z=0
    if d.length<1e-4: continue
    n=Vector((d.y,-d.x,0)).normalized(); m=(a+b)/2
    if n.dot(Vector((m.x-c.x,m.y-c.y,0)))<0: n=-n
    new.append((a,b,n))
for a,b,n in new:
    # skip a strip if it would lie over another part of the target (e.g. a step strip over the pad, a pad strip over the walkway)
    q=[(a+b)/2+n*(W*0.5),a+n*W*0.9+(b-a)*0.05,b+n*W*0.9-(b-a)*0.05]
    if any(over(x) for x in q): skip+=1; continue
    vs=[bm.verts.new(a),bm.verts.new(b),bm.verts.new(b+n*W),bm.verts.new(a+n*W)]
    bm.faces.new(vs); k+=1
bm.to_mesh(o.data); bm.free(); o.data.update()
print('F244A target grown',k,'skipped(over target)',skip,'edge strips width',W,flush=True)
