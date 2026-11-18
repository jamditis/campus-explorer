# oh cams (REVERT=1 removes). blender -b montclair_state.blend --python scripts/oh/oh_cam.py -- --save
import bpy, os, sys
from mathutils import Vector
CN='OH_Schmitt_cams_20261031oh'
REV=os.environ.get('REVERT')=='1'
c=bpy.data.collections.get(CN)
if c:
    for o in list(c.objects): bpy.data.objects.remove(o)
    if REV: bpy.data.collections.remove(c)
if not REV:
    if not c: c=bpy.data.collections.new(CN); bpy.context.scene.collection.children.link(c)
    dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
    def gz(x,y):
        hit,loc,n,i,ob,m=sc.ray_cast(dg,Vector((x,y,400)),Vector((0,0,-1)))
        return loc.z, ob.name if ob else None
    def cam(name,x,y,dz,tx,ty,tz,lens):
        z,on=gz(x,y); print(name,'ground',round(z,2),on)
        d=bpy.data.cameras.new(name); d.lens=lens; d.clip_start=0.1; d.clip_end=3000
        o=bpy.data.objects.new(name,d); c.objects.link(o); o.location=(x,y,z+dz)
        o.rotation_euler=(Vector((tx,ty,tz))-o.location).to_track_quat('-Z','Y').to_euler()
    cam('OH_CAM_eye_schmitt_SSW_end',float(os.environ.get('SX','-12')),float(os.environ.get('SY','92')),1.65,-2,125,143,30)
    cam('OH_CAM_closeup_schmitt_ESE_base_red_frames',19.5,132.0,1.6,9.0,140.0,140.2,35)
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED')
