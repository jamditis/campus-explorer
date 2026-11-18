import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
import collections
cnt=collections.Counter(); ex=collections.defaultdict(list)
ok=('WS130_Chapin_E_service','WS130_stall_lines','WS108_Chapin_eave','WS122_Chapin_windows','WS108_Chapin_tile')
y=-232.0
while y<-220.9:
    x=-200.5
    while x<-194.9:
        o=Vector((x,y,135.5)); r=sc.ray_cast(dg,o,Vector((0,0,-1)))
        if r[0]:
            n=r[4].name
            cnt[n]+=1
            if not n.startswith(ok): ex[n].append((round(x,2),round(y,2),round(r[1].z,2)))
        x+=0.25
    y+=0.25
print('CNT',dict(cnt))
for n,L in ex.items(): print('EX',n,len(L),L[:12])
# wall S facade: horizontal rays northward at z 124 from y -236
for x in range(-216,-198,2):
    r=sc.ray_cast(dg,Vector((x,-236,123.6)),Vector((0,1,0)))
    print('WALL',x,r[0] and (r[4].name[:40],round(r[1].y,2)))
for x in (-214,-210,-206,-202):
  for yy in (-229.5,-230.5,-231.5):
    r=sc.ray_cast(dg,Vector((x,yy,135.5)),Vector((0,0,-1)))
    print('Z',x,yy,r[0] and (r[4].name[:30],round(r[1].z,3)))
