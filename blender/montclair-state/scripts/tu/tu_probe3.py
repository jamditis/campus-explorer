import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
for k in range(3):
    G=bpy.data.objects['TJ_Blanton_entrance_%d_glass_UNVERIFIED'%k]; F=bpy.data.objects['TJ_Blanton_entrance_%d_frame_UNVERIFIED'%k]
    gv=[G.matrix_world@v.co for v in G.data.vertices]; c=sum(gv,Vector())/len(gv)
    fv=[F.matrix_world@v.co for v in F.data.vertices]; fc=sum(fv,Vector())/len(fv)
    n=(fc-c); n.z=0; n.normalize()
    r=sc.ray_cast(dg,c+n*0.3,n,distance=60)
    gz=[]
    for d in (1,3,6,10):
        q=c+n*d; q.z=400; h=sc.ray_cast(dg,q,Vector((0,0,-1)))
        gz.append((d,round(h[1].z,2) if h[0] else None,h[4].name[:22] if h[0] else None))
    print('TUP3',k,[round(x,2) for x in c],'n',[round(x,2) for x in n],'out-hit',r[0] and (round((r[1]-c).length,1),r[4].name[:30]),gz)
