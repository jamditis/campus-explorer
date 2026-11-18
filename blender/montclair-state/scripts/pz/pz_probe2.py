import bpy, collections
from bpy_extras.object_utils import world_to_camera_view as w2c
from mathutils import Vector
sc=bpy.context.scene; sc.render.resolution_x=1024; sc.render.resolution_y=576
cam=bpy.data.objects['PY_CAM_closeup_dickson_wing_coping']; out=[]
def px(p):
    c=w2c(sc,cam,p); return (c.x*1024,(1-c.y)*576,c.z)
for on in ('Dickson Hall walls','PX_Dickson_wing_parapet_infill_UNVERIFIED','PY_Dickson_wing_parapet_raise_UNVERIFIED'):
    o=bpy.data.objects[on]; me=o.data; mw=o.matrix_world; WV=[mw@v.co for v in me.vertices]
    ec=collections.Counter()
    for p in me.polygons:
        for k in p.edge_keys: ec[k]+=1
    for k,c in ec.items():
        if c!=1: continue
        a=WV[k[0]]; b=WV[k[1]]
        if (a.xy-b.xy).length<0.02 and abs(a.z-b.z)>0.2 and max(a.z,b.z)>146:
            A=px(a); B=px(b)
            if 0<A[0]<1024 and 0<min(A[1],B[1])<576 and A[2]>0:
                out.append('%s %.2f %.2f z%.2f-%.2f -> px %.0f y%.0f-%.0f'%(on[:12],a.x,a.y,min(a.z,b.z),max(a.z,b.z),A[0],min(A[1],B[1]),max(A[1],B[1])))
o=bpy.data.objects['PY_Dickson_wing_parapet_coping_UNVERIFIED']
for v in o.data.vertices:
    c=o.matrix_world@v.co; P=px(c)
    if abs(P[0]-328)<40 and abs(P[1]-270)<30: out.append('COP %.3f %.3f %.3f -> %.0f %.0f'%(c.x,c.y,c.z,P[0],P[1]))
for p in [(-182,160,152.9),(-158.6,160,152.9),(-182,77,152.9)]: out.append('REF %s -> %s'%(p,px(Vector(p))))
open('data/pz/probe2.txt','w').write('\n'.join(out)); print('PROBE2',len(out))
