import bpy, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=bpy.data.objects; dg=bpy.context.evaluated_depsgraph_get()
ng=bpy.data.node_groups['WT_skirt_under_richardson_west']
for n in ng.nodes:
    ins={i.name:(round(i.default_value,3) if isinstance(getattr(i,'default_value',None),float) else str(getattr(i,'default_value',''))[:30]) for i in n.inputs if not i.is_linked and hasattr(i,'default_value')}
    print('N',n.name,n.bl_idname,getattr(n,'operation',''),getattr(n,'data_type',''),ins)
for l in ng.links: print('L',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
def bvh(o):
    e=o.evaluated_get(dg); m=e.to_mesh(); b=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); n=len(m.vertices); e.to_mesh_clear(); return b,n
E=O['WT_richardson_west_LiDAR_patch_UNVERIFIED']; sk=O['Context_skirt_3DEP_ortho_4km']
BE,_=bvh(E); BS,ns=bvh(sk); print('skirt eval verts',ns)
hist={}
for p in E.data.polygons:
    c=p.center
    for fx,fy in ((0,0),(0.25,0.25),(-0.25,0.25),(0.25,-0.25),(-0.25,-0.25)):
        x,y=c.x+fx,c.y+fy
        a=BE.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))[0]; s=BS.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))[0]
        if a is not None and s is not None and s.z>a.z-0.003:
            k=int(x)//4*4; hist.setdefault(k,[0,0.0]); hist[k][0]+=1; hist[k][1]=max(hist[k][1],round(s.z-a.z,3))
print('POKE by x',sorted(hist.items()))
