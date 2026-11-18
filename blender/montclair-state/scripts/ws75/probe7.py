import bpy
for n in ('gb_cogen_paving','Footpaths_OSM'):
    o=bpy.data.objects[n]; mw=o.matrix_world
    for p in o.data.polygons:
        c=mw@p.center
        if -280<c.x<-235 and -140<c.y<-95:
            print('P7',n,p.index,o.material_slots[p.material_index].material.name[:22],'c %.1f %.1f %.1f'%tuple(c),'area %.1f'%p.area,'nz %.2f'%p.normal.z)
