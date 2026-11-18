import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
cam=bpy.data.objects['WA1_CAM_eye_stone_footway_from_N']
print('CAM',tuple(round(c,2) for c in cam.matrix_world.translation), cam.data.lens)
# rays through lower-right foreground pixels
import math
fr=cam.data.view_frame(scene=sc)
def ray(u,v):
    tr,br,bl,tl=fr
    p=bl+(br-bl)*u+(tl-bl)*v
    o=cam.matrix_world.translation; d=(cam.matrix_world.to_3x3()@p).normalized()
    return sc.ray_cast(dg,o,d)
for u,v in [(0.7,0.1),(0.8,0.2),(0.9,0.3),(0.75,0.35),(0.95,0.05)]:
    r=ray(u,v)
    if r[0]:
        ob=r[4]; mat=ob.material_slots[ob.data.polygons[r[3]].material_index].material.name if ob.type=='MESH' and ob.material_slots and r[3]<len(ob.data.polygons) else None
        print('HIT',u,v,ob.name,mat,tuple(round(c,2) for c in r[1]), round((r[1]-cam.matrix_world.translation).length,1))
g=bpy.data.objects.get('QS_Richardson_lawn_grass_points_UNVERIFIED')
print('GRASS',g.type,len(g.data.vertices))
for m in g.modifiers:
    print(' MOD',m.type,m.name, getattr(m,'node_group',None) and m.node_group.name)
    if m.type=='NODES':
        for k,v in m.items(): print('   ',k,v if not hasattr(v,'name') else v.name)
        for n in m.node_group.nodes: print('   N',n.bl_idname,n.name,[ (i.name,getattr(i,'default_value',None) if not hasattr(getattr(i,'default_value',None),'__len__') else tuple(i.default_value)) for i in n.inputs if not i.is_linked and hasattr(i,'default_value')][:6])
