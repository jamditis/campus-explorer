import bpy, bmesh
from mathutils import Vector
o=[o for o in bpy.data.objects if o.name.startswith('el coping strips School of Communication and Media')][0]
print('OBJ',o.name,len(o.data.polygons),o.data.users)
mw=o.matrix_world; bm=bmesh.new(); bm.from_mesh(o.data); bm.faces.ensure_lookup_table()
seen={296}; st=[bm.faces[296]]; isl=[]
while st:
    g=st.pop(); isl.append(g)
    for e in g.edges:
        for h in e.link_faces:
            if h.index not in seen: seen.add(h.index); st.append(h)
vs=[mw@v.co for v in {v for g in isl for v in g.verts}]
print('ISL',len(isl),[round(min(v[i] for v in vs),2) for i in range(3)],[round(max(v[i] for v in vs),2) for i in range(3)])
n=Vector((-0.972,0.232,0)).normalized(); t=Vector((0.232,0.972,0)).normalized()
print('UW',round(min(v.dot(t) for v in vs),2),round(max(v.dot(t) for v in vs),2),round(min(v.dot(n) for v in vs),2),round(max(v.dot(n) for v in vs),2))
