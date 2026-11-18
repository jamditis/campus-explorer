import bpy, mathutils
V=mathutils.Vector; col=bpy.data.collections['OE_CCOM_atrium_stair_wall_wood_panelling_20261031oe']
nm='OE_CAM_closeup_atrium_stair_wall_panels_handrail'
if nm in bpy.data.objects: bpy.data.objects.remove(bpy.data.objects[nm])
c=bpy.data.cameras.new(nm); c.lens=26; c.clip_start=0.05; o=bpy.data.objects.new(nm,c); o.location=(-15.6,14.3,139.75)
o.rotation_euler=(V((-12.6,16.5,140.7))-o.location).to_track_quat('-Z','Y').to_euler(); col.objects.link(o)
o['msu_tag_session']='oe'; o['msu_layer']='camera'
bpy.ops.wm.save_mainfile(); print('OE_CAM_SAVED',len(bpy.data.objects))
