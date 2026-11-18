import bpy, os
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sc=bpy.context.scene; cam=bpy.data.objects[os.environ.get('CAM','QC_CAM_closeup_calcia_west_cornerbay')]; dg=bpy.context.evaluated_depsgraph_get()
fr=cam.data.view_frame(scene=sc); fr=[cam.matrix_world@v for v in fr]  # tr, br, bl, tl
o=cam.matrix_world.translation
for (px,py) in [tuple(map(float,s.split(':'))) for s in os.environ.get('PIX','440:60').split()]:
    x=px/640; y=py/360
    top=fr[3]+(fr[0]-fr[3])*x; bot=fr[2]+(fr[1]-fr[2])*x; p=top+(bot-top)*y
    hit,loc,nor,idx,ob,mx=sc.ray_cast(dg,o,(p-o).normalized())
    print('PICK',px,py,hit,ob and ob.name,tuple(round(v,2) for v in loc),'n',tuple(round(v,2) for v in nor),'face',idx, ob and ob.active_material and ob.data.materials[ob.data.polygons[idx].material_index].name if ob and ob.type=='MESH' else '')
for (px,py) in [(440,60),(400,90),(470,40)]:
    x=px/640; y=py/360; top=fr[3]+(fr[0]-fr[3])*x; bot=fr[2]+(fr[1]-fr[2])*x; p=top+(bot-top)*y; d=(p-o).normalized()
    for X in (-106.9,-106.3,-105.7):
        t=(X-o.x)/d.x; q=o+d*t; print('XING',px,py,X,tuple(round(v,2) for v in q))
w=bpy.data.objects['Calcia Hall walls']; me=w.data; uv=me.uv_layers['facade'].data
for p in me.polygons:
    c=w.matrix_world@p.center
    if 196<c.y<199.5 and c.x<-105 and abs(p.normal.z)<0.3:
        vv=[uv[l].uv[1] for l in p.loop_indices]; us=[uv[l].uv[0] for l in p.loop_indices]
        zs=[(w.matrix_world@me.vertices[me.loops[l].vertex_index].co).z for l in p.loop_indices]
        print('WF',p.index,tuple(round(v,2) for v in c),'n',tuple(round(v,2) for v in p.normal),'u %.2f-%.2f z %.2f-%.2f mi %d'%(min(us),max(us),min(zs),max(zs),p.material_index))
