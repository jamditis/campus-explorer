import bpy
dg=bpy.context.evaluated_depsgraph_get()
for o in bpy.data.objects:
    if o.type not in ('MESH','CURVE'): continue
    try:
        e=o.evaluated_get(dg); m=e.to_mesh()
    except Exception: continue
    if m is None: continue
    mw=o.matrix_world; hits=[]
    for p in m.polygons:
        c=mw@p.center
        if -212.0<c.x<-207.5 and -204.5<c.y<-200.3 and 123.8<c.z<125.4: hits.append((round(c.x,2),round(c.y,2),round(c.z,3),round(p.normal.z,2),round(p.area,3)))
    e.to_mesh_clear()
    if hits: print('G',o.name[:70],len(hits),sorted(hits,key=lambda h:-h[2])[:14])
