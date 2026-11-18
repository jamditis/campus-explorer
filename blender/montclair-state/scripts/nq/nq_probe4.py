import bpy,time
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
for x,y in ((-6.27,-9.9),(-6.6,-4.9),(-3.5,-12.1),(-8,-7),(-2,-8)):
    t=time.time(); h,l,n,i,ob,m=sc.ray_cast(dg,(x,y,149.0),(0,0,-1)); 
    print('P4',x,y,h and round(l.z,2),ob and ob.name,[s.material.name for s in ob.material_slots if s.material][:3] if ob else None,round(time.time()-t,2))
