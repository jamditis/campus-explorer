# ws261 probe (subset CHAIN, terrain GN on, crop259, exits before render): EVALUATED stack over the WS129b Chapin S-drive N walk
# + mulch strip + E-end apron. Per 0.25 m cell: if the walk/apron/strip is hit but something non-tree is above it by > 1 cm -> clip.
import bpy, json
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws259/crop259.py').read())
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
X0,X1,Y0,Y1,R=-234.5,-203.0,-246.0,-233.5,0.25
TGT=('WS129b_Chapin_S_drive_N','WS261_')
clip={}; n=0; holes=0
x=X0
while x<X1:
    y=Y0
    while y<Y1:
        o0=Vector((x,y,200)); hs=[]
        for k in range(60):
            r=sc.ray_cast(dg,o0,Vector((0,0,-1)))
            if not r[0]: break
            nm=r[4].name
            if nm.startswith('Context_'): hs.append((nm,r[1].z)); break
            if not nm.startswith(('T_','TREE','MID_canopy')): hs.append((nm,r[1].z))
            o0=r[1]+Vector((0,0,-0.001))
        ti=[i for i,h in enumerate(hs) if h[0].startswith(TGT)]
        if ti:
            n+=1; zt=hs[ti[0]][1]
            for h in hs[:ti[0]]:
                if h[1]>zt+0.01:
                    d=clip.setdefault(h[0][:60],[0,0,None]); d[0]+=1
                    if h[1]-zt>d[1]: d[1]=h[1]-zt; d[2]=(round(x,2),round(y,2))
        elif hs and hs[0][0].startswith('Context_'): holes+=1
        y+=R
    x+=R
print('P261B samples on target',n,'context-only cells',holes,flush=True)
for k,d in sorted(clip.items(),key=lambda kv:-kv[1][0]): print('P261B CLIP',k,'n',d[0],'max %.3f at'%d[1],d[2],flush=True)
json.dump(clip,open('/workspace/nj-scenes/montclair-state/scripts/ws261/eval261b.json','w'))
print('P261B done',flush=True)
raise SystemExit
