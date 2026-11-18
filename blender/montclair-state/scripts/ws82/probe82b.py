import bpy
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']
for o in bpy.data.objects:
    if o.type!='MESH': continue
    mw=o.matrix_world; n=0; ex=[]
    for p in o.data.polygons:
        c=mw@p.center
        if -252<c.x<-222 and -135<c.y<-108 and not (c.x>-230.3 and c.y<-106):
            n+=1
            if len(ex)<3: ex.append((round(c.x,1),round(c.y,1),round(c.z,2)))
    if n: print('OBJ',o.name[:50],n,ex,flush=True)
# camera ray scan along the streak row in the lane-from-S view
def gz(x,y):
    ok,loc,*_=sc.ray_cast(dg,Vector((x,y,400)),Vector((0,0,-1))); return loc.z if ok else 125
c=bpy.data.cameras.new('p'); c.lens=28; o=bpy.data.objects.new('p',c); sc.collection.objects.link(o)
E=Vector((-227,-134,gz(-227,-134)+1.7)); Tt=Vector((-229,-96,gz(-229,-96)+0.5)); o.location=E; o.rotation_euler=(Tt-E).to_track_quat('-Z','Y').to_euler()
sc.render.resolution_x=640; sc.render.resolution_y=360; bpy.context.view_layer.update()
TR,BR,BL,TL=[o.matrix_world@v for v in c.view_frame(scene=sc)]
for px in (100,):
    for py in range(190,240,1):
        u=px/640; v=py/360; p=(TL.lerp(TR,u)).lerp(BL.lerp(BR,u),v); d=(p-E).normalized()
        ok,loc,nrm,i,ob,m=sc.ray_cast(dg,E,d)
        if ok:
            try: mat=ob.material_slots[ob.data.polygons[i].material_index].material.name
            except Exception: mat=None
            print('RAY',py,ob.name[:30],i,mat,tuple(round(x,2) for x in loc),round(nrm.z,3))
