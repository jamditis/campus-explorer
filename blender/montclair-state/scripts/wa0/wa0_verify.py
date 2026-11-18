import bpy, json
from mathutils import Vector
from mathutils.geometry import intersect_point_line
O=bpy.data.objects
fl=O['QU_G_floor_UNVERIFIED']; mw=fl.matrix_world; me=fl.data
ed=[(mw@me.vertices[e.vertices[0]].co, mw@me.vertices[e.vertices[1]].co) for e in me.edges]
def dedge(p):
    best=9
    for a,b in ed:
        q,t=intersect_point_line(p,a,b); t=min(max(t,0),1); q=a.lerp(b,t); best=min(best,(q.to_2d()-p.to_2d()).length)
    return best
F=O['WA0_richardson_wall_foot_fill_UNVERIFIED']; fm=F.matrix_world
import mathutils
# polygon point-in test via ray up against floor
from mathutils.bvhtree import BVHTree
bf=BVHTree.FromObject(fl,bpy.context.evaluated_depsgraph_get())
ds=[]
for p in F.data.polygons:
    c=fm@p.center
    if bf.ray_cast(Vector((c.x,c.y,130)),Vector((0,0,1)))[0] is not None:
        ds.append(round(dedge(c),3))
ds.sort()
print('VER inside-floor fill faces',len(ds),'dist-to-floor-edge max',ds[-1] if ds else None,'p90',ds[int(len(ds)*.9)] if ds else None)
print('VER floor z',round((mw@me.vertices[0].co).z,3))
