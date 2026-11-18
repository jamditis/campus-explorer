# ws82b: the two thin white streaks on the grandstand lawn = slivers of WS3_Concrete_panels_sawcut faces in the Terrain base mesh
# (an old footway line ~(-240,-124.7)->(-226,-115)); switch them to the WS82 lawn (grandstand unmodelled; no walk there per the 2020 ortho lawn).
import bpy
P=[(-264,-86),(-264,-95.5),(-230.3,-108.3),(-230.3,-127),(-229,-130.5),(-224,-131),(-221.5,-128),(-220.3,-120),(-219.8,-110),(-217.5,-108),(-216.5,-96),(-216.5,-86)]
def inside(x,y):
    c=False; n=len(P)
    for i in range(n):
        x1,y1=P[i]; x2,y2=P[(i+1)%n]
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1)+x1: c=not c
    return c
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=T.data; names=[m.name if m else None for m in me.materials]
mi=names.index('WS82_Lawn_grandstand_no_ortho_UNVERIFIED'); ci=names.index('WS3_Concrete_panels_sawcut'); mw=T.matrix_world; n=0; ex=[]
for p in me.polygons:
    if p.material_index!=ci: continue
    c=mw@p.center
    if -252<=c.x<=-224 and -140<=c.y<=-104 and not inside(c.x,c.y):
        p.material_index=mi; n+=1
        if len(ex)<6: ex.append((round(c.x,1),round(c.y,1)))
print('WS82b concrete->lawn',n,ex,flush=True)
dg=bpy.context.evaluated_depsgraph_get(); te=T.evaluated_get(dg); em=te.to_mesh(); en=[m.name if m else None for m in em.materials]; h={}
for p in em.polygons:
    c=mw@p.center
    if -240<c.x<-226 and -126<c.y<-110: k=en[p.material_index]; h[k]=h.get(k,0)+1
print('WS82b eval after',h,flush=True); te.to_mesh_clear()
bpy.ops.wm.save_mainfile(); print('WS82b SAVED',flush=True)
