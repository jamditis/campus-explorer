import bpy
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
names={}
rows=[]
for y in range(126,100,-1):
    r=''
    for x in range(12,50):
        hit,loc,n,i,ob,m=sc.ray_cast(dg,Vector((x+.5,y+.5,160)),Vector((0,0,-1)))
        if not hit: r+=' '; continue
        k=names.setdefault(ob.name,chr(65+len(names)) if len(names)<26 else '?')
        r+=k if loc.z>130 else k.lower()
    rows.append(f'{y:4d} {r}')
print('\n'.join('ROW'+s for s in rows))
for k,v in names.items(): print('KEY',v,k)
