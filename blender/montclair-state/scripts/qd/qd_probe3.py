import bpy
from mathutils import Vector
sc=bpy.context.scene; cam=bpy.data.objects['PE_CAM_eye_calcia_west']; dg=bpy.context.evaluated_depsgraph_get()
fr=[cam.matrix_world@v for v in cam.data.view_frame(scene=sc)]; o=cam.matrix_world.translation
for (px,py) in [(500,520),(300,470),(800,550),(100,430),(600,450)]:
    x=px/1024; y=py/576; top=fr[3]+(fr[0]-fr[3])*x; bot=fr[2]+(fr[1]-fr[2])*x; p=top+(bot-top)*y
    h=sc.ray_cast(dg,o,(p-o).normalized())
    ob=h[4]; idx=h[3]
    mat=None
    if ob and ob.type=='MESH':
        e=ob.evaluated_get(dg).data
        if idx<len(e.polygons): mat=e.materials[e.polygons[idx].material_index].name if e.materials else None
    print('PR',px,py,ob and ob.name,idx,mat,tuple(round(v,3) for v in h[1]),tuple(round(v,2) for v in h[2]))
