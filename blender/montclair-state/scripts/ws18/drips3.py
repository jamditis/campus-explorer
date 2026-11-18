import bpy,os
from mathutils import Vector
ob=bpy.data.objects['WS18_Cole_add_east_sill_drip_stains_UNVERIFIED']; me=ob.data; M=ob.matrix_world; Mi=M.inverted()
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
cam=Vector((-86.5,-79.5,136.6))
ob.hide_set(True); ob.hide_render=True; dg.update()
for p in me.polygons:
    c=M@p.center; n=(M.to_3x3()@p.normal).normalized(); n.z=0; n.normalize()
    if n.dot(cam-c)<0: n=-n   # outward toward the courtyard/camera
    h=sc.ray_cast(dg,c+n*0.6,-n)   # from outside back to the wall face
    if not h[0]: print('nohit'); continue
    t=(h[1]-c).dot(n)+0.004
    print('shift',p.index,h[4].name,round(t,3))
    for vi in p.vertices:
        w=M@me.vertices[vi].co; w+=n*t; me.vertices[vi].co=Mi@w
ob.hide_set(False); ob.hide_render=False; me.update()
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
