# ws249 pass 6 (CHAIN on ws249e): t249.py put each 1 m LiDAR cell's mean at the cell's lower-left CORNER (x, y) instead of
# its CENTRE (x+0.5, y+0.5): a half-cell shift = ~0.3 m height error on the 0.6 m/m berm/embankment. Both WS249 targets'
# vertices move +0.5 m in x and y (z unchanged = the cell mean now sits at the cell centre, as in the ws248 patch).
import bpy
TAG='F249F'
for n in ('WS249_W_slope_LiDAR2023_ground_target','WS249_SE_berm_LiDAR2023_ground_target'):
    o=bpy.data.objects[n]
    if o.get('ws249f_centred'): continue
    for v in o.data.vertices: v.co.x+=0.5; v.co.y+=0.5
    o.data.update(); o['ws249f_centred']=1; print(TAG,n,'shifted',len(o.data.vertices),flush=True)
