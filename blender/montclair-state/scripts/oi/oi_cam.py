# oi cams (REVERT=1 removes). Frontal pavilion eye view (cf. schmitt_03/01), wing oblique eye view, arch/lettering close-up.
import bpy, os, sys
from mathutils import Vector
CN='OI_Schmitt_cams_20261031oi'; REV=os.environ.get('REVERT')=='1'
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
    dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
    def gz(p):
        t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; mi=t.matrix_world.inverted()
        h,l,n,i=t.ray_cast(mi@Vector((p.x,p.y,400)),mi.to_3x3()@Vector((0,0,-1))); return (t.matrix_world@l).z,'terrain'
    def cam(name,a,o,dz,ta,to,tz,lens):
        p=P(a,o,0); z,on=gz(p); print(name,'ground',round(z,2),on)
        d=bpy.data.cameras.new(name); d.lens=lens; d.clip_start=0.1; d.clip_end=3000
        ob=bpy.data.objects.new(name,d); c.objects.link(ob); ob.location=(p.x,p.y,z+dz)
        ob.rotation_euler=(P(ta,to,tz)-ob.location).to_track_quat('-Z','Y').to_euler()
    A=float(os.environ.get('FA','0')); O=float(os.environ.get('FO','26'))
    cam('OI_CAM_eye_schmitt_pavilion_front',A,O,1.65,0,0,145.0,24)
    cam('OI_CAM_eye_schmitt_pavilion_wing_oblique',float(os.environ.get('WA','-26')),float(os.environ.get('WO','16')),1.65,-1,-3,144.2,24)
    cam('OI_CAM_closeup_schmitt_arch_lettering',2.0,10.5,1.65,0,0.3,144.6,30)
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED')
