import bpy
o=bpy.data.objects['Morehead Hall roof (LiDAR)']; me=o.data
print('MODS',[(m.type,m.name) for m in o.modifiers])
print('ATTRS',[(a.name,a.domain,a.data_type) for a in me.attributes])
print('MATS',[m.name if m else None for m in me.materials])
ids=[1029,1812,4570,4574,3059,3055,560]
dg=bpy.context.evaluated_depsgraph_get(); em=o.evaluated_get(dg).data
print('evalpolys',len(em.polygons),'orig',len(me.polygons))
for a in em.attributes:
    if a.domain=='FACE' and a.data_type in('FLOAT','INT','BOOLEAN'):
        print('A',a.name,[round(float(a.data[i].value),3) for i in ids])
for i in ids:
    p=em.polygons[i]; print('P',i,p.material_index,[round(x,2) for x in p.normal],round(p.area,2),[round(x,1) for x in p.center])
m=bpy.data.materials['Roof_tile_or_membrane']
for n in m.node_tree.nodes:
    if n.type=='ATTRIBUTE': print('NODEATTR',n.attribute_name,n.attribute_type)
# stats: em attributes over sloped faces near hit
import statistics
for a in em.attributes:
    if a.domain=='FACE' and a.data_type=='FLOAT':
        vals=[a.data[p.index].value for p in em.polygons if p.normal.z<0.9 and abs(p.center.x+39)<4 and abs(p.center.y+55.5)<4]
        if vals: print('NEAR',a.name,len(vals),round(min(vals),3),round(statistics.mean(vals),3),round(max(vals),3))
