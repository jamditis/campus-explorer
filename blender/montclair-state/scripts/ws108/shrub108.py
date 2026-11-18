import bpy
tex=bpy.data.textures.get('WS108_shrub_leaf_clumps') or bpy.data.textures.new('WS108_shrub_leaf_clumps','VORONOI')
tex.noise_scale=0.22; tex.distance_metric='DISTANCE'
n=0; meshes=set()
for o in bpy.data.objects:
    if o.type=='MESH' and (o.name.startswith('WS99_bed_shrub_') or o.name.startswith('WS105_bank_shrub_')):
        for m in [m for m in o.modifiers if m.name.startswith('WS108_')]: o.modifiers.remove(m)
        s=o.modifiers.new('WS108_subsurf','SUBSURF'); s.levels=1; s.render_levels=2
        d=o.modifiers.new('WS108_leaf_clumps','DISPLACE'); d.texture=tex; d.strength=0.07; d.mid_level=0.5; d.texture_coords='GLOBAL'
        meshes.add(o.data); n+=1
for me in meshes:
    for p in me.polygons: p.use_smooth=True
print('S108 shrubs',n,'meshes',len(meshes))
bpy.ops.wm.save_mainfile(); print('S108 SAVED',flush=True)
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws105/cut105.py').read().replace('ws105/render_cut105','ws108/render_cut108'))
