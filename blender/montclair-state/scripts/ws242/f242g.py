# ws242: faces added this session to M3a/M3b (W60 flap, W59b gap fill, W59c flaps) sample the north 2020 ortho/paving mask
# outside its useful extent (DTM no-data / beyond the tile) and render pale grey. Put every face that touches a new vertex
# (vs the pre-ws242 mesh) on the tile's own lawn slot (gd_grass_lawn*), the procedural campus lawn.
import bpy
from mathutils import Vector
from mathutils.kdtree import KDTree
PRE='/workspace/nj-scenes/montclair-state/montclair_state_pre_20261125ws242.blend'
for tgt in [x for x in bpy.data.objects if x.name.startswith(('M3a_north_LiDAR_DTM_1m','M3b_north_LiDAR_DTM_1m')) and not x.library]:
    slot=[i for i,m in enumerate(tgt.data.materials) if m and m.name.startswith('gd_grass_lawn')]
    if not slot: print('F242G no lawn slot',tgt.name,[m.name for m in tgt.data.materials if m]); continue
    with bpy.data.libraries.load(PRE) as (a,b): b.meshes=[]; b.objects=[tgt.name]
    old=b.objects[0].data; kd=KDTree(len(old.vertices))
    for i,v in enumerate(old.vertices): kd.insert(Vector((v.co.x,v.co.y,0)),i)
    kd.balance(); me=tgt.data
    new=set(i for i,v in enumerate(me.vertices) if kd.find(Vector((v.co.x,v.co.y,0)))[2]>1e-3)
    k=0
    for p in me.polygons:
        if any(vi in new for vi in p.vertices): p.material_index=slot[0]; k+=1
    me.update(); bpy.data.objects.remove(b.objects[0])
    print('F242G',tgt.name[:12],'faces to lawn',k,'slot',slot[0],flush=True)
