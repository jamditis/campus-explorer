# ws89: swap the 5 WS88 mannequin statues for walking-pose Segal-style figures (assets/ws89_segal_walkers.blend); old ones hidden, not deleted
import bpy,os
OB=bpy.data.objects
old=sorted([o for o in OB if o.name.startswith('WS88_Cole_statue_INNER_arc')],key=lambda o:o.name)
for o in [o for o in OB if o.name.startswith('WS89_Segal_walker')]: OB.remove(o)
with bpy.data.libraries.load('/workspace/nj-scenes/assets/ws89_segal_walkers.blend') as (s,d):
    d.objects=sorted([n for n in s.objects if n.startswith('WS89_Segal_walker')])
col=old[0].users_collection[0]
for o,w in zip(old,d.objects):
    col.objects.link(w); w.location=o.location.copy(); w.location.z=o.location.z+0.005; w.rotation_euler=o.rotation_euler.copy()
    w.name=w.name+'_INNER_arc_JOE20261112_UNVERIFIED_pose'
    o.hide_render=True; o.hide_viewport=True
    print('W89',w.name[:40],tuple(round(v,2) for v in w.location))
bpy.ops.wm.save_mainfile(); print('W89 saved')
