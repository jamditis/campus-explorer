import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
for x,y in [(-69.7,-68.8),(-69.2,-69.0),(-70.3,-68.5),(-68.0,-69.4)]:
    o=Vector((x,y,170)); hs=[]
    for i in range(10):
        r=sc.ray_cast(dg,o,Vector((0,0,-1)))
        if not r[0]: break
        ob=r[4]; ms=''
        try: ms=ob.material_slots[ob.data.polygons[r[3]].material_index].name if ob.type=='MESH' and r[3]<len(ob.data.polygons) else '(gn)'
        except Exception: ms='?'
        hs.append((ob.name[:34],ms[:28],round(r[1].z,3)))
        if ob.name.startswith('Terrain'): break
        o=r[1]+Vector((0,0,-0.001))
    print('PX',x,y,[h for h in hs if not h[0].startswith(('T_','gt_'))])
