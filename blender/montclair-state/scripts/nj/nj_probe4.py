import bpy, mathutils, bmesh
def bb(o):
    cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]
    return [round(min(c[i] for c in cs),2) for i in range(3)],[round(max(c[i] for c in cs),2) for i in range(3)]
def mat(n):
    m=bpy.data.materials.get(n)
    if not m: print('NOMAT',n); return
    print('MAT',n,'users',m.users)
    for nd in m.node_tree.nodes:
        ins={i.name:(tuple(round(x,3) for x in i.default_value) if hasattr(i.default_value,'__len__') else round(i.default_value,3)) for i in nd.inputs if hasattr(i,'default_value') and not i.is_linked and i.name in ('Base Color','Roughness','IOR','Alpha','Transmission Weight','Color','Scale','Fac','Strength','Emission Strength','Specular IOR Level','Coat Weight')}
        print('  ND',nd.type,nd.name,ins)
for n in ['NG_wall_white','NG_terrazzo_1F_open_floor','NH_terrazzo_1F_tone_variation_UNVERIFIED','NG_red_wall','NG_maroon_frame','NG_ceiling_white','NG_led_strip','NG_frosted_glass']: mat(n)
for o in bpy.data.objects:
    if o.hide_render: continue
    if o.name.startswith('CCOM atrium glass') or 'stair' in o.name.lower() and o.name.startswith(('NG','NH')) or o.name.startswith('Downspout boots') or ('red wall' in o.name.lower()) or ('maroon door' in o.name.lower()) or o.name.startswith('NG') and 'door' in o.name.lower():
        print('OB|%s|%s|%s|%s'%(o.name,bb(o),[s.material.name if s.material else None for s in o.material_slots],[s.link for s in o.material_slots]))
for o in bpy.data.objects:
    if o.type=='MESH' and any(s.material and s.material.name=='NG_led_strip' for s in o.material_slots): print('LED|',o.name,bb(o))
o=bpy.data.objects['Downspout boots + drain grates (3g, CCOM)']
bm=bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
seen=set(); M=o.matrix_world
for v in bm.verts:
    if v.index in seen: continue
    st=[v]; isl=[]
    seen.add(v.index)
    while st:
        x=st.pop(); isl.append(x)
        for e in x.link_edges:
            y=e.other_vert(x)
            if y.index not in seen: seen.add(y.index); st.append(y)
    ps=[M@x.co for x in isl]
    c=sum(ps,mathutils.Vector())/len(ps)
    print('ISL',len(isl),[round(a,2) for a in c],round(min(p.z for p in ps),2),round(max(p.z for p in ps),2))
for o in bpy.data.objects:
    if o.name.lower().startswith('downspout') or 'downpipe' in o.name.lower():
        lo,hi=bb(o)
        if hi[0]>-22 and lo[0]<-15 and hi[1]>5 and lo[1]<15: print('DSP|',o.name,lo,hi,o.hide_render)
