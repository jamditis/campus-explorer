import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
L=bpy.data.objects['WS76_accessible_lot_asphalt_ortho2020_UNVERIFIED_edges']; mw=L.matrix_world
T=BVHTree.FromPolygons([mw@v.co for v in L.data.vertices],[tuple(f.vertices) for f in L.data.polygons])
def z(x,y):
    h=T.ray_cast(Vector((x,y,300)),Vector((0,0,-1))); return h[0].z if h[0] else None
B=bpy.data.objects['WS76_lot_stall_paint_blue_accessible_ortho2020_UNVERIFIED']
for n in ['','.001','.002','.003']:
    o=bpy.data.objects['WS76_lot_accessible_symbol_standin_UNVERIFIED'+n]; m=o.matrix_world
    print('Q196',o.name,'parent',o.parent.name if o.parent else None,'users_col',[c.name for c in o.users_collection],'data',o.data.name,'mods',[(x.type,x.name) for x in o.modifiers],flush=True)
    for i,f in enumerate(o.data.polygons):
        if i>=20: break
        P=[m@o.data.vertices[k].co for k in f.vertices]
        c=sum(P,Vector())/len(P); xs=[p.x for p in P]; ys=[p.y for p in P]; zs=[p.z for p in P]; za=z(c.x,c.y)
        dz=[p.z-(z(p.x,p.y) or p.z) for p in P]
        print('Q196  f%d n%d c(%.2f,%.2f) w%.2f h%.2f nz%.2f zrange %.3f above asphalt min %.3f max %.3f'%(i,len(P),c.x,c.y,max(xs)-min(xs),max(ys)-min(ys),f.normal.z,max(zs)-min(zs),min(dz),max(dz)),flush=True)
# blue paint height
m=B.matrix_world; dz=[ (m@v.co).z-(z((m@v.co).x,(m@v.co).y) or 0) for v in B.data.vertices[:400:10]]
print('Q196 blue paint dz',np.round(dz,3).tolist()[:40])
