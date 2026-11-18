import bpy
from mathutils import Vector
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws166/hdr166.py').read())
bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
for (x,y) in [(-295.4,-272.1),(-299.3,-277.5),(-298.4,-279.9),(-290.5,-294.3),(-296.15,-269.85),(-317,-270),(-330,-268),(-310,-280),(-280,-276)]:
    hit,loc,nor,idx,ob,_=sc.ray_cast(dg,Vector((x,y,170)),Vector((0,0,-1)))
    if hit and 'tree' in ob.name.lower(): hit,loc,nor,idx,ob,_=sc.ray_cast(dg,Vector((x,y,loc.z-0.01)),Vector((0,0,-1)))
    print('PROBE171e',x,y,ob.name[:45] if hit else None,round(loc.z-dz(x,y),2) if hit else None,flush=True)
