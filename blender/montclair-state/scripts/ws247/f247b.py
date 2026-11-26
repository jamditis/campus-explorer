# ws247 W62e pass 2: add the east-stand back walk from h247.json (Paving_concrete, same collection as Footpaths_OSM)
import bpy, json
TAG='F247B'; NM='WS247_E_stand_back_walk_ortho2020_UNVERIFIED_level'
J=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws247/h247.json'))
if NM in bpy.data.objects: print(TAG,'exists, skip',flush=True)
else:
    me=bpy.data.meshes.new(NM); me.from_pydata(J['V'],[],J['F']); me.validate(); me.update()
    for p in me.polygons: p.use_smooth=False
    fp=bpy.data.objects['Footpaths_OSM']; me.materials.append(bpy.data.materials['Paving_concrete'])
    o=bpy.data.objects.new(NM,me)
    for c in fp.users_collection: c.objects.link(o)
    uv=me.uv_layers.new(name='UVMap')
    for p in me.polygons:
        for li in p.loop_indices:
            v=me.vertices[me.loops[li].vertex_index].co; uv.data[li].uv=(v.x/2.0,v.y/2.0)
    print(TAG,'added',NM,len(me.vertices),len(me.polygons),'colls',[c.name for c in o.users_collection],flush=True)
