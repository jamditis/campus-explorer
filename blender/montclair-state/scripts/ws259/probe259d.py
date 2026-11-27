# ws259 probe (subset CHAIN, exits before render): WS103 walk W/E edge vs whatever ground is beside it (evaluated, terrain GN on)
import bpy, numpy as np
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws259/crop259.py').read())
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
w=[o for o in sc.objects if o.name.startswith('WS103_CollegeAve_S_W_sidewalk')][0]
V=np.array([tuple(w.matrix_world@v.co) for v in w.data.vertices])
def top(x,y,skip=()):
    o0=Vector((x,y,200))
    for k in range(6):
        r=sc.ray_cast(dg,o0,Vector((0,0,-1)))
        if not r[0]: return None,None
        if not r[4].name.startswith(skip) and not r[4].name.startswith(('WS259_','T_','TREE')): return r[4].name,r[1].z
        o0=r[1]+Vector((0,0,-0.0005))
    return None,None
for y in np.arange(-238,-158,4.0):
    s=V[np.abs(V[:,1]-y)<0.3]
    if len(s)==0: continue
    xw,xe=s[:,0].min(),s[:,0].max()
    _,zw=top(xw+0.1,y); _,ze=top(xe-0.1,y)
    nW,gW=top(xw-0.35,y,('WS103',)); nE,gE=top(xe+0.35,y,('WS103',))
    print('P259D y %.0f W edge %.2f z %.3f | beside %s %.3f dz %+.2f || E edge %.2f z %.3f | beside %s %.3f dz %+.2f'%(y,xw,zw or 0,(nW or '-')[:30],gW or 0,(gW or 0)-(zw or 0),xe,ze or 0,(nE or '-')[:30],gE or 0,(gE or 0)-(ze or 0)),flush=True)
raise SystemExit
