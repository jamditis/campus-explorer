# ws81f: undo ws81e flattening (pushed lot cells up to 25 cm under the lawn -> green bands through the lane): restore WS75/WS80 mesh data from the pre-ws81 backup
import bpy
src='/workspace/nj-scenes/montclair-state/montclair_state_pre_20261112ws81.blend'
N=['WS75_sprague_lot_asphalt_ortho2020_UNVERIFIED_edges','WS80_sprague_lot_fill_asphalt_ortho2020_UNVERIFIED_edges']
with bpy.data.libraries.load(src,link=False) as (fr,to): to.meshes=[bpy.data.objects[n].data.name for n in N]
for n,m in zip(N,to.meshes):
    o=bpy.data.objects[n]; old=o.data; mats=list(old.materials); o.data=m
    if not m.materials: [m.materials.append(x) for x in mats]
    print('WS81F restored',n[:20],len(m.vertices),[x.name for x in m.materials],flush=True)
    if old.users==0: bpy.data.meshes.remove(old)
bpy.ops.wm.save_mainfile(); print('WS81F SAVED',flush=True)
