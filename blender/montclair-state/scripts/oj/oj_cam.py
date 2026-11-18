# oj cams (REVERT=1 removes): eye oblique from the +a (NNE) side of the pavilion, close-up of the +a side windows + landing pad.
import bpy, os, sys
from mathutils import Vector
CN='OJ_Schmitt_cams_20261031oj'; REV=os.environ.get('REVERT')=='1'
c=bpy.data.collections.get(CN)
if c:
    for o in list(c.objects): d=o.data; bpy.data.objects.remove(o); bpy.data.cameras.remove(d)
    if REV: bpy.data.collections.remove(c)
if not REV:
    if not c: c=bpy.data.collections.new(CN); bpy.context.scene.collection.children.link(c)
    fr=bpy.data.objects['OG_Schmitt_E_entrance_storefront_frame']; la=bpy.data.objects['OG_Schmitt_E_entrance_landing']
    fv=[fr.matrix_world@v.co for v in fr.data.vertices]; lb=[la.matrix_world@v.co for v in la.data.vertices]
    cen=sum(fv,Vector())/len(fv); lc=sum(lb,Vector())/len(lb); cen.z=0
    OUT=Vector(((lc-cen).x,(lc-cen).y,0)).normalized(); AL=Vector((-OUT.y,OUT.x,0))
    def P(a,o,z): return cen+AL*a+OUT*o+Vector((0,0,z))
    t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; mi=t.matrix_world.inverted()
    def gz(p):
        h,l,n,i=t.ray_cast(mi@Vector((p.x,p.y,400)),mi.to_3x3()@Vector((0,0,-1))); return (t.matrix_world@l).z
    def cam(name,a,o,z,ta,to,tz,lens):
        p=P(a,o,0); print(name,'terrain',round(gz(p),2),'cam z',z)
        d=bpy.data.cameras.new(name); d.lens=lens; d.clip_start=0.1; d.clip_end=3000
        ob=bpy.data.objects.new(name,d); c.objects.link(ob); ob.location=P(a,o,z)
        ob.rotation_euler=(P(ta,to,tz)-ob.location).to_track_quat('-Z','Y').to_euler()
    EA=float(os.environ.get('EA','22')); EO=float(os.environ.get('EO','15'))
    cam('OJ_CAM_eye_schmitt_pavilion_from_NNE',EA,EO,max(gz(P(EA,EO,0)),138.4)+1.65,1.5,-2,144.6,24)
    cam('OJ_CAM_eye_schmitt_pavilion_front_on_walk',-5.6,10.2,138.42+1.65,0,0,145.2,22)
    cam('OJ_CAM_closeup_schmitt_pavilion_side_windows_landing',8.0,7.0,140.6,2.2,-0.8,141.4,26)
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED')
