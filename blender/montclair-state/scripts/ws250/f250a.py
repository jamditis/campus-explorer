# ws250 (CHAIN via ws208/merge208.py): UNIFY W63 — ground N of the soccer field's east stand, between Feliciano's east face,
# Dickson Hall's north end and the lawn S of University Hall. Main terrain there was 0.6-1.3 m BELOW the 2023 and 2017 LiDAR
# (which agree to ~0.12 m) on the lawn/plaza y 166..210 (LiDAR trees already stood 0.8 m above it), and up to 2.2 m ABOVE on the
# Feliciano/Dickson passage slope y 142..166. Same raycast snap GN as ws248/ws249 (attr w250), after WS249_SE_berm snap.
# University Hall (Wyndle's) is not in main and its footprint (y>=221) is outside the box: untouched.
import bpy
J='/workspace/nj-scenes/montclair-state/scripts/ws250/'
_src=open('/workspace/nj-scenes/montclair-state/scripts/ws249/f249a.py').read().split('PK=bpy.data.objects')[0]
_src=_src.replace("TAG='F249A'","TAG='F250A'").replace("J='/workspace/nj-scenes/montclair-state/scripts/ws249/'","J='%s'"%J).replace("'w249'","'w250'")
exec(_src)
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; ref=bpy.data.objects['WS248_E_stand_LiDAR2023_ground_target']
tg=target('WS250_W63_LiDAR2023_ground_target','t250.json',ref); tg.hide_render=True
snap(T,'WS250_W63_LiDAR_terrain_snap',tg,after='WS249_SE_berm_LiDAR_terrain_snap')
