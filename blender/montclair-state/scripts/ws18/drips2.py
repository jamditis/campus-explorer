import bpy,os
from mathutils import Vector
mat=bpy.data.materials['WS18_sill_drip_stain_UNVERIFIED']; nt=mat.node_tree
for n in nt.nodes:
    if n.type=='MAP_RANGE': n.inputs['From Min'].default_value=0.38; n.inputs['From Max'].default_value=0.62
    if n.type=='MATH' and n.operation=='MULTIPLY' and not n.inputs[1].is_linked: n.inputs[1].default_value=0.6
    if n.type=='MATH' and n.operation=='POWER': n.inputs[1].default_value=1.3
ob=bpy.data.objects['WS18_Cole_add_east_sill_drip_stains_UNVERIFIED']
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
cam=Vector((-86.5,-79.5,136.6))
for p in ob.data.polygons:
    c=ob.matrix_world@p.center; d=(c-cam).normalized()
    h=sc.ray_cast(dg,cam,d); print('RAY',h[0] and h[4].name, round((h[1]-c).length,3))
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
