# ws75c: remaining visible Roads_OSM stubs by the new lot / grandstand lawn (x -256..-226, y -126..-72): delete faces that are top-most
# (or only under OZ walk-joint overlay) at their centre. College Ave (WS27/WS67) covered faces are left alone.
import bpy,bmesh
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
o=bpy.data.objects['Roads_OSM']; mw=o.matrix_world; kill=[]; tops={}
for p in o.data.polygons:
    c=mw@p.center
    if -256<c.x<-226 and -126<c.y<-72:
        hit,loc,nor,idx,ob,mx=sc.ray_cast(dg,c+Vector((0,0,30)),Vector((0,0,-1)))
        t=ob.name[:30] if hit else None; tops[t]=tops.get(t,0)+1
        if t and (t.startswith('Roads_OSM') or t.startswith('OZ_walk_joints')): kill.append(p.index)
print('WS75c tops',tops,'kill',len(kill),flush=True)
bm=bmesh.new(); bm.from_mesh(o.data); bm.faces.ensure_lookup_table()
bmesh.ops.delete(bm,geom=[bm.faces[i] for i in kill],context='FACES'); bm.to_mesh(o.data); bm.free(); o.data.update()
