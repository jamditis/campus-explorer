# ws241 pass 4: probe241e for M3b's S/SE free edge W of the police building (W57 back line).
# flap targets: for selected free-edge verts (WS68 W edge, M3a W edge by the NJT deck) the outward xy direction and the
# EVALUATED skirt z at 1..5 m out (the skirt's under-modifiers dig a 3-4 m flat trench beside these edges = the dark slot).
import bpy, bmesh, json, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
JOBS=[('M3b_north_LiDAR_DTM_1m_west_rail_corridor',lambda p: -420<=p.x<=-344 and -70<=p.y<=-15)]
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']
for m in sk.modifiers: m.show_viewport=m.show_render
dg=bpy.context.evaluated_depsgraph_get(); e=sk.evaluated_get(dg); me=e.to_mesh(); M=sk.matrix_world
T=BVHTree.FromPolygons([M@v.co for v in me.vertices],[p.vertices[:] for p in me.polygons]); e.to_mesh_clear()
out={}
for pre,sel in JOBS:
    o=next(x for x in bpy.data.objects if x.name.startswith(pre)); W=o.matrix_world
    bm=bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table(); L=[]
    for v in bm.verts:
        if not v.is_boundary: continue
        p=W@v.co
        if not sel(p): continue
        c=sum((W@f.calc_center_median() for f in v.link_faces),Vector())/max(1,len(v.link_faces))
        d=Vector((p.x-c.x,p.y-c.y,0));
        if d.length<1e-6: continue
        d.normalize(); zs=[]
        for s in (0.5,1,2,3,4,5,6):
            h=T.ray_cast(Vector((p.x+d.x*s,p.y+d.y*s,p.z+30)),Vector((0,0,-1)),60); zs.append(round(h[0].z,3) if h[0] else None)
        L.append([v.index,round(p.x,2),round(p.y,2),round(p.z,3),round(d.x,3),round(d.y,3),zs])
    out[o.name]=L; bm.free()
    print('P241J',o.name[:20],len(L),'sample',L[:2],flush=True)
json.dump(out,open('/workspace/nj-scenes/montclair-state/scripts/ws241/probe241j.json','w')); os._exit(0)
