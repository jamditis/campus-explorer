import bpy, mathutils
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
# roof height just inside facade; terrain just outside
for x,y,dy in [(-205,167.5,1),(-215,168,1),(-230,177,1),(-245,177,1),(-197,170,1),(-256,186,1),(-225,200,0),(-210,200,0),(-240,195,0)]:
    h,loc,n,i,ob,m=sc.ray_cast(dg,(x,y+dy,180),(0,0,-1)); print('R',x,y+dy,ob.name[:30] if h else None,round(loc.z,2) if h else None)
w=bpy.data.objects['Feliciano School of Business walls']
me=w.data; import collections
zs=collections.Counter(round((w.matrix_world@v.co).z,1) for v in me.vertices); print('WALLZ',sorted(zs.items())[:40])
