import bpy
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
s=bpy.data.objects['WS72b_Kasser_S_sidewalk_east_to_Cole_UNVERIFIED_width']
xs=sorted(set(round(v.co.x,2) for v in s.data.vertices)); bad=[];c=0
for x in xs:
    ys=[v.co.y for v in s.data.vertices if abs(v.co.x-x)<0.01]
    for k in range(0,21):
        y=min(ys)+(max(ys)-min(ys))*k/20
        r=sc.ray_cast(dg,Vector((x,y,400)),Vector((0,0,-1))); c+=1
        if r[0] and r[4].name!=s.name and 'Kasser' not in r[4].name: bad.append((x,round(y,2),r[4].name[:25],round(r[1].z,2)))
print('P7 nonslab hits',len(bad),'/',c, bad[:20])
