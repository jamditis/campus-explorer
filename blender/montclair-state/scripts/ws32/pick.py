import bpy
from mathutils import Vector
from bpy_extras.view3d_utils import region_2d_to_vector_3d
sc=bpy.context.scene; c=bpy.data.objects['WS32_CAM_closeup_walk_apron_seam']
dg=bpy.context.evaluated_depsgraph_get()
fr=[c.matrix_world@v for v in c.data.view_frame(scene=sc)]  # tr, br, bl, tl
def ray(u,v):
    top=fr[3].lerp(fr[0],u); bot=fr[2].lerp(fr[1],u); p=top.lerp(bot,v)
    o=c.matrix_world.translation; d=(p-o).normalized()
    r=sc.ray_cast(dg,o,d)
    if r[0]:
        ob=r[4]; mi=r[3]; mat=''
        try:
            e=ob.evaluated_get(dg); mat=e.data.polygons[r[3]].material_index; mat=e.material_slots[mat].name if e.material_slots else ''
        except Exception as ex: mat='?'
        return ob.name, mat, tuple(round(x,2) for x in r[1])
for (px,py) in [(300,175),(260,178),(120,165),(400,200),(445,215),(330,230),(560,250)]:
    print('PICK',px,py,ray(px/640,py/360))
