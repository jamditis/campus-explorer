import bpy, json
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
names=['WS27_CollegeAve_carriageway_2020ortho']
with bpy.data.libraries.load(p) as (s,d): d.objects=names
o=d.objects[0]; bpy.context.scene.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get(); dg.update()
e=o.evaluated_get(dg); m=e.to_mesh(); mw=o.matrix_world
print('MODS',[(x.type,x.name) for x in o.modifiers])
json.dump([[ (mw@v.co).x,(mw@v.co).y,(mw@v.co).z] for v in m.vertices],open('/workspace/nj-scenes/montclair-state/scripts/ws100/cw100.json','w'))
