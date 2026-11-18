# ws73d: WS72 landing rows west of the WS27 curb_left start (x < ~-248, gap-strip curbs) got no raise in ws73c -> taper the raise to 0 over 4 m westward
import bpy,os
from collections import defaultdict
N='WS72_Kasser_SW_RHD_core_sidewalk_landing_UNVERIFIED_width'
with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/montclair_state_pre_20261111ws73.blend',link=False) as (fr,to): to.meshes=[bpy.data.objects[N].data.name]
om=to.meshes[0]; me=bpy.data.objects[N].data
d=defaultdict(list)
for a,b in zip(me.vertices,om.vertices): d[round(a.co.x,1)].append(a.co.z-b.co.z)
rd={x:max(v) for x,v in d.items()}
xs=sorted(rd); raised=[x for x in xs if rd[x]>0.001]; x0=min(raised); d0=rd[x0]
print('W73d rows',[(x,round(rd[x],3)) for x in xs])
n=0
for v in me.vertices:
    x=round(v.co.x,1)
    if x<x0 and rd[x]<=0.001:
        v.co.z+=d0*max(0,1-(x0-x)/4.0); n+=1
me.update(); bpy.data.meshes.remove(om)
print('W73d tapered verts',n,'x0',x0,'d0',round(d0,3),flush=True)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('W73d SAVED',flush=True)
