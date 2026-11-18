import bpy
dg=bpy.context.evaluated_depsgraph_get()
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; te=T.evaluated_get(dg); me=te.to_mesh()
names=[m.name if m else None for m in me.materials]; mw=T.matrix_world; h={}; ex={}
for p in me.polygons:
    c=mw@p.center
    if -240<c.x<-226 and -126<c.y<-110:
        n=names[p.material_index]; h[n]=h.get(n,0)+1
        if n and ('Concrete' in n or 'walk' in n.lower() or 'mulch' in n.lower() or 'asph' in n.lower()): ex.setdefault(n,[]).append((round(c.x,2),round(c.y,2),round(c.z,3),round(p.area,3)))
print('EVAL', len(me.polygons), h)
for k,v in ex.items(): print('EX',k,len(v),v[:12])
for md in T.modifiers: print('MOD',md.name,md.type,md.show_render, md.node_group.name if getattr(md,'node_group',None) else '')
