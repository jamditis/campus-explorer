import bpy, numpy as np
A=np.array([-235.4,-235.3]);B=np.array([-222.0,-197.4]);d=(B-A)/np.linalg.norm(B-A);n=np.array([-d[1],d[0]])
dg=bpy.context.evaluated_depsgraph_get()
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    e=o.evaluated_get(dg); me=e.to_mesh(); mw=o.matrix_world; hits=[]
    for f in me.polygons:
        c=mw@f.center; q=np.array([c.x,c.y])-A; s=q@d; t=q@n
        if 4<s<13 and -3.5<t<-1.0: hits.append((round(s,1),round(t,1),round(c.z,2),f.material_index))
    e.to_mesh_clear()
    if hits and not o.name.startswith(('Terrain_LiDAR','WS113_terrain')): print('C115',o.name[:60],len(hits),hits[:5],[m.name for m in o.data.materials][:3])
    elif hits: print('C115 terrain',o.name[:30],len(hits),set(h[3] for h in hits))
