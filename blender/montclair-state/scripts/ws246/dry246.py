import bpy, os
S='/workspace/nj-scenes/montclair-state/'
N=['Terrain_LiDAR_DTM_1m','WS243_stands_pitch_holdunder_target','WS245_E_bank_grade_target_UNVERIFIED','fse_stand_under_pad','fr_stand_under_pad','fs_turf','fse_front_walkway','fr_front_walkway','PZ_Feliciano_SW_DTM_edge_feather_UNVERIFIED','Context_skirt_3DEP_ortho_4km']
with bpy.data.libraries.load(S+os.environ.get('SRC','montclair_state.blend')) as (a,b): b.objects=N
for o in b.objects: bpy.context.scene.collection.objects.link(o)
os.environ['DRY']='1'; exec(open(S+'scripts/ws246/'+os.environ.get('FX','f246a.py')).read()); os._exit(0)
