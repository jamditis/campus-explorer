# ws50 combined main-file apply: ws49 crown rebuild + SE seam filler. Idempotent.
import bpy, os
os.environ['SAVE_OUTER']=os.environ.get('SAVE','0'); os.environ['SAVE']='0'
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws49/crown.py').read())
if 'WS50_SE_seam_filler' not in bpy.data.objects:
    with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/data/ws50/se_seam_filler.blend',link=False) as (s,d): d.objects=['WS50_SE_seam_filler']
    f=d.objects[0]; t=bpy.data.objects['Terrain_LiDAR_DTM_1m']
    for c in t.users_collection: c.objects.link(f)
    if t.data.materials: f.data.materials.append(t.data.materials[0])
    f.use_fake_user=False
print('A50 filler', 'WS50_SE_seam_filler' in bpy.data.objects, [m.name for m in bpy.data.objects['WS50_SE_seam_filler'].data.materials])
if os.environ['SAVE_OUTER']=='1': bpy.ops.wm.save_mainfile(); print('C49 saved'); print('A50 saved')
