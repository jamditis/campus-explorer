# ng camera aims (track-to targets); exec'd by ng_build.py, or run standalone with SAVE=1
import bpy, mathutils, os
AIM={'NG_CAM_aerial_cutaway':((-8,-24,172),(-3,8,139),22),
     'NG_CAM_eye_balcony_down':((7.6,7.6,143.5),(11.2,12.0,137.7),16)}
for n,(loc,tgt,lens) in AIM.items():
    o=bpy.data.objects[n]; o.location=loc; o.data.lens=lens
    o.rotation_euler=(mathutils.Vector(tgt)-mathutils.Vector(loc)).to_track_quat('-Z','Y').to_euler()
if __name__=='__main__' and os.environ.get('SAVE')=='1' and 'NG_CCOM_1F_open_floor_20261030ng' in bpy.data.collections:
    bpy.ops.wm.save_mainfile(); print('SAVED_CAMS')
