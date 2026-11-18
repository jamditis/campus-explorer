import bpy,os
from mathutils import Vector
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws32/fix.py').read())
dg=bpy.context.evaluated_depsgraph_get(); dg.update(); sc=bpy.context.scene
D=Vector((0,0,-1))
print('EAST profile')
for y in (-36,-32,-28,-24):
    s=[]
    for x in (12,13,14,15,15.5,16,16.5,17,18,19,20,22):
        r=sc.ray_cast(dg,Vector((x,y,200)),D); s.append(f"{x}:{r[4].name[:10]}@{r[1].z:.2f}" if r[0] else f"{x}:-")
    print(y,' '.join(s))
print('SEAM grid (names: A apron F foot O OZ joints P PA chips R roads C curb L lawn T terrain)')
for y10 in range(-380,-230,5):
    s=''
    for x10 in range(-20,90,3):
        r=sc.ray_cast(dg,Vector((x10/10,y10/10,200)),D)
        n=r[4].name if r[0] else '-'
        s+= {'CCOM_dock_':'A','Footpaths_':'F','OZ_walk_jo':'O','PA_walk_pa':'P','Roads_OSM':'R','Curbs_gran':'C','Lawn_worn_':'L','Terrain_Li':'T'}.get(n[:10],'?')
    print(f'{y10/10:6.1f} {s}')
