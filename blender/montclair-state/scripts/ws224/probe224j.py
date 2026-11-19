import bpy
n=0
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render or not o.data.polygons: continue
    R=o.matrix_world.to_3x3()
    a=[(R@p.normal).z*p.area for p in o.data.polygons]
    dn=-sum(x for x in a if x<-0.3*0); up=sum(x for x in a if x>0)
    if dn>2*up and dn>0.2:
        n+=1; print('P224 INV %-70s down %.1f up %.1f nf %d'%(o.name[:70],dn,up,len(a)))
print('P224 inverted-looking objects',n)
