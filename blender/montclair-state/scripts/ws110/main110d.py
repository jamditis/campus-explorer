# brick-paver crosswalk band across the College Ave mouth (2020 ortho: red band y ~ -256..-258 at the centreline)
import bpy, numpy as np
ob=next(o for o in bpy.data.objects if o.name.startswith('WS110_CollegeAve_S_end_to_NormalAve'))
me=ob.data; brick=bpy.data.materials['WS27_brick_crosswalk_2020ortho']
if brick.name not in [m.name for m in me.materials]: me.materials.append(brick)
mi=[m.name for m in me.materials].index(brick.name)
Tc=24.18; nrow=int(np.ceil(Tc/0.5)); ncol=13
n=0
for i in range(nrow):
    kc=(i+0.5)/nrow*Tc
    if 13.9<=kc<=16.0:
        for j in range(ncol): me.polygons[i*ncol+j].material_index=mi; n+=1
print('E110d brick faces',n,'of',len(me.polygons))
bpy.ops.wm.save_mainfile(); print('M110 SAVED d',flush=True)
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws105/cut105.py').read().replace('ws105/render_cut105','ws110/render_cut110'))
