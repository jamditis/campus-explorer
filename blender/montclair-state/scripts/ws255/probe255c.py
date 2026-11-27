import sys; sys.stdout.reconfigure(line_buffering=True)
import bpy, os
F=os.environ.get('F','/workspace/nj-scenes/montclair-state/montclair_state_ws255a.blend')
with bpy.data.libraries.load(F) as (a,b): b.objects=['PI_Feliciano_east_base_course_UNVERIFIED']
o=b.objects[0]; M=o.matrix_world
for p in o.data.polygons:
    ws=[M@o.data.vertices[i].co for i in p.vertices]
    if max(w.x for w in ws)>-198.5 and 169<min(w.y for w in ws)<174.5 or (max(w.x for w in ws)>-198.5 and 169<max(w.y for w in ws)<174.5):
        print('P255C',p.index,' '.join('(%.2f,%.2f,%.2f)'%(w.x,w.y,w.z) for w in ws))
os._exit(0)
