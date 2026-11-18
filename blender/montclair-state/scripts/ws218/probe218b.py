import bpy, json
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws189/alloff189.py').read())
bpy.ops.wm.open_mainfile(filepath='/workspace/nj-scenes/montclair-state/north/montclair_north.blend',load_ui=False)
man=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws217/north_manifest217.json'))
want=[n for n,v in man.items() if (v[0] in ('APPEND','NONMESH_EMPTY') or n.startswith('UH ground-floor lobby glazing')) and (n.startswith(('UH','OF','University Hall')) or "Children" in n)]
def walk(lc,acc):
    acc[lc.collection.name]=(lc.exclude,lc.hide_viewport,lc.collection.hide_render)
    for c in lc.children: walk(c,acc)
acc={}; walk(bpy.context.view_layer.layer_collection,acc)
vis={}
for n in want:
    o=bpy.data.objects[n]
    eff=o.hide_render or all(acc.get(c.name,(True,))[0] or acc.get(c.name,(0,0,False))[2] for c in o.users_collection)
    # parent collection chain exclude
    vis[n]=bool(eff)
hid=[n for n,v in vis.items() if v]
print('P218B hidden-in-north',len(hid),hid[:40],flush=True)
json.dump(hid,open('/workspace/nj-scenes/montclair-state/scripts/ws218/north_hidden218.json','w'))
print('P218B colls',{c:acc.get(c) for c in set(c.name for n in want for c in bpy.data.objects[n].users_collection)},flush=True)
