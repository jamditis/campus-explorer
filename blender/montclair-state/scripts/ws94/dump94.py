import bpy,json
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
pre=('WS74_cogen_lot_asphalt','WS75_sprague_lot_asphalt','WS76_accessible_lot_asphalt','WS80_sprague_lot_fill','WS79_lot_E_patch','WS81_lot_seam_underlay','WS77')
with bpy.data.libraries.load(p) as (s,d): d.objects=[n for n in s.objects if n.startswith(pre) and 'CAM' not in n]
D={}
for o in d.objects:
    if o.type!='MESH': continue
    bpy.context.scene.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get()
for o in d.objects:
    if o.type!='MESH': continue
    me=o.evaluated_get(dg).to_mesh(); mw=o.matrix_world
    D[o.name]={'v':[list(mw@v.co) for v in me.vertices],'f':[list(p.vertices) for p in me.polygons],'mods':[m.type for m in o.modifiers]}
json.dump(D,open('scripts/ws94/dump94.json','w')); print('D94',list(D))
