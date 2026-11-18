import bpy
g=bpy.data.objects['CCOM atrium glass (arched, 7x10 grid)']
m=g.data.materials[0]; print('MAT',m.name,m.users,[ (n.bl_idname) for n in m.node_tree.nodes])
p=[n for n in m.node_tree.nodes if n.bl_idname=='ShaderNodeBsdfPrincipled']
for n in p: print('PR',[(i.name,tuple(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value) for i in n.inputs if i.name in('Base Color','Roughness','Transmission Weight','Alpha','IOR','Metallic')])
print('SLOTS',[(s.link,s.material.name) for s in g.material_slots], 'users of mesh',g.data.users, 'nverts',len(g.data.vertices),'npolys',len(g.data.polygons))
W=g.matrix_world; vs=[W@v.co for v in g.data.vertices]
import statistics
pts=[(v.x,v.y) for v in vs]
my=statistics.mean(y for x,y in pts); mx=statistics.mean(x for x,y in pts)
b=sum((x-mx)*(y-my) for x,y in pts)/sum((y-my)**2 for x,y in pts); a=mx-b*my
res=[x-(a+b*y) for x,y in pts]; print('LINE x=a+b*y',a,b,'resid',min(res),max(res))
print('Z',min(v.z for v in vs),max(v.z for v in vs))
for n in ['CCOM entrance threshold','CCOM door frame -1','CCOM door stile -1-0.95','CCOM atrium arch frame']:
    o=bpy.data.objects[n]; print('OBJ',n,o.data.materials[0].name, len(o.data.vertices))
# objects of CCOM_interior_20261014v near front
for o in bpy.data.collections['CCOM_interior_20261014v'].all_objects:
    print('INT',o.name,o.hide_render,[round(c,2) for c in o.location])
