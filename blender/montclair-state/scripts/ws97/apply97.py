import bpy,json,os
R=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws97/edge97.json'))['raise']
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; imw=T.matrix_world.inverted(); mw=T.matrix_world
for i,d in R:
    v=T.data.vertices[i]; w=mw@v.co; w.z+=d; v.co=imw@w
T.data.update(); print("A97 terrain raised",len(R))
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print("A97 SAVED")
