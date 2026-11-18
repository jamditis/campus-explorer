import bpy
from mathutils import Vector
F=bpy.data.objects['Footpaths_OSM']; dg=bpy.context.evaluated_depsgraph_get(); FE=F.evaluated_get(dg); FI=F.matrix_world.inverted()
B=[(121,141,201,218),(118,145,183,201),(108,121,201,250),(-134,-102,193,228)]
rows=[]
for y in range(140,252,4):
    s=''
    for x in range(60,180,4):
        ok,loc,n,i=FE.ray_cast(FI@Vector((x,y,300)),Vector((0,0,-1)))
        inb=any(a<=x<=b and c<=y<=d for a,b,c,d in B)
        s+=('B' if inb else '#') if ok else '.'
    rows.append('%4d %s'%(y,s))
print('\n'.join(reversed(rows)))
print('Fmw',F.matrix_world.translation[:])
