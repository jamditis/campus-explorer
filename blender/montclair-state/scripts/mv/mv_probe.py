# Session mv: list every mesh with verts in the S corner of the CCOM entrance gable (rake-tip points)
import bpy
from mathutils import Vector
n=Vector((-0.972,0.232,0)).normalized(); t=Vector((0.232,0.972,0)).normalized()
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if max(v.z for v in bb)<146.0 or min(v.z for v in bb)>148.6: continue
    if max(v.dot(n) for v in bb)<20.0 or min(v.dot(n) for v in bb)>24.5: continue
    if min(v.dot(t) for v in bb)>3.6 or max(v.dot(t) for v in bb)<1.0: continue
    mw=o.matrix_world
    vs=[mw@v.co for v in o.data.vertices]
    sel=[v for v in vs if 1.0<v.dot(t)<3.6 and 146.0<v.z<148.6 and 20.0<v.dot(n)<24.5]
    if not sel: continue
    print('OBJ',repr(o.name),'nv',len(o.data.vertices),'sel',len(sel),'mats',[m.name if m else None for m in o.data.materials][:3],
      'u',round(min(v.dot(t) for v in sel),3),round(max(v.dot(t) for v in sel),3),
      'w',round(min(v.dot(n) for v in sel),3),round(max(v.dot(n) for v in sel),3),
      'z',round(min(v.z for v in sel),3),round(max(v.z for v in sel),3), 'cols',[c.name for c in o.users_collection])
print('COUNT',len(bpy.data.objects))
