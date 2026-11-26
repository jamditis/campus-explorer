# ws248 W62g pass 2 (CHAIN on ws248b): add the LiDAR ground patch E of the east stand, keep the fan terrain 0.3 m under it,
# re-drape the back walk on LiDAR (flat ~134.1-134.6, level with the stand pad), joints + edge-face material (f248 parts 2-3).
import bpy, json, numpy as np
TAG='F248C'; PN='WS248_E_stand_LiDAR2023_ground_patch_1m'; WN='WS247_E_stand_back_walk_ortho2020_UNVERIFIED_level'
J=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws248/h248p.json'))
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']
if PN not in bpy.data.objects:
    me=bpy.data.meshes.new(PN); me.from_pydata(J['V'],[],[tuple(f) for f in J['F']]); me.validate(); me.update()
    for p in me.polygons: p.use_smooth=True
    me.materials.append(T.data.materials[J['mslot']])
    uv=me.uv_layers.new(name='ortho')
    for p in me.polygons:
        for li in p.loop_indices: uv.data[li].uv=J['UV'][me.loops[li].vertex_index]
    o=bpy.data.objects.new(PN,me)
    for c in T.users_collection: c.objects.link(o)
    print(TAG,'patch',PN,len(me.vertices),len(me.polygons),me.materials[0].name,[c.name for c in o.users_collection],flush=True)
# fan terrain under the patch: target 0.3 m below LiDAR for x > -224.5 (dense snapped terrain W of that stays exact)
tg=bpy.data.objects['WS248_E_stand_LiDAR2023_ground_target']; n=0
if not tg.get('ws248c_lowered'):
    for v in tg.data.vertices:
        if v.co.x>-224.5 and 45<v.co.y<135: v.co.z-=0.3; n+=1
    tg['ws248c_lowered']=1
print(TAG,'target verts lowered',n,flush=True)
# walk mesh replaced (same object, same row layout as h247)
wk=bpy.data.objects[WN]; old=wk.data
me=bpy.data.meshes.new(WN); me.from_pydata(J['WV'],[],[tuple(f) for f in J['WF']]); me.update()
for p in me.polygons: p.use_smooth=False
wk.data=me; bpy.data.meshes.remove(old)
uv=me.uv_layers.new(name='UVMap')
for p in me.polygons:
    for li in p.loop_indices:
        v=me.vertices[me.loops[li].vertex_index].co; uv.data[li].uv=(v.x/2.0,v.y/2.0)
print(TAG,'walk replaced',len(me.vertices),len(me.polygons),flush=True)
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws248/f248_joints.py').read())
