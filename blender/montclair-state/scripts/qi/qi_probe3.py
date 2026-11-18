import bpy, math
from mathutils import Vector
CW=bpy.data.objects['QE_CCIS_drape_cover_wall_east_UNVERIFIED']; M=CW.matrix_world
W=[M@v.co for v in CW.data.vertices]
print('CW nverts',len(W),'faces',len(CW.data.polygons),'mods',[m.type for m in CW.modifiers])
for p in CW.data.polygons[:12]:
    vv=[W[i] for i in p.vertices]; print('CWF',[tuple(round(c,1) for c in v) for v in vv])
xs=[v.x for v in W]; ys=[v.y for v in W]; print('CW bbox',min(xs),max(xs),min(ys),max(ys),min(v.z for v in W),max(v.z for v in W))
for o in bpy.data.objects:
    if 'Computing' in o.name or 'CCIS' in o.name:
        if o.type!='MESH' or o.hide_render: continue
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        print('OBJ',o.name,len(o.data.vertices),[round(min(v.x for v in bb),1),round(max(v.x for v in bb),1),round(min(v.y for v in bb),1),round(max(v.y for v in bb),1),round(min(v.z for v in bb),1),round(max(v.z for v in bb),1)])
