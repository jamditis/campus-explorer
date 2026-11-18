import bpy, os
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
def gz(x,y):
    r=sc.ray_cast(dg,Vector((x,y,400)),Vector((0,0,-1)))
    return r[1].z if r[0] else 0
for o in sc.objects:
    if 'tree' in o.name.lower() or 'canopy' in o.name.lower() or o.name.startswith(('WS163_skirt_target','WS167_skirt_target','WS113_paving_tops','Context_skirt','BD_farfield')) or o.type!='MESH': o.hide_viewport=True
dg.update()
lx,ly,tx,ty=-313.0,-239.0,-292.0,-236.0
L=Vector((lx,ly,gz(lx,ly)+1.7)); T=Vector((tx,ty,118.8))
c=bpy.data.objects.new('P',bpy.data.cameras.new('P')); sc.collection.objects.link(c); c.location=L; c.data.lens=26
c.rotation_euler=(T-L).to_track_quat('-Z','Y').to_euler(); sc.render.resolution_x=1280; sc.render.resolution_y=720; bpy.context.view_layer.update()
fr=[c.matrix_world@v for v in c.data.view_frame(scene=sc)]  # tr, br, bl, tl
print('CAM',L,T)
for px,py in [(340,205),(330,207),(350,204),(700,250),(690,248),(100,232),(150,228)]:
    u=px/768; v=py/432
    top=fr[3].lerp(fr[0],u); bot=fr[2].lerp(fr[1],u); p=top.lerp(bot,v)
    d=(p-L).normalized(); r=sc.ray_cast(dg,L,d)
    print('PICK',px,py,r[0], r[4].name if r[0] else None, tuple(round(a,2) for a in r[1]) if r[0] else None, tuple(round(a,2) for a in r[2]) if r[0] else None,flush=True)
