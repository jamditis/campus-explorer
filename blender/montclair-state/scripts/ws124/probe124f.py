import bpy
dg=bpy.context.evaluated_depsgraph_get()
for o in bpy.data.objects:
    if o.type!='MESH': continue
    e=o.evaluated_get(dg); m=e.to_mesh(); mw=o.matrix_world; hits={}
    for p in m.polygons:
        c=mw@p.center
        if -209.3<c.x<-207.3 and -203.0<c.y<-199.0 and 124.0<c.z<125.2:
            mn=m.materials[p.material_index].name if m.materials and m.materials[p.material_index] else None
            k=(mn,round(p.normal.z,1)); hits.setdefault(k,[]).append((round(c.x,2),round(c.y,2),round(c.z,3)))
    e.to_mesh_clear()
    for k,v in hits.items(): print('G',o.name[:55],k,len(v),v[:4])
