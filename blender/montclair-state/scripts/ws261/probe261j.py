# ws261: fine transects (1 cm) across the WS113 / Terrain boundary line E of the WS115 walk (after f261b x2): top object, z, normal z,
# and the 2nd hit, to find what draws the dark line still visible in the eye-from-N WIP.
import bpy, json
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws259/crop259.py').read())
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
B=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws261/bnd261g.json'))
out={}
for yc in (-217.0,-215.0,-213.0,-211.0,-209.0,-207.0):
    near=[p for p in B if abs(p[1]-yc)<0.08]
    if not near: continue
    xc=sum(p[0] for p in near)/len(near); row=[]
    for k in range(-40,41):
        x=xc+k*0.01; o0=Vector((x,yc,200)); hs=[]
        for s in range(60):
            r=sc.ray_cast(dg,o0,Vector((0,0,-1)))
            if not r[0]: break
            nm=r[4].name
            if not nm.startswith(('T_','TREE','MID_canopy')): hs.append((nm[:24],round(r[1].z,3),round(r[2].z,3)))
            if len(hs)>=2 or nm.startswith('Context_'): break
            o0=r[1]+Vector((0,0,-0.001))
        row.append((round(x,2),hs))
    out[str(yc)]=row
json.dump(out,open('/workspace/nj-scenes/montclair-state/scripts/ws261/eval261j.json','w'))
raise SystemExit
