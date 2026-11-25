# W60: M3a free-edge verts along the W side of Lot 28S (x -262..-195, y 585..745): outward dir + EVALUATED skirt z 0.5..10 m out,
# plus any other non-skirt object hit straight down at 3 m out (so the flap never lands on another ground/paving).
import bpy, bmesh, json, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']
dg=bpy.context.evaluated_depsgraph_get(); e=sk.evaluated_get(dg); me=e.to_mesh(); M=sk.matrix_world
T=BVHTree.FromPolygons([M@v.co for v in me.vertices],[p.vertices[:] for p in me.polygons]); e.to_mesh_clear()
sc=bpy.context.scene
o=next(x for x in bpy.data.objects if x.name.startswith(os.environ.get('POBJ','M3a_north_LiDAR_DTM_1m_ext_y515'))); W=o.matrix_world
bm=bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table(); L=[]
for v in bm.verts:
    if not v.is_boundary: continue
    p=W@v.co
    bx=[float(t) for t in os.environ.get('PBOX','-262,-195,585,745').split(',')]
    if not (bx[0]<=p.x<=bx[1] and bx[2]<=p.y<=bx[3]): continue
    c=sum((W@f.calc_center_median() for f in v.link_faces),Vector())/max(1,len(v.link_faces))
    d=Vector((p.x-c.x,p.y-c.y,0))
    if d.length<1e-6: continue
    d.normalize()
    if os.environ.get('FIXD'): d=Vector([float(t) for t in os.environ['FIXD'].split(',')]+[0]).normalized()
    zs=[]
    for s in (0.5,1,2,3,4,5,6,8,10):
        h=T.ray_cast(Vector((p.x+d.x*s,p.y+d.y*s,p.z+30)),Vector((0,0,-1)),80); zs.append(round(h[0].z,3) if h[0] else None)
    h=sc.ray_cast(dg,Vector((p.x+d.x*3,p.y+d.y*3,p.z+30)),Vector((0,0,-1)),distance=80)
    L.append([v.index,round(p.x,2),round(p.y,2),round(p.z,3),round(d.x,3),round(d.y,3),zs,h[4].name if h[0] else None])
json.dump({o.name:L},open('/workspace/nj-scenes/montclair-state/scripts/ws242/'+os.environ.get('PO','probe242d.json'),'w'))
print('P242D',o.name,len(L),'sample',L[:3],flush=True); os._exit(0)
