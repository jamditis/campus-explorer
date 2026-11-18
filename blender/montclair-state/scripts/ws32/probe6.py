import bpy,bmesh
from mathutils import Vector
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws32/fix4.py').read())
dg=bpy.context.evaluated_depsgraph_get(); dg.update()
for n in ('Footpaths_OSM','CCOM_dock_apron_20261014jf3','Lawn_worn_edge_along_walks','Curbs_granite_OSM'):
    o=bpy.data.objects[n]; e=o.evaluated_get(dg); m=e.to_mesh(); mw=o.matrix_world
    c=0
    for p in m.polygons:
        cc=mw@p.center
        if 1<cc.x<8 and -36<cc.y<-28:
            nz=(mw.to_3x3()@p.normal).normalized().z
            if abs(nz)<0.8:
                c+=1
                if c<8: print('STEEP',n,p.index,[round(x,2) for x in cc],round(nz,2),round(p.area,3),len(p.vertices))
    print('STEEPCOUNT',n,c, 'base faces',len(o.data.polygons) if o.type=='MESH' else '-', 'eval faces',len(m.polygons))
    e.to_mesh_clear()
