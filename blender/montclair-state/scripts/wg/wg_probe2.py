import bpy
o=bpy.data.objects['QY_walk_junction_wear_decals_UNVERIFIED']; me=o.data
print('OBJ',len(me.vertices),len(me.polygons),'attrs',[ (a.name,a.domain,a.data_type) for a in me.attributes],'uv',[u.name for u in me.uv_layers],'mods',[m.type for m in o.modifiers],'loc',tuple(o.location),'dims',tuple(o.dimensions), 'coll',[c.name for c in o.users_collection])
import numpy as np
P=np.array([o.matrix_world@v.co for v in me.vertices]); print('BB',P.min(0),P.max(0))
# islands
import bmesh
bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
seen=set(); isl=[]
for f in bm.faces:
    if f.index in seen: continue
    st=[f]; cnt=0; seen.add(f.index); cs=[]
    while st:
        g=st.pop(); cnt+=1; cs.append(g.calc_center_median())
        for e in g.edges:
            for h in e.link_faces:
                if h.index not in seen: seen.add(h.index); st.append(h)
    c=sum(cs,type(cs[0])())/len(cs); isl.append((cnt,tuple(round(x,1) for x in (o.matrix_world@c))))
print('ISLANDS',len(isl)); [print(' I',i) for i in isl[:40]]
ar=[f.calc_area() for f in bm.faces]; print('face area med',np.median(ar),'min',min(ar),'max',max(ar))
m=o.active_material; nt=m.node_tree
print('MAT',m.name,'blend',getattr(m,'blend_method',None),'surface_render_method',getattr(m,'surface_render_method',None))
for n in nt.nodes:
    ex=''
    if n.type=='TEX_IMAGE' and n.image: ex=f' img={n.image.name} {tuple(n.image.size)} {n.interpolation}'
    vals=[(i.identifier,round(i.default_value,3) if isinstance(i.default_value,float) else None) for i in n.inputs if not i.is_linked and hasattr(i,'default_value') and isinstance(getattr(i,'default_value',None),float)]
    print(' N',n.name,n.type,ex,vals[:8], getattr(n,'attribute_name',''), getattr(n,'blend_type',''), getattr(n,'operation',''))
for l in nt.links: print(' L',l.from_node.name,l.from_socket.identifier,'->',l.to_node.name,l.to_socket.identifier)
