import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
N=['WS94_lot_slit_filler_asphalt_UNVERIFIED','WS75_sprague_lot_asphalt_ortho2020_UNVERIFIED_edges','WS76_accessible_lot_asphalt_ortho2020_UNVERIFIED_edges','WS76_lot_stall_paint_blue_accessible_ortho2020_UNVERIFIED']
T={}
for n in N:
    o=bpy.data.objects[n]; mw=o.matrix_world; V=[mw@v.co for v in o.data.vertices]
    T[n]=BVHTree.FromPolygons(V,[tuple(p.vertices) for p in o.data.polygons])
    xs=[v.x for v in V]; ys=[v.y for v in V]
    print('P198',n,len(V),len(o.data.polygons),'bb',round(min(xs),1),round(max(xs),1),round(min(ys),1),round(max(ys),1),'mats',[m.name if m else None for m in o.data.materials],'mods',[m.name for m in o.modifiers],'smooth',sum(p.use_smooth for p in o.data.polygons),flush=True)
o=bpy.data.objects[N[0]]; mw=o.matrix_world
for p in o.data.polygons:
    c=mw@p.center; nz=(mw.to_3x3()@p.normal).normalized().z
    print('P198f',p.index,tuple(round(x,2) for x in c),'nz',round(nz,3),'verts',[tuple(round(x,2) for x in mw@o.data.vertices[i].co) for i in p.vertices],flush=True)
for y in np.arange(-86,-72,1.0):
    row=[]
    for x in np.arange(-238,-212,2.0):
        s=[]
        for n in N[:3]:
            h=T[n].ray_cast(Vector((x,y,300)),Vector((0,0,-1)))
            s.append('%.2f'%h[0].z if h[0] else '  -   ')
        row.append('/'.join(s))
    print('P198g y=%.0f'%y,' '.join(row),flush=True)
