import bpy, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
out=[]
g=bpy.data.objects['M3a_north_LiDAR_DTM_1m_ext_y515_UNVERIFIED_seam']
for m in g.material_slots:
    mt=m.material; out.append('M3a mat %s nodes %s'%(mt.name,[(n.type,getattr(n,'attribute_name',''),getattr(n,'uv_map','')) for n in mt.node_tree.nodes if n.type in('ATTRIBUTE','UVMAP','TEX_COORD','TEX_IMAGE','VERTEX_COLOR')]))
out.append('M3a attrs %s uv %s'%([(a.name,a.domain,a.data_type) for a in g.data.attributes],[u.name for u in g.data.uv_layers]))
def ev(o):
    for m in o.modifiers: m.show_viewport=m.show_render
    dg=bpy.context.evaluated_depsgraph_get(); e=o.evaluated_get(dg); me=e.to_mesh(); M=o.matrix_world
    t=BVHTree.FromPolygons([M@v.co for v in me.vertices],[p.vertices[:] for p in me.polygons]); e.to_mesh_clear(); return t
T={n:ev(bpy.data.objects[k]) for n,k in [('sk','Context_skirt_3DEP_ortho_4km'),('ws68',next(x.name for x in bpy.data.objects if x.name.startswith('WS68_RHD_ground')))]}
for y in (-60,-50,-40,-30):
    row=[]
    for i in range(17):
        x=-350+i*0.5; r=[]
        for n,t in T.items():
            h=t.ray_cast(Vector((x,y,200)),Vector((0,0,-1))); r.append('%s%.2f'%(n[:2],h[0].z) if h[0] else n[:2]+'--')
        row.append('%.1f:%s'%(x,'/'.join(r)))
    out.append('y=%d %s'%(y,' '.join(row)))
open('/workspace/nj-scenes/montclair-state/scripts/ws241/probe241d.out','w').write('\n'.join(out)); print('P241D ok',flush=True)
os._exit(0)
