import bpy, os
from mathutils import Vector
sc=bpy.context.scene
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']
def gz(x,y):
    mi=T.matrix_world.inverted(); ok,l,n,i=T.ray_cast(mi@Vector((x,y,400)),(mi.to_3x3()@Vector((0,0,-1))).normalized())
    return (T.matrix_world@l).z if ok else 128.0
CAMS={}
def mk(n,loc,tgt,lens,eye,th):
    L=Vector((loc[0],loc[1],gz(loc[0],loc[1])+eye)); G=Vector((tgt[0],tgt[1],gz(tgt[0],tgt[1])+th))
    cd=bpy.data.cameras.new(n); cd.lens=lens; cd.clip_start=0.05; o=bpy.data.objects.new(n,cd); sc.collection.objects.link(o)
    o.location=L; o.rotation_euler=(G-L).to_track_quat('-Z','Y').to_euler(); bpy.context.view_layer.update(); CAMS[n]=o
mk('WS143_CAM_eye_forecourt_from_N_aisle',(-64.5,-160),(-73,-176),26,1.7,0.5)
mk('WS148_CAM_closeup_Lot9_E_edge',(-64.6,-193.5),(-68.6,-184.5),30,1.6,0.0)
def cast(camname,PX,nx=24,ny=12):
    cam=CAMS[camname]
    sc.render.resolution_x=768; sc.render.resolution_y=432
    dg=bpy.context.evaluated_depsgraph_get(); fr=cam.data.view_frame(scene=sc); mw=cam.matrix_world
    print("CAM",cam.name,tuple(round(x,2) for x in mw.translation))
    hits={}
    for iy in range(ny):
      for ix in range(nx):
        u=PX[0]+(PX[1]-PX[0])*ix/(nx-1); v=PX[2]+(PX[3]-PX[2])*iy/(ny-1)
        p=fr[1].lerp(fr[0],u); q=fr[2].lerp(fr[3],u); pt=p.lerp(q,v)
        dd=(mw@pt)-mw.translation
        ok,lp,n,fi,ob,_=sc.ray_cast(dg,mw.translation,dd.normalized())
        if ok:
            mat='?'
            try:
                oe=ob.evaluated_get(dg); mat=oe.material_slots[oe.data.polygons[fi].material_index].material.name
            except Exception: pass
            k=(ob.name,mat); h=hits.setdefault(k,[0,lp,(lp-mw.translation).length]); h[0]+=1
        else: hits.setdefault(('MISS',''),[0,None,0])[0]+=1
    for k,v in sorted(hits.items(),key=lambda kv:-kv[1][0]):
        print("HIT",camname[:20],v[0],k, tuple(round(x,2) for x in v[1]) if v[1] else '', round(v[2],2))
cast('WS143_CAM_eye_forecourt_from_N_aisle',(0.29,0.50,0.52,0.58))
cast('WS143_CAM_eye_forecourt_from_N_aisle',(0.08,0.30,0.58,0.62))
cast('WS148_CAM_closeup_Lot9_E_edge',(0.30,0.74,0.79,0.91))
