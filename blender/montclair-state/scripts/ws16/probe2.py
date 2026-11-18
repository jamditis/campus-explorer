import bpy, collections
o=bpy.data.objects['TZ_Cole_north_addition_UNVERIFIED']; mw=o.matrix_world; me=o.data
st=collections.defaultdict(list)
for p in me.polygons:
    c=mw@p.center; st[p.material_index].append((c,p.area,p.normal))
for mi,l in st.items():
    zs=[c.z for c,a,n in l]; A=sum(a for c,a,n in l)
    print('MI',mi,o.material_slots[mi].material.name,len(l),'area',round(A,1),'z',round(min(zs),2),round(max(zs),2))
# roof faces details near eave
for c,a,n in st[1][:0]: pass
o2=bpy.data.objects['Cole Hall 2020 north addition (LiDAR footprint/eave/ridge MEASU'] if 'Cole Hall 2020 north addition (LiDAR footprint/eave/ridge MEASU' in bpy.data.objects else None
for ob in bpy.data.objects:
    if ob.name.startswith('Cole Hall 2020 north addition'):
        print('ADD2',ob.name,'hide',ob.hide_render,[round(v,1) for v in ob.matrix_world.translation], ob.dimensions[:])
print('TZ',o.hide_render,o.dimensions[:])
