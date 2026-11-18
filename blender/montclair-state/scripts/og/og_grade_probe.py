import bpy, math
from mathutils import Vector
sc=bpy.context.scene; DG=bpy.context.evaluated_depsgraph_get()
wo=bpy.data.objects['Schmitt Hall walls']; me=wo.data; mw=wo.matrix_world
C=Vector((-3.4,153.4,0))
def rc(o,d,dist=1e4):
    t=0.0; hits=[]
    while t<dist:
        h,l,nn,i,ob,_=sc.ray_cast(DG,o+d*t,d,distance=dist-t)
        if not h: break
        hits.append((round(l.z,2),ob.name[:40])); t+=(l-(o+d*t)).length+0.02
        if len(hits)>6: break
    return hits
bot=[mw@v.co for v in me.vertices if (mw@v.co).z<138.5]
print('bottom verts',len(bot))
seen=0
for p in bot[::3]:
    q=p+(Vector((p.x,p.y,0))-C).normalized()*1.2
    hs=rc(Vector((q.x,q.y,160)),Vector((0,0,-1)),40)
    hs=[h for h in hs if not h[1].startswith('T_') and 'Schmitt' not in h[1]]
    print(round(p.x,1),round(p.y,1),'wallbot',round(p.z,2),hs[:3]); seen+=1
    if seen>40: break
