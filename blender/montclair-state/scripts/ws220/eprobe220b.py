import bpy, os, json
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
X0,X1,Y0,Y1,ST=[float(v) for v in os.environ['PG'].split(',')]
out=[]
y=Y1
while y>=Y0-1e-6:
    x=X0
    while x<=X1+1e-6:
        o=Vector((x,y,170)); hs=[]
        for k in range(3):
            r=sc.ray_cast(dg,o,Vector((0,0,-1)))
            if not r[0]: break
            hs.append((r[4].name,round(r[1].z,3))); o=Vector((x,y,r[1].z-0.002))
        out.append((x,y,hs)); x+=ST
    y-=ST
json.dump(out,open('/tmp/eprobe220b.json','w')); print('HITE done',len(out),flush=True)
raise SystemExit
