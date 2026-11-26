import bpy,os
with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/montclair_state.blend') as (a,b):
    print('MATS',[m for m in a.materials if any(k in m.lower() for k in ('pav','concrete','stair','step','wall','plaza','stone','brick'))])
    print('OBJS',[o for o in a.objects if any(k in o.lower() for k in ('lamp_acorn','feliciano','dickson','footpath','w63','ws251','ws250'))][:80])
os._exit(0)
