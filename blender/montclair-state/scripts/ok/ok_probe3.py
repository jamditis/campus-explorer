import bpy
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']
for m in t.data.materials:
    print('MAT',m.name)
    for n in m.node_tree.nodes:
        extra=''
        if n.type=='TEX_IMAGE': extra=n.image.name if n.image else ''
        if n.type=='TEX_COORD' or n.type=='UVMAP': extra=getattr(n,'uv_map','')
        print('  N',n.type,n.name,extra,[ (s.name) for s in n.inputs if s.is_linked][:4])
print('uv',[u.name for u in t.data.uv_layers], 'mod',[m.type for m in t.modifiers])
