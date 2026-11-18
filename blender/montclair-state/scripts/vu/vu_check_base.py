import bpy, bmesh
from mathutils import Vector
BB=bpy.data.objects['TN_Blanton_block_base_UNVERIFIED']
bm=bmesh.new(); bm.from_mesh(BB.data); bm.faces.ensure_lookup_table(); mw=BB.matrix_world
for k in range(3):
    G=bpy.data.objects['TJ_Blanton_entrance_%d_glass_UNVERIFIED'%k]
    gv=[G.matrix_world@v.co for v in G.data.vertices]
    gc=sum(gv,Vector())/len(gv)
    best=None
    for i in range(len(gv)):
        for j in range(i+1,len(gv)):
            d=gv[j]-gv[i]; d.z=0
            if best is None or d.length>best.length: best=d
    u=best.normalized(); n=Vector((-u.y,u.x,0))
    BC=Vector((141.6,450.4,0))
    if (gc-BC).to_2d().dot(n.to_2d())<0: n=-n
    half_w=max(abs((v-gc).dot(u)) for v in gv)
    tops=[]
    for f in bm.faces:
        c=mw@f.calc_center_median(); d=c-gc
        nz=(mw.to_3x3()@f.normal).z
        if abs(d.dot(u))<half_w and abs(d.dot(n))<1.0 and nz>0.7:
            tops.append((round(d.dot(u),2), round(d.dot(n),2), round(c.z,2)))
    print('door',k,'top-facing faces in span', tops)
bm.free()
print('objs', len(bpy.data.objects))
