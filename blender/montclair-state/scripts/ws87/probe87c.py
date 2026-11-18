import bpy
from mathutils import Vector
print('P87 mats',[m.name for m in bpy.data.materials if 'ulch' in m.name or 'ark_soil' in m.name.lower()][:20])
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
for x in [-182,-180,-178,-176,-174]:
    for y in [-94,-90,-86,-82,-78]:
        ok,loc,n,i,o,_=sc.ray_cast(dg,Vector((x,y,131.6)),Vector((0,0,-1)))
        print('P87',x,y,round(loc.z,2) if ok else None,o.name[:40] if ok else '')
w=bpy.data.objects['Plaza long arched wall (LiDAR line/top MEASURED; arches UNVERIFIED)'] if 'Plaza long arched wall (LiDAR line/top MEASURED; arches UNVERIFIED)' in bpy.data.objects else [o for o in bpy.data.objects if o.name.startswith('Plaza long arched wall')][0]
vs=[w.matrix_world@v.co for v in w.data.vertices if (w.matrix_world@v.co).z<129.8]
import math
print('P87 wallbase n',len(vs)); 
for v in vs[::max(1,len(vs)//25)]: print('P87 wb',round(v.x,2),round(v.y,2),round(v.z,2))
s=bpy.data.objects['WS35_Kasser_terrace_steps_concrete_5risers_UNVERIFIED']
print('P87 steps verts sample',[tuple(round(c,1) for c in (s.matrix_world@v.co)) for v in s.data.vertices[::30]])
