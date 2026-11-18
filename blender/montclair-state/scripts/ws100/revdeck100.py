import bpy, numpy as np, os
bk='/workspace/nj-scenes/montclair-state/montclair_state_pre_20261112ws100.blend'
names=['COLE_plaza_deck_bs','COLE_plaza_edge_bs']
with bpy.data.libraries.load(bk) as (s,d): d.meshes=[bpy.data.objects[n].data.name for n in names]
for n,m in zip(names,d.meshes):
    o=bpy.data.objects[n]; me=o.data
    assert len(me.vertices)==len(m.vertices), n
    co=np.empty(len(m.vertices)*3); m.vertices.foreach_get('co',co); me.vertices.foreach_set('co',co); me.update(); print('R100 restored',n)
