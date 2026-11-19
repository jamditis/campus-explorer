# W53e (ws229): the "flat grey sheet" in the SE eye view is the terrain's ortho texture mis-registered. The base terrain's
# 'ortho' UV map is exactly u = x/500 + 0.5, v = y/500 + 0.5 over the central/NE terrain (probe229g: lstsq residual 99th pct
# < 0.0003), but in the SE quadrant (x >= 25, y <= -25) the UVs came from the old giant interpolated faces (and ws227/ws228
# re-grids copied those faces' affine UVs), so the 2020 ortho there is displaced by a median 8.6 m and up to ~32 m (street
# asphalt and roofs painted across lawns: the grey sheet). Every loop of a Terrain_LiDAR_DTM_1m face whose centre is in that
# quadrant and whose UV is > 0.5 m off the global mapping is reset to the global mapping. Geometry untouched.
import bpy, json, numpy as np
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=t.data; uv=me.uv_layers['ortho'].data
n=0; offs=[]
for p in me.polygons:
    c=p.center
    if c.x<25 or c.y>-25: continue
    for li in p.loop_indices:
        v=me.vertices[me.loops[li].vertex_index].co
        gu=v.x/500+0.5; gv=v.y/500+0.5; e=((uv[li].uv[0]-gu)**2+(uv[li].uv[1]-gv)**2)**0.5*500
        if e>0.5: offs.append(e); uv[li].uv=(gu,gv); n+=1
me.update()
rep={'loops_reset':n,'mean_off_m':round(float(np.mean(offs)) if offs else 0,2),'max_off_m':round(max(offs or [0]),2)}
print('F229D',json.dumps(rep),flush=True)
json.dump(rep,open('/workspace/nj-scenes/montclair-state/scripts/ws229/fix229d_report.json','w'))
