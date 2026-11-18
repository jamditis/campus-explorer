import bpy,json
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
S=json.load(open('data/tu/door_probe.json'))
for d in S:
    c=Vector(d['c']); u=Vector(d['u']); n=Vector(d['n'])
    F=bpy.data.objects['TJ_Blanton_entrance_%d_frame_UNVERIFIED'%d['k']]
    fv=[F.matrix_world@v.co for v in F.data.vertices]; fc=sum(fv,Vector())/len(fv)
    if (fc-c).dot(n)<0: n=-n
    nc=c+u*(d['shift'] or 0)
    out=[]
    for su in (-2.8,-2,-1,0,1,2,2.8):
        o=nc+u*su+n*3+Vector((0,0,0.3))
        r=sc.ray_cast(dg,o,-n)
        out.append((su,round(3-r[1].distance if False else 3-(r[1]-o).length,3) if r[0] else None, r[4].name[:28] if r[0] else None))
    print('TUP',d['k'],out)
