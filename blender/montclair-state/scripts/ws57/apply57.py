import bpy
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws57/lift2.py').read())
src=open('/workspace/nj-scenes/montclair-state/scripts/ws57/local_seat.py').read().split('for n,cx,cy in SPOTS:')[0]
exec(src)
for n,cx,cy in SPOTS: print('L57 main after',n,measure(n,cx,cy))
bpy.ops.wm.save_mainfile(); print('L57 saved')
