import bpy,os
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get(); cam=bpy.data.objects[os.environ.get('CAM','WA2_CAM_eye_richardson_west_walk_from_W')]
fr=[cam.matrix_world@v for v in cam.data.view_frame(scene=sc)]
P=cam.matrix_world.translation; W,H=1024,576
def ray(px,py):
    u=px/W; v=py/H
    top=fr[3].lerp(fr[0],u); bot=fr[2].lerp(fr[1],u); t=top.lerp(bot,v); return (t-P).normalized()
for px in range(10,340,30):
    prev=None; out=[]
    for py in range(380,576,2):
        h=sc.ray_cast(dg,P,ray(px,py))
        n=h[4].name[:22] if h[0] else 'NONE'
        if n!=prev: out.append((py,n,tuple(round(c,2) for c in h[1]) if h[0] else '',tuple(round(c,2) for c in h[2]) if h[0] else ''))
        prev=n
    print('COL',px,out,flush=True)
