import bpy, collections
o=bpy.data.objects['TZ_Cole_north_addition_UNVERIFIED']; mw=o.matrix_world; me=o.data
c=collections.Counter(); 
for p in me.polygons:
    z=(mw@p.center).z
    if p.material_index==0 and z>141.8: c[(round(z,2),round(p.area,3))]+=1
print('EAVEWALL',sorted(c.items())[:40], sum(c.values()))
print('ATTRS',[(a.name,a.domain,a.data_type) for a in me.attributes])
r=me.polygons[10]; print('ROOF10',[ (mw@me.vertices[v].co)[:] for v in r.vertices], r.normal[:])
for p in me.polygons:
    if p.material_index==1: print('ROOFF',p.index,round(p.area,1),[round(x,2) for x in (mw@p.center)],[round(x,2) for x in p.normal])
m=bpy.data.materials['Roof_tile_or_membrane']
for n in m.node_tree.nodes:
    extra=getattr(n,'attribute_name','') or getattr(n,'layer_name','')
    print('NODE',n.type,n.name,extra)
