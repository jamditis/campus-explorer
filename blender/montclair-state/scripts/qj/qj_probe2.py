import bpy
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
for cn,pts in (('QJ_CAM_eye_NE_seam_from_west',[(0.5,0.25),(0.3,0.2),(0.7,0.3),(0.5,0.4)]),('QJ_CAM_closeup_NE_seam',[(0.5,0.2),(0.7,0.3),(0.8,0.55),(0.65,0.52),(0.2,0.25),(0.3,0.4)]),('QJ_CAM_eye_NE_seam_from_east',[(0.62,0.48),(0.75,0.5),(0.4,0.45)])):
    c=sc.objects[cn]; fr=c.data.view_frame(scene=sc); M=c.matrix_world; o=M.translation
    for u,v in pts:  # u left->right, v bottom->top
        tl,bl=fr[3],fr[2]; tr,br=fr[0],fr[1]
        p=bl.lerp(br,u).lerp(tl.lerp(tr,u),v); d=(M@p-o).normalized()
        r=sc.ray_cast(dg,o,d)
        print('HIT',cn,u,v,r[0] and r[4].name, r[0] and tuple(round(x,1) for x in r[1]), r[0] and r[3], 'mat', r[0] and (r[4].material_slots[r[4].data.polygons[r[3]].material_index].name if r[4].type=='MESH' and r[3]<len(r[4].data.polygons) and r[4].material_slots else None))
