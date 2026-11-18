# ws22: court north of Life Hall (between Life and the Schmitt entrance walk): the 2020 ortho shows grey paving there,
# rendered as blurry ortho drape with jagged baked lines. Assign the WS3 sawcut concrete panel slot to those patch faces (UNVERIFIED extent from ortho tone, 1 m cells, majority-filtered).
import bpy,json,os
o=bpy.data.objects['QG_north_strip_LiDAR_terrain_patch']; me=o.data
slot=[i for i,s in enumerate(o.material_slots) if s.material and s.material.name=='WS3_Concrete_panels_sawcut'][0]
ids=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws22/court_faces.json'))
a=me.attributes.get('ws22_orig_mat') or me.attributes.new('ws22_orig_mat','INT','FACE')
for p in me.polygons: a.data[p.index].value=p.material_index
for i in ids: me.polygons[i].material_index=slot
me.update(); print('ASSIGNED',len(ids),'slot',slot)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
