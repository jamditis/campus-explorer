import bpy
from mathutils import Vector
import os; X0,X1,Y0,Y1=[float(s) for s in os.environ["BOX"].split(",")]
for o in bpy.data.objects:
    if o.type!='MESH' or not o.data.vertices or len(o.data.vertices)>300000: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if min(v.x for v in bb)>X1 or max(v.x for v in bb)<X0 or min(v.y for v in bb)>Y1 or max(v.y for v in bb)<Y0: continue
    M=o.matrix_world; vs=[(i,M@v.co) for i,v in enumerate(o.data.vertices)]
    vs=[(i,w) for i,w in vs if X0<=w.x<=X1 and Y0<=w.y<=Y1]
    print('P222 OBJ %s hide_render %s nv_in %d'%(o.name,o.hide_render,len(vs)))
    for i,w in vs[:24]: print('P222   v%d (%.3f,%.3f,%.3f)'%(i,w.x,w.y,w.z))
